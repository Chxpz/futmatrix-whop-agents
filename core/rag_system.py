"""
RAG (Retrieval-Augmented Generation) system implementation.
"""
import logging
from typing import Dict, Any, List, Optional
import hashlib
from datetime import datetime

from utils.exceptions import RAGError

class RAGSystem:
    """RAG system with database and MCP integration."""
    
    def __init__(self, database_manager, mcp_client):
        self.database = database_manager
        self.mcp_client = mcp_client
        self.logger = logging.getLogger("rag_system")
        
    async def initialize(self) -> None:
        """Initialize RAG system."""
        try:
            # Check if RAG documents table exists and has data
            documents = await self.database.search_rag_documents("", limit=1)
            
            if not documents:
                self.logger.info("No RAG documents found, system ready for document ingestion")
            else:
                self.logger.info(f"RAG system initialized with existing documents")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            raise RAGError(f"RAG system initialization failed: {e}")
    
    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> str:
        """Add document to RAG knowledge base."""
        try:
            if not document_id:
                # Generate document ID from content hash
                document_id = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            if not metadata:
                metadata = {}
            
            # Add timestamp to metadata
            metadata.update({
                "added_at": datetime.utcnow().isoformat(),
                "content_length": len(content)
            })
            
            # Generate embeddings if MCP provides embedding tools
            embeddings = await self._generate_embeddings(content)
            
            # Save to database
            await self.database.save_rag_document(
                document_id=document_id,
                content=content,
                metadata=metadata,
                embeddings=embeddings
            )
            
            self.logger.info(f"Added document {document_id} to RAG knowledge base")
            return document_id
            
        except Exception as e:
            self.logger.error(f"Error adding document to RAG: {e}")
            raise RAGError(f"Failed to add document to RAG: {e}")
    
    async def query(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query RAG system for relevant documents."""
        try:
            # Try MCP RAG tools first
            mcp_results = await self.mcp_client.query_rag(query, top_k)
            
            if mcp_results:
                self.logger.debug(f"Retrieved {len(mcp_results)} results from MCP RAG")
                return mcp_results
            
            # Fallback to database search
            db_results = await self.database.search_rag_documents(
                query=query,
                limit=top_k,
                metadata_filter=metadata_filter
            )
            
            # Format results
            formatted_results = []
            for doc in db_results:
                formatted_results.append({
                    "document_id": doc.get("document_id"),
                    "content": doc.get("content"),
                    "metadata": doc.get("metadata", {}),
                    "relevance_score": self._calculate_relevance_score(query, doc.get("content", ""))
                })
            
            # Sort by relevance score
            formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            self.logger.debug(f"Retrieved {len(formatted_results)} results from database RAG")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error querying RAG system: {e}")
            raise RAGError(f"Failed to query RAG system: {e}")
    
    async def _generate_embeddings(self, text: str) -> Optional[List[float]]:
        """Generate embeddings for text using MCP tools."""
        try:
            # Look for embedding tools in MCP
            tools = await self.mcp_client.list_tools()
            embedding_tools = [t for t in tools if "embed" in t.get("name", "").lower()]
            
            if not embedding_tools:
                self.logger.debug("No embedding tools available via MCP")
                return None
            
            # Use first available embedding tool
            embedding_tool = embedding_tools[0]
            
            result = await self.mcp_client.call_tool(
                embedding_tool["name"],
                {"text": text},
                embedding_tool["server_url"]
            )
            
            embeddings = result.get("embeddings", [])
            
            if embeddings:
                self.logger.debug("Generated embeddings via MCP")
                return embeddings
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to generate embeddings via MCP: {e}")
            return None
    
    def _calculate_relevance_score(self, query: str, content: str) -> float:
        """Calculate simple relevance score between query and content."""
        try:
            # Simple keyword-based relevance scoring
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            
            if not query_words:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(query_words.intersection(content_words))
            union = len(query_words.union(content_words))
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception as e:
            self.logger.warning(f"Error calculating relevance score: {e}")
            return 0.0
    
    async def get_document_count(self) -> int:
        """Get total number of documents in RAG knowledge base."""
        try:
            # This is a simple implementation - in production you'd have a proper count query
            documents = await self.database.search_rag_documents("", limit=1000)
            return len(documents)
            
        except Exception as e:
            self.logger.error(f"Error getting document count: {e}")
            return 0
    
    async def remove_document(self, document_id: str) -> bool:
        """Remove document from RAG knowledge base."""
        try:
            # This would require implementing delete functionality in database manager
            self.logger.warning("Document removal not implemented in current version")
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing document: {e}")
            return False
