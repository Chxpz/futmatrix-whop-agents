"""
FastAPI REST API for agent system management and communication.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.message_broker import RabbitMQBroker, Message
from core.session_manager import RedisSessionManager, UserSession
from core.websocket_server import WebSocketManager
from agents.agent_factory import AgentFactory
from config.settings import Settings
from utils.logger import setup_logger


# Pydantic models for API
class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    agent_id: str = Field(..., description="Agent ID (agent_alpha or agent_beta)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Initial session context")


class SendMessageRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Message metadata")


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    agent_id: str
    created_at: str
    last_activity: str
    is_active: bool
    message_count: int


class MessageResponse(BaseModel):
    message_id: str
    type: str
    content: str
    timestamp: str
    session_id: str


class AgentStatusResponse(BaseModel):
    agent_id: str
    personality: str
    business_rules: str
    status: str
    active_sessions: int


# Global components
message_broker: RabbitMQBroker = None
session_manager: RedisSessionManager = None
websocket_manager: WebSocketManager = None
agents: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global message_broker, session_manager, websocket_manager, agents
    
    # Setup logging
    setup_logger()
    
    # Load settings
    settings = Settings()
    
    # Initialize components
    message_broker = RabbitMQBroker(settings.RABBITMQ_URL)
    session_manager = RedisSessionManager(settings.REDIS_URL)
    websocket_manager = WebSocketManager(message_broker, session_manager)
    
    # Initialize message broker and session manager
    await message_broker.initialize()
    await session_manager.initialize()
    
    # Create agents
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
    
    for agent_id, config in agent_configs.items():
        agent = await AgentFactory.create_agent(agent_id, config)
        agents[agent_id] = agent
    
    # Start message consumers
    start_message_consumers()
    
    yield
    
    # Cleanup
    message_broker.close()
    await session_manager.close()


def start_message_consumers():
    """Start RabbitMQ message consumers."""
    def handle_user_prompt(message: Message):
        """Handle user prompt from queue."""
        asyncio.create_task(process_user_prompt(message))
    
    def handle_agent_response(message: Message):
        """Handle agent response from queue."""
        asyncio.create_task(process_agent_response(message))
    
    message_broker.consume_user_prompts(handle_user_prompt)
    message_broker.consume_agent_responses(handle_agent_response)


async def process_user_prompt(message: Message):
    """Process user prompt through agent."""
    try:
        agent = agents.get(message.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {message.agent_id} not found")
        
        # Process through agent workflow
        response = await agent.process_prompt(
            user_id=message.user_id,
            session_id=message.session_id,
            prompt=message.content,
            context=message.metadata
        )
        
        # Create response message
        response_message = Message(
            id=str(uuid.uuid4()),
            user_id=message.user_id,
            agent_id=message.agent_id,
            content=response["content"],
            message_type="agent_response",
            timestamp=datetime.utcnow(),
            session_id=message.session_id,
            metadata=response.get("metadata", {})
        )
        
        # Publish response
        message_broker.publish_agent_response(response_message)
        
        # Send via WebSocket if connected
        await websocket_manager._send_to_user(message.user_id, {
            "type": "agent_response",
            "message_id": response_message.id,
            "agent_id": message.agent_id,
            "content": response_message.content,
            "timestamp": response_message.timestamp.isoformat(),
            "session_id": message.session_id
        })
        
    except Exception as e:
        # Handle error
        error_message = Message(
            id=str(uuid.uuid4()),
            user_id=message.user_id,
            agent_id=message.agent_id,
            content=f"Error processing prompt: {str(e)}",
            message_type="error",
            timestamp=datetime.utcnow(),
            session_id=message.session_id,
            metadata={"error": True}
        )
        
        message_broker.publish_agent_response(error_message)


async def process_agent_response(message: Message):
    """Process agent response (for logging, analytics, etc.)."""
    # Add response to session history
    await session_manager.add_message_to_session(
        message.session_id,
        {
            "id": message.id,
            "type": "agent_response",
            "content": message.content,
            "agent_id": message.agent_id,
            "timestamp": message.timestamp.isoformat()
        }
    )


# Create FastAPI app
app = FastAPI(
    title="AI Agents System API",
    description="REST API for managing AI agents and real-time communication",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "message_broker": "connected" if message_broker else "disconnected",
            "session_manager": "connected" if session_manager else "disconnected",
            "agents": list(agents.keys())
        }
    }


@app.get("/agents", response_model=List[AgentStatusResponse])
async def list_agents():
    """List all available agents."""
    agent_list = []
    
    for agent_id, agent in agents.items():
        # Get active sessions for this agent
        active_sessions = await session_manager.get_agent_sessions(agent_id)
        
        agent_list.append(AgentStatusResponse(
            agent_id=agent_id,
            personality=agent.personality,
            business_rules=agent.business_rules,
            status="active",
            active_sessions=len(active_sessions)
        ))
    
    return agent_list


@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new user session."""
    # Validate agent exists
    if request.agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Create session
    session = await session_manager.create_session(
        user_id=request.user_id,
        session_id=session_id,
        agent_id=request.agent_id,
        context=request.context
    )
    
    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        agent_id=session.agent_id,
        created_at=session.created_at.isoformat(),
        last_activity=session.last_activity.isoformat(),
        is_active=session.is_active,
        message_count=len(session.message_history)
    )


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details."""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        agent_id=session.agent_id,
        created_at=session.created_at.isoformat(),
        last_activity=session.last_activity.isoformat(),
        is_active=session.is_active,
        message_count=len(session.message_history)
    )


@app.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str, limit: int = 50):
    """Get session message history."""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get recent messages
    messages = session.message_history[-limit:] if session.message_history else []
    
    return [
        MessageResponse(
            message_id=msg.get("id", ""),
            type=msg.get("type", ""),
            content=msg.get("content", ""),
            timestamp=msg.get("timestamp", ""),
            session_id=session_id
        )
        for msg in messages
    ]


@app.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(session_id: str, request: SendMessageRequest):
    """Send message to agent."""
    # Validate session exists
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create message
    message = Message(
        id=str(uuid.uuid4()),
        user_id=session.user_id,
        agent_id=session.agent_id,
        content=request.content,
        message_type="user_prompt",
        timestamp=datetime.utcnow(),
        session_id=session_id,
        metadata=request.metadata or {}
    )
    
    # Add to session history
    await session_manager.add_message_to_session(
        session_id,
        {
            "id": message.id,
            "type": "user_prompt",
            "content": message.content,
            "user_id": message.user_id,
            "timestamp": message.timestamp.isoformat()
        }
    )
    
    # Publish to message broker
    message_broker.publish_user_prompt(message)
    
    return MessageResponse(
        message_id=message.id,
        type=message.message_type,
        content=message.content,
        timestamp=message.timestamp.isoformat(),
        session_id=session_id
    )


@app.delete("/sessions/{session_id}")
async def end_session(session_id: str):
    """End a session."""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await session_manager.end_session(session_id)
    
    return {"message": "Session ended successfully"}


@app.get("/users/{user_id}/sessions", response_model=List[SessionResponse])
async def get_user_sessions(user_id: str):
    """Get all sessions for a user."""
    session_ids = await session_manager.get_user_sessions(user_id)
    sessions = []
    
    for session_id in session_ids:
        session = await session_manager.get_session(session_id)
        if session:
            sessions.append(SessionResponse(
                session_id=session.session_id,
                user_id=session.user_id,
                agent_id=session.agent_id,
                created_at=session.created_at.isoformat(),
                last_activity=session.last_activity.isoformat(),
                is_active=session.is_active,
                message_count=len(session.message_history)
            ))
    
    return sessions


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    
    try:
        # Wait for authentication
        auth_data = await websocket.receive_json()
        user_id = auth_data.get("user_id")
        connection_type = auth_data.get("type", "user")
        
        if not user_id:
            await websocket.send_json({
                "type": "error",
                "message": "Missing user_id in authentication"
            })
            return
        
        # Register connection
        connection_id = await websocket_manager.register_connection(
            websocket, user_id, connection_type
        )
        
        # Handle messages
        while True:
            message_data = await websocket.receive_json()
            await websocket_manager.handle_message(connection_id, message_data)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"WebSocket error: {str(e)}"
        })
    finally:
        if 'connection_id' in locals():
            await websocket_manager.unregister_connection(connection_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)