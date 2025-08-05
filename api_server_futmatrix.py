#!/usr/bin/env python3
"""
Futmatrix AI Agents API Server
Coach and Rivalizer agents for EA Sports FC 25 competitive gaming platform
Built using the existing AI Agents Factory system
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import Settings
from agents.agent_factory import AgentFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Pydantic models for API requests
class CoachingRequest(BaseModel):
    user_id: str
    message: str
    focus_areas: list[str] = ["finishing", "defending", "strategy"]

class MatchmakingRequest(BaseModel):
    user_id: str
    message: str
    skill_level: str = "intermediate"
    playstyle: str = "balanced"

class AgentResponse(BaseModel):
    success: bool
    agent_id: str
    user_id: str
    response: str
    tokens_used: int = 0
    timestamp: str
    error: str = None

# Global variables
app = FastAPI(
    title="Futmatrix AI Agents API",
    description="Coach and Rivalizer agents for EA Sports FC 25 competitive gaming",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global factory instance
agent_factory: AgentFactory = None

@app.on_event("startup")
async def startup_event():
    """Initialize the Futmatrix agents on startup."""
    global agent_factory
    
    logger = logging.getLogger("futmatrix_api")
    logger.info("🎮 Starting Futmatrix AI Agents API Server")
    
    try:
        # Initialize settings and factory
        settings = Settings()
        agent_factory = AgentFactory(settings)
        
        # Initialize the factory
        await agent_factory.initialize()
        logger.info("✅ Agent factory initialized")
        
        # Create Futmatrix agents
        logger.info("🏆 Creating Coach Agent...")
        coach_agent = agent_factory.create_agent(
            agent_id="futmatrix_coach",
            personality_type="coaching", 
            business_domain="sports_coaching"
        )
        logger.info(f"✅ Coach Agent created: {coach_agent.agent_id}")
        
        logger.info("⚔️ Creating Rivalizer Agent...")
        rivalizer_agent = agent_factory.create_agent(
            agent_id="futmatrix_rivalizer",
            personality_type="competitive",
            business_domain="competitive_gaming"
        )
        logger.info(f"✅ Rivalizer Agent created: {rivalizer_agent.agent_id}")
        
        # Initialize and start agents
        await agent_factory.initialize_all_agents()
        await agent_factory.start_all_agents()
        
        logger.info("🚀 Futmatrix AI Agents API Server ready!")
        logger.info("📋 Available endpoints:")
        logger.info("   GET  /                     - System info")
        logger.info("   GET  /health               - Health check")
        logger.info("   GET  /agents               - List agents")
        logger.info("   POST /coach/analyze        - Get coaching analysis")
        logger.info("   POST /rivalizer/match      - Find match opponents")
        logger.info("   GET  /docs                 - API documentation")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Futmatrix agents: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up agents on shutdown."""
    global agent_factory
    
    logger = logging.getLogger("futmatrix_api")
    logger.info("🛑 Shutting down Futmatrix AI Agents API Server")
    
    if agent_factory:
        try:
            await agent_factory.stop_all_agents()
            logger.info("✅ All agents stopped successfully")
        except Exception as e:
            logger.error(f"⚠️ Error during shutdown: {e}")

