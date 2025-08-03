#!/usr/bin/env python3
"""
Unit tests for core Agent functionality.
"""
import pytest
import asyncio
from datetime import datetime
import uuid

from core.agent import Agent
from core.database import DatabaseManager
from core.mcp_client import MCPClient
from core.rag_system import RAGSystem
from agents.personalities import PersonalityManager
from agents.business_rules import BusinessRuleEngine
from config.settings import Settings
from models.schemas import UserInteraction, AgentResponse

class TestAgentCore:
    """Test core agent functionality."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings()
    
    @pytest.fixture
    async def test_agent(self, settings):
        """Create test agent instance."""
        agent = Agent(
            agent_id="test_agent",
            personality="analytical",
            business_rules="financial_advisor",
            mcp_servers=settings.MCP_SERVERS,
            database_config=settings.DATABASE_CONFIG
        )
        await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, test_agent):
        """Test agent initialization."""
        assert test_agent.agent_id == "test_agent"
        assert test_agent.personality == "analytical"
        assert test_agent.business_rules == "financial_advisor"
        assert test_agent.database is not None
        assert test_agent.mcp_client is not None
        assert test_agent.rag_system is not None
    
    @pytest.mark.asyncio
    async def test_process_prompt_basic(self, test_agent):
        """Test basic prompt processing."""
        prompt = "What is the best investment strategy for beginners?"
        user_id = "test_user_123"
        session_id = str(uuid.uuid4())
        
        response = await test_agent.process_prompt(prompt, user_id, session_id)
        
        assert isinstance(response, AgentResponse)
        assert response.agent_id == "test_agent"
        assert response.user_id == user_id
        assert response.session_id == session_id
        assert response.content is not None
        assert len(response.content) > 0
        assert isinstance(response.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_process_multiple_prompts(self, test_agent):
        """Test processing multiple prompts in sequence."""
        prompts = [
            "What are the basics of investing?",
            "How much should I save for retirement?",
            "What are the risks of stock market investing?"
        ]
        user_id = "test_user_456"
        
        responses = []
        for prompt in prompts:
            session_id = str(uuid.uuid4())
            response = await test_agent.process_prompt(prompt, user_id, session_id)
            responses.append(response)
        
        assert len(responses) == 3
        for response in responses:
            assert isinstance(response, AgentResponse)
            assert response.agent_id == "test_agent"
            assert response.user_id == user_id
            assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_agent_start_stop(self, settings):
        """Test agent start and stop lifecycle."""
        agent = Agent(
            agent_id="lifecycle_test",
            personality="creative",
            business_rules="content_creator",
            mcp_servers=settings.MCP_SERVERS,
            database_config=settings.DATABASE_CONFIG
        )
        
        # Test start
        await agent.start()
        assert agent.database is not None
        
        # Test processing while running
        response = await agent.process_prompt(
            "Create a catchy headline",
            "test_user",
            str(uuid.uuid4())
        )
        assert response is not None
        
        # Test cleanup
        await agent.cleanup()