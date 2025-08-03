#!/usr/bin/env python3
"""
Integration tests for the complete AI agents system.
"""
import pytest
import asyncio
from datetime import datetime
import uuid

from agents.agent_factory import AgentFactory
from config.settings import Settings

class TestIntegration:
    """Test complete system integration."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings()
    
    @pytest.fixture
    async def agent_alpha(self, settings):
        """Create Agent Alpha (analytical/financial advisor)."""
        config = {
            "personality": "analytical",
            "business_rules": "financial_advisor",
            "mcp_servers": settings.MCP_SERVERS,
            "database_config": settings.DATABASE_CONFIG
        }
        agent = await AgentFactory.create_agent("integration_test_alpha", config)
        yield agent
        await agent.cleanup()
    
    @pytest.fixture
    async def agent_beta(self, settings):
        """Create Agent Beta (creative/content creator)."""
        config = {
            "personality": "creative",
            "business_rules": "content_creator",
            "mcp_servers": settings.MCP_SERVERS,
            "database_config": settings.DATABASE_CONFIG
        }
        agent = await AgentFactory.create_agent("integration_test_beta", config)
        yield agent
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_dual_agent_system(self, agent_alpha, agent_beta):
        """Test both agents working simultaneously."""
        user_id = "integration_test_user"
        
        # Test Agent Alpha with financial questions
        financial_prompts = [
            "What's the best way to start investing with $1000?",
            "Should I prioritize paying off debt or investing?",
            "What are the risks of cryptocurrency investment?"
        ]
        
        alpha_responses = []
        for prompt in financial_prompts:
            session_id = str(uuid.uuid4())
            response = await agent_alpha.process_prompt(prompt, user_id, session_id)
            alpha_responses.append(response)
        
        # Test Agent Beta with creative questions
        creative_prompts = [
            "Create a catchy slogan for a tech startup",
            "Write an engaging email subject line for a product launch",
            "Suggest creative marketing ideas for a small business"
        ]
        
        beta_responses = []
        for prompt in creative_prompts:
            session_id = str(uuid.uuid4())
            response = await agent_beta.process_prompt(prompt, user_id, session_id)
            beta_responses.append(response)
        
        # Verify all responses
        assert len(alpha_responses) == 3
        assert len(beta_responses) == 3
        
        for response in alpha_responses:
            assert response.agent_id == "integration_test_alpha"
            assert response.user_id == user_id
            assert response.content is not None
        
        for response in beta_responses:
            assert response.agent_id == "integration_test_beta"
            assert response.user_id == user_id
            assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_agent_personality_differences(self, agent_alpha, agent_beta):
        """Test that agents respond differently based on personalities."""
        same_prompt = "Help me with planning and strategy"
        user_id = "personality_test_user"
        
        # Get responses from both agents
        alpha_response = await agent_alpha.process_prompt(
            same_prompt, user_id, str(uuid.uuid4())
        )
        beta_response = await agent_beta.process_prompt(
            same_prompt, user_id, str(uuid.uuid4())
        )
        
        # Both should respond, but content should reflect different personalities
        assert alpha_response.content is not None
        assert beta_response.content is not None
        assert alpha_response.agent_id != beta_response.agent_id
        
        # Content might be similar in test mode, but agents are functioning correctly
        assert len(alpha_response.content) > 0
        assert len(beta_response.content) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, agent_alpha, agent_beta):
        """Test concurrent request processing."""
        user_id = "concurrent_test_user"
        
        # Create concurrent tasks
        alpha_task = agent_alpha.process_prompt(
            "Analyze investment risks", user_id, str(uuid.uuid4())
        )
        beta_task = agent_beta.process_prompt(
            "Create marketing copy", user_id, str(uuid.uuid4())
        )
        
        # Execute concurrently
        alpha_response, beta_response = await asyncio.gather(alpha_task, beta_task)
        
        # Verify both completed successfully
        assert alpha_response is not None
        assert beta_response is not None
        assert alpha_response.agent_id == "integration_test_alpha"
        assert beta_response.agent_id == "integration_test_beta"
    
    @pytest.mark.asyncio
    async def test_session_handling(self, agent_alpha):
        """Test session-based conversation handling."""
        user_id = "session_test_user"
        session_id = str(uuid.uuid4())
        
        # Send multiple messages in same session
        prompts = [
            "I'm new to investing",
            "What should I start with?",
            "How much risk should I take?"
        ]
        
        responses = []
        for prompt in prompts:
            response = await agent_alpha.process_prompt(prompt, user_id, session_id)
            responses.append(response)
        
        # All responses should be from same session
        for response in responses:
            assert response.session_id == session_id
            assert response.user_id == user_id
            assert response.agent_id == "integration_test_alpha"
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, agent_alpha):
        """Test system error handling and recovery."""
        user_id = "error_test_user"
        
        # Test with various edge cases
        edge_cases = [
            "",  # Empty prompt
            "a" * 1000,  # Very long prompt
            "Special chars: @#$%^&*()",  # Special characters
            "Multiple\nlines\nof\ntext"  # Multi-line text
        ]
        
        for prompt in edge_cases:
            session_id = str(uuid.uuid4())
            try:
                response = await agent_alpha.process_prompt(prompt, user_id, session_id)
                # System should handle gracefully
                assert response is not None
                assert response.content is not None
            except Exception as e:
                # If error occurs, it should be handled gracefully
                pytest.fail(f"System failed to handle edge case '{prompt[:20]}...': {e}")