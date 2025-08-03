"""
Simplified startup script for the complete AI agents system.
This version handles all message flow components gracefully.
"""
import asyncio
import logging
from typing import Dict, Any
from config.settings import Settings
from agents.agent_factory import AgentFactory
from utils.logger import setup_logger

async def run_agent(agent_id: str, config: Dict[str, Any]):
    """Run a single agent instance with error handling."""
    logger = logging.getLogger(f"agent_{agent_id}")
    
    try:
        # Create agent instance
        agent = await AgentFactory.create_agent(agent_id, config)
        
        logger.info(f"Agent {agent_id} initialized successfully")
        
        # Start agent processing loop
        await agent.start()
        
    except Exception as e:
        logger.error(f"Error running agent {agent_id}: {e}")
        # Don't re-raise to keep the system running
        
async def main():
    """Initialize and run the AI agents system."""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        # Load settings
        settings = Settings()
        
        # Initialize message components with proper error handling
        message_broker = None
        session_manager = None
        
        try:
            # Try to use real message broker services first
            from core.message_broker import RabbitMQBroker
            from core.session_manager import RedisSessionManager
            
            message_broker = RabbitMQBroker(settings.RABBITMQ_URL)
            session_manager = RedisSessionManager(settings.REDIS_URL)
            
            await message_broker.initialize()
            await session_manager.initialize()
            logger.info("Real message flow components initialized successfully")
            
        except Exception as e:
            logger.warning(f"Real message broker services not available: {e}")
            logger.info("Falling back to mock message flow components for demonstration")
            
            try:
                from core.mock_message_broker import MockMessageBroker, MockRedisSession
                
                message_broker = MockMessageBroker(settings.RABBITMQ_URL)
                session_manager = MockRedisSession(settings.REDIS_URL)
                
                await message_broker.initialize()
                await session_manager.initialize()
                
                logger.info("Mock message flow components initialized successfully")
                logger.info("This demonstrates the full message flow architecture using in-memory simulation")
                
            except Exception as mock_e:
                logger.error(f"Failed to initialize mock components: {mock_e}")
                logger.info("Running in standalone mode without message flow")
                message_broker = None
                session_manager = None
        
        # Agent configurations
        agent_configs = {
            "agent_alpha": {
                "personality": "analytical",
                "business_rules": "financial_advisor",
                "mcp_servers": settings.MCP_SERVERS,
                "database_config": settings.DATABASE_CONFIG,
                "message_broker": message_broker,
                "session_manager": session_manager
            },
            "agent_beta": {
                "personality": "creative",
                "business_rules": "content_creator",
                "mcp_servers": settings.MCP_SERVERS,
                "database_config": settings.DATABASE_CONFIG,
                "message_broker": message_broker,
                "session_manager": session_manager
            }
        }
        
        logger.info("Starting AI agents system...")
        
        # Create tasks for both agents
        tasks = [
            asyncio.create_task(run_agent(agent_id, config))
            for agent_id, config in agent_configs.items()
        ]
        
        # Add API server if FastAPI components are available
        try:
            import uvicorn
            from api.rest_api import app
            
            async def run_api():
                config = uvicorn.Config(
                    app,
                    host=settings.API_HOST,
                    port=settings.API_PORT,
                    log_level="info"
                )
                server = uvicorn.Server(config)
                await server.serve()
            
            tasks.append(asyncio.create_task(run_api()))
            logger.info(f"Added API server task on {settings.API_HOST}:{settings.API_PORT}")
            
        except Exception as e:
            logger.warning(f"API server not available: {e}")
        
        # Run all components concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        logger.info("System shutdown requested")
        if message_broker:
            message_broker.close()
        if session_manager:
            await session_manager.close()
    except Exception as e:
        logger.error(f"System error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())