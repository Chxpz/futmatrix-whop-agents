#!/usr/bin/env python3
"""
Unit tests for LangGraph workflow functionality.
"""
import pytest
import asyncio
from datetime import datetime
import uuid

from core.workflow import WorkflowEngine
from core.agent import Agent
from models.schemas import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from config.settings import Settings

class TestWorkflow:
    """Test LangGraph workflow functionality."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings()
    
    @pytest.fixture
    async def test_agent(self, settings):
        """Create test agent for workflow testing."""
        agent = Agent(
            agent_id="workflow_test_agent",
            personality="analytical",
            business_rules="financial_advisor",
            mcp_servers=settings.MCP_SERVERS,
            database_config=settings.DATABASE_CONFIG
        )
        await agent.initialize()
        yield agent
        await agent.cleanup()
    
    @pytest.fixture
    def workflow_engine(self, test_agent):
        """Create workflow engine instance."""
        return WorkflowEngine(test_agent)
    
    @pytest.fixture
    def test_state(self):
        """Create test agent state."""
        return AgentState(
            user_id="workflow_test_user",
            session_id=str(uuid.uuid4()),
            messages=[HumanMessage(content="Test workflow message")],
            context={}
        )
    
    @pytest.mark.asyncio
    async def test_receive_input(self, workflow_engine, test_state):
        """Test input reception workflow step."""
        result = await workflow_engine.receive_input(test_state)
        
        assert result == test_state
        assert "input_validation" in test_state.context
        assert test_state.context["input_validation"]["valid"] is True
    
    @pytest.mark.asyncio
    async def test_notify_user(self, workflow_engine, test_state):
        """Test user notification workflow step."""
        result = await workflow_engine.notify_user(test_state)
        
        assert result == test_state
        assert "notification" in test_state.context
        assert test_state.context["notification"]["sent"] is True
    
    @pytest.mark.asyncio
    async def test_query_database(self, workflow_engine, test_state):
        """Test database query workflow step."""
        result = await workflow_engine.query_database(test_state)
        
        assert result == test_state
        assert "database_results" in test_state.context
        assert "user_history" in test_state.context["database_results"]
        assert "rag_results" in test_state.context["database_results"]
    
    @pytest.mark.asyncio
    async def test_apply_business_logic(self, workflow_engine, test_state):
        """Test business logic application workflow step."""
        result = await workflow_engine.apply_business_logic(test_state)
        
        assert result == test_state
        assert "business_logic_result" in test_state.context
        assert "compliance_check" in test_state.context["business_logic_result"]
    
    @pytest.mark.asyncio
    async def test_generate_response(self, workflow_engine, test_state):
        """Test response generation workflow step."""
        # Set up context from previous steps
        test_state.context = {
            "database_results": {"user_history": []},
            "business_logic_result": {"compliance_check": {"passed": True}}
        }
        
        result = await workflow_engine.generate_response(test_state)
        
        assert result == test_state
        assert len(test_state.messages) >= 2
        assert isinstance(test_state.messages[-1], AIMessage)
        assert len(test_state.messages[-1].content) > 0
    
    @pytest.mark.asyncio
    async def test_send_response(self, workflow_engine, test_state):
        """Test response sending workflow step."""
        # Add an AI message to test
        test_state.messages.append(AIMessage(content="Test response"))
        
        result = await workflow_engine.send_response(test_state)
        
        assert result == test_state
        assert "response_sent" in test_state.context
        assert test_state.context["response_sent"] is True
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, test_agent):
        """Test complete workflow execution through agent."""
        prompt = "What are the best investment options for beginners?"
        user_id = "workflow_test_user"
        session_id = str(uuid.uuid4())
        
        response = await test_agent.process_prompt(prompt, user_id, session_id)
        
        assert response is not None
        assert response.agent_id == test_agent.agent_id
        assert response.user_id == user_id
        assert response.session_id == session_id
        assert response.content is not None
        assert len(response.content) > 0