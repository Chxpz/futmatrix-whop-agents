"""
Main entry point for the AI agents system.
Initializes and runs two independent agents with different personalities.
"""
import asyncio
import logging
from typing import Dict, Any
from config.settings import Settings
from agents.agent_factory import AgentFactory
from utils.logger import setup_logger

async def run_agent(agent_id: str, config: Dict[str, Any]):
    """Run a single agent instance."""
    logger = logging.getLogger(f"agent_{agent_id}")
    
    try:
        # Create agent instance
        agent = await AgentFactory.create_agent(agent_id, config)
        
        logger.info(f"Agent {agent_id} initialized successfully")
        
        # Start agent processing loop
        await agent.start()
        
    except Exception as e:
        logger.error(f"Error running agent {agent_id}: {e}")
        raise

async def main():
    """Initialize and run both AI agents."""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        # Load settings
        settings = Settings()
        
        # Agent configurations
        agent_configs = {
            "agent_alpha": {
                "personality": "analytical",
                "business_rules": "financial_advisor",
                "mcp_servers": settings.MCP_SERVERS,
                "database_config": settings.DATABASE_CONFIG
            },
            "agent_beta": {
                "personality": "creative",
                "business_rules": "content_creator",
                "mcp_servers": settings.MCP_SERVERS,
                "database_config": settings.DATABASE_CONFIG
            }
        }
        
        logger.info("Starting AI agents system...")
        
        # Create tasks for both agents
        tasks = [
            asyncio.create_task(run_agent(agent_id, config))
            for agent_id, config in agent_configs.items()
        ]
        
        # Run agents concurrently
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        logger.info("System shutdown requested")
    except Exception as e:
        logger.error(f"System error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
