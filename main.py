"""
Main entry point for the AI agents system with complete message flow control.
Initializes agents, message broker, session manager, and API server.
"""
import asyncio
import logging
from typing import Dict, Any
from config.settings import Settings
from agents.agent_factory import AgentFactory
from core.message_broker import RabbitMQBroker
from core.session_manager import RedisSessionManager
from core.websocket_server import WebSocketServer
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

async def run_api_server():
    """Run the FastAPI server."""
    import uvicorn
    from api.rest_api import app
    
    settings = Settings()
    
    config = uvicorn.Config(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Initialize and run the complete AI agents system."""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        # Load settings
        settings = Settings()
        
        # Initialize message broker and session manager
        message_broker = RabbitMQBroker(settings.RABBITMQ_URL)
        session_manager = RedisSessionManager(settings.REDIS_URL)
        
        # Initialize components
        await message_broker.initialize()
        await session_manager.initialize()
        
        # Agent configurations with message flow components
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
        
        logger.info("Starting AI agents system with complete message flow control...")
        
        # Create all system tasks
        tasks = []
        
        # Add agent tasks
        for agent_id, config in agent_configs.items():
            tasks.append(asyncio.create_task(run_agent(agent_id, config)))
        
        # Add API server task
        tasks.append(asyncio.create_task(run_api_server()))
        
        # Add WebSocket server task
        websocket_server = WebSocketServer(
            host=settings.WEBSOCKET_HOST,
            port=settings.WEBSOCKET_PORT,
            message_broker=message_broker,
            session_manager=session_manager
        )
        await websocket_server.start()
        logger.info(f"WebSocket server started on {settings.WEBSOCKET_HOST}:{settings.WEBSOCKET_PORT}")
        
        # Run all components concurrently
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        logger.info("System shutdown requested")
        if 'message_broker' in locals():
            message_broker.close()
        if 'session_manager' in locals():
            await session_manager.close()
    except Exception as e:
        logger.error(f"System error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