@app.get("/")
async def root():
    """Get system information."""
    return {
        "service": "Futmatrix AI Agents API",
        "version": "1.0.0",
        "platform": "EA Sports FC 25 Competitive Gaming",
        "description": "Coach and Rivalizer agents for performance optimization and competitive matchmaking",
        "agents": [
            {
                "agent_id": "futmatrix_coach",
                "name": "Coach Agent",
                "description": "Performance analysis and training optimization",
                "personality": "coaching",
                "specialization": "sports_coaching"
            },
            {
                "agent_id": "futmatrix_rivalizer", 
                "name": "Rivalizer Agent",
                "description": "Competitive matchmaking and strategic analysis",
                "personality": "competitive",
                "specialization": "competitive_gaming"
            }
        ],
        "endpoints": {
            "coach_analysis": "/coach/analyze",
            "rivalizer_matching": "/rivalizer/match",
            "health_check": "/health",
            "documentation": "/docs"
        },
        "powered_by": "AI Agents Factory + OpenAI GPT-4o",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Check system health."""
    global agent_factory
    
    if not agent_factory:
        raise HTTPException(status_code=503, detail="Agent factory not initialized")
    
    try:
        health = await agent_factory.health_check()
        return {
            "status": "healthy" if health["factory_status"] == "healthy" else "unhealthy",
            "factory_status": health["factory_status"],
            "openai_integration": health["openai_integration"]["status"],
            "agents": {
                "total": len(health["agents"]),
                "healthy": len([a for a in health["agents"].values() if a["status"] == "healthy"]),
                "details": health["agents"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List all available agents."""
    global agent_factory
    
    if not agent_factory:
        raise HTTPException(status_code=503, detail="Agent factory not initialized")
    
    try:
        agents = agent_factory.list_agents()
        stats = agent_factory.get_factory_stats()
        
        return {
            "agents": agents,
            "statistics": stats,
            "total_agents": len(agents),
            "active_agents": len([a for a in agents if a["is_active"]]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")

@app.post("/coach/analyze", response_model=AgentResponse)
async def get_coaching_analysis(request: CoachingRequest):
    """Get coaching analysis and performance recommendations."""
    global agent_factory
    
    if not agent_factory:
        raise HTTPException(status_code=503, detail="Agent factory not initialized")
    
    try:
        # Process coaching request
        response = await agent_factory.process_user_message(
            agent_id="futmatrix_coach",
            user_id=request.user_id,
            message=request.message,
            context={"focus_areas": request.focus_areas}
        )
        
        if response["success"]:
            return AgentResponse(
                success=True,
                agent_id="futmatrix_coach",
                user_id=request.user_id,
                response=response.get("response", "Coaching analysis completed"),
                tokens_used=response.get("tokens_used", 0),
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Coaching analysis failed: {response.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/rivalizer/match", response_model=AgentResponse)
async def find_match_opponents(request: MatchmakingRequest):
    """Find competitive match opponents and strategic insights."""
    global agent_factory
    
    if not agent_factory:
        raise HTTPException(status_code=503, detail="Agent factory not initialized")
    
    try:
        # Process matchmaking request  
        response = await agent_factory.process_user_message(
            agent_id="futmatrix_rivalizer",
            user_id=request.user_id,
            message=request.message,
            context={
                "skill_level": request.skill_level,
                "playstyle": request.playstyle
            }
        )
        
        if response["success"]:
            return AgentResponse(
                success=True,
                agent_id="futmatrix_rivalizer",
                user_id=request.user_id,
                response=response.get("response", "Matchmaking analysis completed"),
                tokens_used=response.get("tokens_used", 0),
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Matchmaking failed: {response.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get detailed system statistics."""
    global agent_factory
    
    if not agent_factory:
        raise HTTPException(status_code=503, detail="Agent factory not initialized")
    
    try:
        stats = agent_factory.get_factory_stats()
        health = await agent_factory.health_check()
        
        return {
            "system_info": {
                "service": "Futmatrix AI Agents",
                "version": "1.0.0",
                "platform": "EA Sports FC 25",
                "factory_status": health["factory_status"],
                "openai_status": health["openai_integration"]["status"]
            },
            "agent_statistics": stats,
            "performance_metrics": {
                "total_agents": stats["total_agents"],
                "active_agents": stats["active_agents"],
                "openai_agents": stats["openai_agents"],
                "uptime": "operational"
            },
            "available_personalities": stats["available_personalities"],
            "available_domains": stats["available_domains"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

if __name__ == "__main__":
    print("🎮 Starting Futmatrix AI Agents API Server...")
    print("🏆 Coach Agent: Performance analysis and training optimization")
    print("⚔️ Rivalizer Agent: Competitive matchmaking and strategic insights")
    print("🚀 Server starting on http://0.0.0.0:5000")
    
    uvicorn.run(
        "api_server_futmatrix:app",
        host="0.0.0.0",
        port=5000,
        log_level="info",
        reload=False
    )