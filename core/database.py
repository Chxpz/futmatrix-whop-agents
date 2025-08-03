"""
Supabase database integration for AI agents.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from supabase import create_client, Client
from postgrest.exceptions import APIError

from models.schemas import UserInteraction, AgentResponse
from utils.exceptions import DatabaseError
import os

class DatabaseManager:
    """Supabase database manager for agent data persistence."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("database")
        self.client: Optional[Client] = None
        
    async def initialize(self) -> None:
        """Initialize Supabase client connection."""
        try:
            # Check if in test mode
            if self.config.get("test_mode", True):
                self.logger.info("Running in test mode - database operations will be simulated")
                self.client = None
                return
            
            supabase_url = os.getenv("SUPABASE_URL", self.config.get("url"))
            supabase_key = os.getenv("SUPABASE_ANON_KEY", self.config.get("anon_key"))
            
            if not supabase_url or not supabase_key:
                self.logger.warning("Missing Supabase credentials - running in test mode")
                self.client = None
                return
            
            self.client = create_client(supabase_url, supabase_key)
            
            # Test connection
            await self._test_connection()
            
            self.logger.info("Database connection established successfully")
            
        except Exception as e:
            self.logger.warning(f"Database connection failed, running in test mode: {e}")
            self.client = None
    
    async def _test_connection(self) -> None:
        """Test database connection."""
        try:
            # Simple query to test connection
            if self.client:
                result = self.client.table("user_interactions").select("count").limit(1).execute()
                self.logger.debug("Database connection test successful")
            else:
                raise DatabaseError("Client not initialized")
        except Exception as e:
            raise DatabaseError(f"Database connection test failed: {e}")
    
    async def save_interaction(self, interaction: UserInteraction) -> Dict[str, Any]:
        """Save user interaction to database."""
        try:
            data = {
                "user_id": interaction.user_id,
                "session_id": interaction.session_id,
                "agent_id": interaction.agent_id,
                "prompt": interaction.prompt,
                "timestamp": interaction.timestamp.isoformat(),
                "metadata": interaction.metadata or {}
            }
            
            if self.client:
                result = self.client.table("user_interactions").insert(data).execute()
                if result.data:
                    self.logger.debug(f"Saved interaction for user {interaction.user_id}")
                    return result.data[0]
                else:
                    raise DatabaseError("No data returned from insert operation")
            else:
                # Test mode - simulate successful save
                self.logger.debug(f"[TEST MODE] Simulated saving interaction for user {interaction.user_id}")
                return {"id": 1, **data}
                
        except APIError as e:
            self.logger.error(f"API error saving interaction: {e}")
            raise DatabaseError(f"Failed to save interaction: {e}")
        except Exception as e:
            self.logger.error(f"Error saving interaction: {e}")
            raise DatabaseError(f"Failed to save interaction: {e}")
    
    async def save_response(self, response: AgentResponse) -> Dict[str, Any]:
        """Save agent response to database."""
        try:
            data = {
                "agent_id": response.agent_id,
                "user_id": response.user_id,
                "session_id": response.session_id,
                "content": response.content,
                "timestamp": response.timestamp.isoformat(),
                "metadata": response.metadata or {}
            }
            
            if self.client:
                result = self.client.table("agent_responses").insert(data).execute()
                if result.data:
                    self.logger.debug(f"Saved response from agent {response.agent_id}")
                    return result.data[0]
                else:
                    raise DatabaseError("No data returned from insert operation")
            else:
                # Test mode - simulate successful save
                self.logger.debug(f"[TEST MODE] Simulated saving response from agent {response.agent_id}")
                return {"id": 1, **data}
                
        except APIError as e:
            self.logger.error(f"API error saving response: {e}")
            raise DatabaseError(f"Failed to save response: {e}")
        except Exception as e:
            self.logger.error(f"Error saving response: {e}")
            raise DatabaseError(f"Failed to save response: {e}")
    
    async def get_user_history(
        self, 
        user_id: str, 
        limit: int = 10,
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user interaction history."""
        try:
            if self.client:
                query = self.client.table("user_interactions").select("*")
                query = query.eq("user_id", user_id)
                
                if agent_id:
                    query = query.eq("agent_id", agent_id)
                
                query = query.order("timestamp", desc=True).limit(limit)
                
                result = query.execute()
                return result.data or []
            else:
                # Test mode - return empty history
                self.logger.debug(f"[TEST MODE] Returning empty history for user {user_id}")
                return []
            
        except APIError as e:
            self.logger.error(f"API error getting user history: {e}")
            raise DatabaseError(f"Failed to get user history: {e}")
        except Exception as e:
            self.logger.error(f"Error getting user history: {e}")
            raise DatabaseError(f"Failed to get user history: {e}")
    
    async def get_agent_responses(
        self,
        agent_id: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get agent response history."""
        try:
            if not self.client:
                raise DatabaseError("Database client not initialized")
                
            query = self.client.table("agent_responses").select("*")
            query = query.eq("agent_id", agent_id)
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            query = query.order("timestamp", desc=True).limit(limit)
            
            result = query.execute()
            
            return result.data or []
            
        except APIError as e:
            self.logger.error(f"API error getting agent responses: {e}")
            raise DatabaseError(f"Failed to get agent responses: {e}")
        except Exception as e:
            self.logger.error(f"Error getting agent responses: {e}")
            raise DatabaseError(f"Failed to get agent responses: {e}")
    
    async def save_rag_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any],
        embeddings: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Save RAG document to database."""
        try:
            data = {
                "document_id": document_id,
                "content": content,
                "metadata": metadata,
                "embeddings": embeddings,
                "created_at": datetime.utcnow().isoformat()
            }
            
            if not self.client:
                raise DatabaseError("Database client not initialized")
                
            result = self.client.table("rag_documents").insert(data).execute()
            
            if result.data:
                self.logger.debug(f"Saved RAG document {document_id}")
                return result.data[0]
            else:
                raise DatabaseError("No data returned from insert operation")
                
        except APIError as e:
            self.logger.error(f"API error saving RAG document: {e}")
            raise DatabaseError(f"Failed to save RAG document: {e}")
        except Exception as e:
            self.logger.error(f"Error saving RAG document: {e}")
            raise DatabaseError(f"Failed to save RAG document: {e}")
    
    async def search_rag_documents(
        self,
        query: str,
        limit: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search RAG documents by content similarity."""
        try:
            if self.client:
                # Basic text search - in production you'd use vector similarity
                query_builder = self.client.table("rag_documents").select("*")
                # Use ilike for text search instead of textSearch
                query_builder = query_builder.ilike("content", f"%{query}%")
                
                if metadata_filter:
                    for key, value in metadata_filter.items():
                        query_builder = query_builder.eq(f"metadata->{key}", value)
                
                query_builder = query_builder.limit(limit)
                
                result = query_builder.execute()
                return result.data or []
            else:
                # Test mode - return empty results
                self.logger.debug(f"[TEST MODE] RAG search for query: {query}")
                return []
            
        except APIError as e:
            self.logger.error(f"API error searching RAG documents: {e}")
            raise DatabaseError(f"Failed to search RAG documents: {e}")
        except Exception as e:
            self.logger.error(f"Error searching RAG documents: {e}")
            raise DatabaseError(f"Failed to search RAG documents: {e}")
    
    async def close(self) -> None:
        """Close database connection."""
        try:
            # Supabase client doesn't require explicit closing
            self.client = None
            self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database connection: {e}")
