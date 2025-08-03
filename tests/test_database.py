#!/usr/bin/env python3
"""
Unit tests for database management.
"""
import pytest
import asyncio
from datetime import datetime
import uuid

from core.database import DatabaseManager
from models.schemas import UserInteraction, AgentResponse
from config.settings import Settings

class TestDatabase:
    """Test database management functionality."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings()
    
    # Using shared database fixture from conftest.py
    
    @pytest.mark.asyncio
    async def test_database_initialization(self, database):
        """Test database initialization in test mode."""
        assert database is not None
        # In test mode, client should be None
        assert database.client is None
    
    @pytest.mark.asyncio
    async def test_save_interaction(self, database):
        """Test saving user interaction."""
        interaction = UserInteraction(
            user_id="test_user_123",
            session_id=str(uuid.uuid4()),
            agent_id="test_agent",
            prompt="Test prompt for interaction",
            timestamp=datetime.utcnow(),
            metadata={"test": True}
        )
        
        result = await database.save_interaction(interaction)
        
        assert result is not None
        assert "id" in result
        assert result["user_id"] == interaction.user_id
        assert result["agent_id"] == interaction.agent_id
        assert result["prompt"] == interaction.prompt
    
    @pytest.mark.asyncio
    async def test_save_response(self, database):
        """Test saving agent response."""
        response = AgentResponse(
            agent_id="test_agent",
            user_id="test_user_123",
            session_id=str(uuid.uuid4()),
            content="Test response content",
            timestamp=datetime.utcnow(),
            metadata={"confidence": 0.95}
        )
        
        result = await database.save_response(response)
        
        assert result is not None
        assert "id" in result
        assert result["agent_id"] == response.agent_id
        assert result["user_id"] == response.user_id
        assert result["content"] == response.content
    
    @pytest.mark.asyncio
    async def test_get_user_history(self, database):
        """Test retrieving user history."""
        user_id = "test_user_456"
        
        # In test mode, this should return empty list
        history = await database.get_user_history(user_id, limit=10)
        
        assert isinstance(history, list)
        assert len(history) == 0  # Test mode returns empty
    
    @pytest.mark.asyncio
    async def test_get_agent_responses(self, database):
        """Test retrieving agent responses."""
        agent_id = "test_agent"
        
        # In test mode, this should return empty list
        responses = await database.get_agent_responses(agent_id, limit=10)
        
        assert isinstance(responses, list)
        assert len(responses) == 0  # Test mode returns empty
    
    @pytest.mark.asyncio
    async def test_search_rag_documents(self, database):
        """Test RAG document search."""
        query = "investment strategies"
        
        # In test mode, this should return empty list
        documents = await database.search_rag_documents(query, limit=5)
        
        assert isinstance(documents, list)
        assert len(documents) == 0  # Test mode returns empty