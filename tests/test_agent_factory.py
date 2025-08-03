#!/usr/bin/env python3
"""
Unit tests for Agent Factory functionality.
"""
import pytest
import asyncio
from agents.agent_factory import AgentFactory
from config.settings import Settings

class TestAgentFactory:
    """Test agent factory creation and configuration."""
    
    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings()
    
    @pytest.fixture
    def agent_config(self, settings):
        """Create base agent configuration."""
        return {
            "personality": "analytical",
            "business_rules": "financial_advisor",
            "mcp_servers": settings.MCP_SERVERS,
            "database_config": settings.DATABASE_CONFIG
        }
    
    @pytest.mark.asyncio
    async def test_create_analytical_agent(self, agent_config):
        """Test creation of analytical agent."""
        agent = await AgentFactory.create_agent("test_agent_alpha", agent_config)
        
        assert agent is not None
        assert agent.agent_id == "test_agent_alpha"
        assert agent.personality == "analytical"
        assert agent.business_rules == "financial_advisor"
        
        # Cleanup
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_create_creative_agent(self, agent_config):
        """Test creation of creative agent."""
        agent_config.update({
            "personality": "creative",
            "business_rules": "content_creator"
        })
        
        agent = await AgentFactory.create_agent("test_agent_beta", agent_config)
        
        assert agent is not None
        assert agent.agent_id == "test_agent_beta"
        assert agent.personality == "creative"
        assert agent.business_rules == "content_creator"
        
        # Cleanup
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_invalid_personality(self, agent_config):
        """Test agent creation with invalid personality."""
        agent_config["personality"] = "invalid_personality"
        
        with pytest.raises(ValueError):
            await AgentFactory.create_agent("test_invalid", agent_config)
    
    @pytest.mark.asyncio
    async def test_invalid_business_rules(self, agent_config):
        """Test agent creation with invalid business rules."""
        agent_config["business_rules"] = "invalid_rules"
        
        with pytest.raises(ValueError):
            await AgentFactory.create_agent("test_invalid", agent_config)