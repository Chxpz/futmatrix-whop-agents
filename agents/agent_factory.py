"""
Factory for creating configured AI agents with different personalities.
"""
import logging
from typing import Dict, Any
from core.agent import Agent
from utils.exceptions import AgentError

class AgentFactory:
    """Factory class for creating AI agents with specific configurations."""
    
    @staticmethod
    async def create_agent(agent_id: str, config: Dict[str, Any]) -> Agent:
        """Create and initialize an AI agent with the specified configuration."""
        logger = logging.getLogger("agent_factory")
        
        try:
            # Validate required configuration
            required_keys = ["personality", "business_rules", "mcp_servers", "database_config"]
            for key in required_keys:
                if key not in config:
                    raise AgentError(f"Missing required configuration key: {key}")
            
            # Create agent instance
            agent = Agent(
                agent_id=agent_id,
                personality=config["personality"],
                business_rules=config["business_rules"],
                database_config=config["database_config"],
                mcp_servers=config["mcp_servers"]
            )
            
            logger.info(f"Created agent {agent_id} with personality '{config['personality']}' and business rules '{config['business_rules']}'")
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            raise AgentError(f"Agent creation failed: {e}")
    
    @staticmethod
    def get_available_personalities() -> Dict[str, str]:
        """Get available agent personalities."""
        return {
            "analytical": "Data-driven, logical, and systematic approach to problem solving",
            "creative": "Innovative, imaginative, and artistic approach to challenges",
            "helpful": "Supportive, friendly, and service-oriented assistance",
            "professional": "Formal, business-focused, and efficiency-oriented responses"
        }
    
    @staticmethod
    def get_available_business_rules() -> Dict[str, str]:
        """Get available business rule types."""
        return {
            "financial_advisor": "Financial planning, investment advice, and market analysis",
            "content_creator": "Content generation, creative writing, and marketing assistance",
            "technical_support": "Technical problem solving and IT assistance",
            "general_assistant": "General purpose assistance and information provision"
        }
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """Validate agent configuration."""
        try:
            required_keys = ["personality", "business_rules", "mcp_servers", "database_config"]
            
            for key in required_keys:
                if key not in config:
                    return False
            
            # Validate personality
            available_personalities = AgentFactory.get_available_personalities()
            if config["personality"] not in available_personalities:
                return False
            
            # Validate business rules
            available_rules = AgentFactory.get_available_business_rules()
            if config["business_rules"] not in available_rules:
                return False
            
            # Validate MCP servers list
            if not isinstance(config["mcp_servers"], list):
                return False
            
            # Validate database config
            if not isinstance(config["database_config"], dict):
                return False
            
            return True
            
        except Exception:
            return False
