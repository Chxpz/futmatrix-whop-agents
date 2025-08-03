"""
Configuration settings for the AI agents system.
"""
import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # Database configuration  
        self.DATABASE_CONFIG = {
            "url": os.getenv("SUPABASE_URL"),
            "anon_key": os.getenv("SUPABASE_ANON_KEY"),
            "service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
            "test_mode": os.getenv("DATABASE_TEST_MODE", "true").lower() == "true"
        }
        
        # MCP server configuration
        self.MCP_SERVERS = [
            os.getenv("MCP_SERVER_1", "http://localhost:3001"),
            os.getenv("MCP_SERVER_2", "http://localhost:3002")
        ]
        
        # Logging configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # API Keys
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default_openai_key")
        self.MCP_API_KEY = os.getenv("MCP_API_KEY", "default_mcp_key")
        
        # Agent configuration
        self.AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "300"))  # 5 minutes
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
        
        # RAG configuration
        self.RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
        self.RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))
        
        # Business rules configuration
        self.ENABLE_FINANCIAL_COMPLIANCE = os.getenv("ENABLE_FINANCIAL_COMPLIANCE", "true").lower() == "true"
        self.ENABLE_CONTENT_MODERATION = os.getenv("ENABLE_CONTENT_MODERATION", "true").lower() == "true"
        
        # Security configuration
        self.ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        required_settings = [
            self.DATABASE_CONFIG["url"],
            self.DATABASE_CONFIG["anon_key"]
        ]
        
        for setting in required_settings:
            if not setting or setting.startswith("your-") or setting == "default_":
                return False
        
        return True
    
    def get_database_tables(self) -> Dict[str, str]:
        """Get database table creation SQL."""
        return {
            "user_interactions": """
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_interactions_agent_id ON user_interactions(agent_id);
                CREATE INDEX IF NOT EXISTS idx_user_interactions_session_id ON user_interactions(session_id);
                CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp);
            """,
            "agent_responses": """
                CREATE TABLE IF NOT EXISTS agent_responses (
                    id BIGSERIAL PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_agent_responses_agent_id ON agent_responses(agent_id);
                CREATE INDEX IF NOT EXISTS idx_agent_responses_user_id ON agent_responses(user_id);
                CREATE INDEX IF NOT EXISTS idx_agent_responses_session_id ON agent_responses(session_id);
                CREATE INDEX IF NOT EXISTS idx_agent_responses_timestamp ON agent_responses(timestamp);
            """,
            "rag_documents": """
                CREATE TABLE IF NOT EXISTS rag_documents (
                    id BIGSERIAL PRIMARY KEY,
                    document_id TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    embeddings FLOAT8[] NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_rag_documents_document_id ON rag_documents(document_id);
                CREATE INDEX IF NOT EXISTS idx_rag_documents_content_search ON rag_documents USING gin(to_tsvector('english', content));
                CREATE INDEX IF NOT EXISTS idx_rag_documents_metadata ON rag_documents USING gin(metadata);
            """,
            "agent_configurations": """
                CREATE TABLE IF NOT EXISTS agent_configurations (
                    id BIGSERIAL PRIMARY KEY,
                    agent_id TEXT UNIQUE NOT NULL,
                    personality TEXT NOT NULL,
                    business_rules TEXT NOT NULL,
                    configuration JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_agent_configurations_agent_id ON agent_configurations(agent_id);
                CREATE INDEX IF NOT EXISTS idx_agent_configurations_personality ON agent_configurations(personality);
                CREATE INDEX IF NOT EXISTS idx_agent_configurations_business_rules ON agent_configurations(business_rules);
            """
        }
