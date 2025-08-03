"""
Vector database integration for RAG (Retrieval-Augmented Generation).
Uses pgvector extension for PostgreSQL to store and search document embeddings.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import json
from datetime import datetime

import asyncpg
import numpy as np
from openai import AsyncOpenAI
from utils.exceptions import RAGError
from config.settings import Settings


class VectorDatabase:
    """PostgreSQL + pgvector implementation for document embeddings."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("vector_db")
        self.connection_pool = None
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Embedding configuration
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        self.similarity_threshold = 0.7
    
    async def initialize(self) -> None:
        """Initialize vector database connection and create tables."""
        try:
            # Create connection pool
            db_url = self.settings.DATABASE_CONFIG["url"]
            self.connection_pool = await asyncpg.create_pool(
                dsn=db_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            # Create vector extension and tables
            await self._setup_vector_tables()
            
            self.logger.info("Vector database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Vector database initialization failed: {e}")
            raise RAGError(f"Vector database initialization failed: {e}")
    
    async def _setup_vector_tables(self) -> None:
        """Setup pgvector extension and create necessary tables."""
        async with self.connection_pool.acquire() as conn:
            # Enable pgvector extension
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                self.logger.info("pgvector extension enabled")
            except Exception as e:
                self.logger.warning(f"Could not enable pgvector extension: {e}")
                # Continue without vector extension for development
            
            # Create documents table with vector embeddings
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS public.rag_documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_hash TEXT UNIQUE NOT NULL,
                    category TEXT,
                    source TEXT,
                    metadata JSONB DEFAULT '{}',
                    agent_types TEXT[] DEFAULT '{}',
                    embedding vector(1536),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Create indexes for performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rag_documents_category 
                ON public.rag_documents(category)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rag_documents_agent_types 
                ON public.rag_documents USING GIN(agent_types)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rag_documents_content_hash 
                ON public.rag_documents(content_hash)
            """)
            
            # Create vector similarity index if pgvector is available
            try:
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_rag_documents_embedding 
                    ON public.rag_documents USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """)
                self.logger.info("Vector similarity index created")
            except Exception as e:
                self.logger.info("Vector index not created (pgvector might not be available)")
            
            self.logger.info("Vector database tables setup complete")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            # Clean and prepare text
            cleaned_text = text.strip().replace("\n", " ")[:8000]  # Limit text length
            
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=cleaned_text
            )
            
            embedding = response.data[0].embedding
            self.logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            raise RAGError(f"Embedding generation failed: {e}")
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash for content deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def add_document(self, 
                          title: str, 
                          content: str, 
                          category: Optional[str] = None,
                          source: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          agent_types: Optional[List[str]] = None) -> str:
        """Add document to vector database with embedding."""
        try:
            # Calculate content hash for deduplication
            content_hash = self._calculate_content_hash(content)
            
            # Check if document already exists
            async with self.connection_pool.acquire() as conn:
                existing = await conn.fetchval(
                    "SELECT id FROM public.rag_documents WHERE content_hash = $1",
                    content_hash
                )
                
                if existing:
                    self.logger.info(f"Document already exists with hash {content_hash}")
                    return str(existing)
            
            # Generate embedding
            embedding = await self.generate_embedding(content)
            
            # Store document
            async with self.connection_pool.acquire() as conn:
                document_id = await conn.fetchval("""
                    INSERT INTO public.rag_documents 
                    (title, content, content_hash, category, source, metadata, agent_types, embedding)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id
                """, 
                title, 
                content, 
                content_hash, 
                category, 
                source, 
                metadata or {}, 
                agent_types or [],
                embedding
                )
                
                self.logger.info(f"Added document: {title} (ID: {document_id})")
                return str(document_id)
                
        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")
            raise RAGError(f"Failed to add document: {e}")
    
    async def search_documents(self, 
                              query: str, 
                              agent_type: Optional[str] = None,
                              category: Optional[str] = None,
                              limit: int = 5,
                              similarity_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search documents using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            threshold = similarity_threshold or self.similarity_threshold
            
            # Build search query
            conditions = []
            params = [query_embedding, limit]
            param_count = 2
            
            if agent_type:
                param_count += 1
                conditions.append(f"${param_count} = ANY(agent_types)")
                params.append(agent_type)
            
            if category:
                param_count += 1
                conditions.append(f"category = ${param_count}")
                params.append(category)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # Search with vector similarity
            search_query = f"""
                SELECT 
                    id,
                    title,
                    content,
                    category,
                    source,
                    metadata,
                    agent_types,
                    1 - (embedding <=> $1) as similarity,
                    created_at
                FROM public.rag_documents
                {where_clause}
                ORDER BY embedding <=> $1
                LIMIT $2
            """
            
            async with self.connection_pool.acquire() as conn:
                try:
                    results = await conn.fetch(search_query, *params)
                except Exception as vector_error:
                    # Fallback to text search if vector search fails
                    self.logger.warning(f"Vector search failed, using text search: {vector_error}")
                    return await self._fallback_text_search(query, agent_type, category, limit)
                
                documents = []
                for row in results:
                    similarity = float(row['similarity'])
                    
                    # Filter by similarity threshold
                    if similarity >= threshold:
                        documents.append({
                            "id": str(row['id']),
                            "title": row['title'],
                            "content": row['content'],
                            "category": row['category'],
                            "source": row['source'],
                            "metadata": row['metadata'],
                            "agent_types": row['agent_types'],
                            "similarity": similarity,
                            "created_at": row['created_at'].isoformat()
                        })
                
                self.logger.info(f"Found {len(documents)} documents for query: {query[:50]}...")
                return documents
                
        except Exception as e:
            self.logger.error(f"Document search failed: {e}")
            # Fallback to text search
            return await self._fallback_text_search(query, agent_type, category, limit)
    
    async def _fallback_text_search(self, 
                                   query: str, 
                                   agent_type: Optional[str] = None,
                                   category: Optional[str] = None,
                                   limit: int = 5) -> List[Dict[str, Any]]:
        """Fallback text-based search when vector search is unavailable."""
        try:
            conditions = ["(title ILIKE $1 OR content ILIKE $1)"]
            params = [f"%{query}%", limit]
            param_count = 2
            
            if agent_type:
                param_count += 1
                conditions.append(f"${param_count} = ANY(agent_types)")
                params.append(agent_type)
            
            if category:
                param_count += 1
                conditions.append(f"category = ${param_count}")
                params.append(category)
            
            where_clause = "WHERE " + " AND ".join(conditions)
            
            search_query = f"""
                SELECT 
                    id, title, content, category, source, metadata, agent_types, created_at
                FROM public.rag_documents
                {where_clause}
                ORDER BY 
                    CASE WHEN title ILIKE $1 THEN 1 ELSE 2 END,
                    created_at DESC
                LIMIT ${param_count + 1}
            """
            
            params.append(limit)
            
            async with self.connection_pool.acquire() as conn:
                results = await conn.fetch(search_query, *params)
                
                documents = []
                for row in results:
                    documents.append({
                        "id": str(row['id']),
                        "title": row['title'],
                        "content": row['content'],
                        "category": row['category'],
                        "source": row['source'],
                        "metadata": row['metadata'],
                        "agent_types": row['agent_types'],
                        "similarity": 0.8,  # Default similarity for text search
                        "created_at": row['created_at'].isoformat()
                    })
                
                self.logger.info(f"Fallback search found {len(documents)} documents")
                return documents
                
        except Exception as e:
            self.logger.error(f"Fallback text search failed: {e}")
            return []
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            async with self.connection_pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT * FROM public.rag_documents WHERE id = $1",
                    document_id
                )
                
                if result:
                    return {
                        "id": str(result['id']),
                        "title": result['title'],
                        "content": result['content'],
                        "category": result['category'],
                        "source": result['source'],
                        "metadata": result['metadata'],
                        "agent_types": result['agent_types'],
                        "created_at": result['created_at'].isoformat()
                    }
                
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document by ID."""
        try:
            async with self.connection_pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM public.rag_documents WHERE id = $1",
                    document_id
                )
                
                deleted = result.split()[-1] == "1"
                if deleted:
                    self.logger.info(f"Deleted document: {document_id}")
                
                return deleted
                
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            async with self.connection_pool.acquire() as conn:
                # Total documents
                total_docs = await conn.fetchval(
                    "SELECT COUNT(*) FROM public.rag_documents"
                )
                
                # Documents by category
                categories = await conn.fetch("""
                    SELECT category, COUNT(*) as count 
                    FROM public.rag_documents 
                    WHERE category IS NOT NULL
                    GROUP BY category
                    ORDER BY count DESC
                """)
                
                # Documents by agent type
                agent_types = await conn.fetch("""
                    SELECT unnest(agent_types) as agent_type, COUNT(*) as count
                    FROM public.rag_documents
                    WHERE agent_types != '{}'
                    GROUP BY agent_type
                    ORDER BY count DESC
                """)
                
                return {
                    "total_documents": total_docs,
                    "categories": [{"category": row['category'], "count": row['count']} for row in categories],
                    "agent_types": [{"agent_type": row['agent_type'], "count": row['count']} for row in agent_types],
                    "embedding_model": self.embedding_model,
                    "embedding_dimension": self.embedding_dimension,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def close(self) -> None:
        """Close database connections."""
        try:
            if self.connection_pool:
                await self.connection_pool.close()
                self.logger.info("Vector database connections closed")
                
        except Exception as e:
            self.logger.error(f"Error closing vector database: {e}")