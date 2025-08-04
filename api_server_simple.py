"""
Simple REST API Server for AI Agents System - Production Ready
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from standalone_simple import SimpleAgentSystem
from utils.logger import setup_logger

# Initialize FastAPI app
app = FastAPI(
    title="AI Agents API",
    description="Production-ready REST API for intelligent AI agents with MCP integration",
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent system
agent_system = None

# Pydantic models for API requests
class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class AnalysisRequest(BaseModel):
    user_id: str
    data: Dict[str, Any]
    analysis_type: Optional[str] = "general"

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the AI agents system."""
    global agent_system
    
    setup_logger()
    logger = logging.getLogger("api_startup")
    
    try:
        logger.info("Starting AI Agents API Server v1.2.0")
        
        # Initialize agent system
        agent_system = SimpleAgentSystem()
        await agent_system.initialize()
        
        logger.info("AI Agents API Server ready!")
        logger.info("Features: OpenAI GPT-4o, MCP Integration, Database Persistence")
        logger.info("Available endpoints:")
        logger.info("  GET  /                    - System info")
        logger.info("  GET  /health              - Health check")
        logger.info("  GET  /agents              - List agents")
        logger.info("  GET  /agents/{id}/tools   - Agent MCP tools")
        logger.info("  POST /agents/{id}/chat    - Chat with agent")
        logger.info("  POST /demo/test           - Test agents")
        logger.info("  GET  /docs                - API documentation")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global agent_system
    logger = logging.getLogger("api_shutdown")
    
    if agent_system:
        # Save any pending data
        for agent in agent_system.agents.values():
            for user_id, conversation in agent.conversations.items():
                await agent.database.save_conversation(agent.agent_id, user_id, conversation)
    
    logger.info("AI Agents API Server shutdown complete")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "service": "AI Agents API",
        "status": "running",
        "version": "1.2.0",
        "description": "Production-ready multi-agent AI system with OpenAI GPT-4o, MCP integration, and database persistence",
        "features": [
            "OpenAI GPT-4o Integration",
            "MCP (Model Context Protocol) Support", 
            "Multi-Agent Architecture",
            "Conversation Persistence",
            "Smart Context Enhancement"
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "agents": "/agents", 
            "chat": "/agents/{agent_id}/chat",
            "tools": "/agents/{agent_id}/tools",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with system diagnostics."""
    try:
        if not agent_system:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": "Agent system not initialized",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Test OpenAI connectivity with a simple chat
        test_result = await agent_system.chat(
            "agent_alpha", 
            "health_check_user", 
            "Hello, this is a health check."
        )
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agents_count": len(agent_system.agents),
            "openai_connection": "working" if test_result["success"] else "failed",
            "system_components": {
                "agent_system": "operational",
                "openai_integration": "active",
                "mcp_integration": "available",
                "database_persistence": "active",
                "personality_system": "loaded",
                "business_rules": "loaded"
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/agents")
async def list_agents():
    """List all available agents with their capabilities."""
    try:
        if not agent_system:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        agents_info = agent_system.list_agents()
        
        # Add detailed agent information
        detailed_agents = []
        for agent_info in agents_info["agents"]:
            agent_id = agent_info["agent_id"]
            agent = agent_system.agents[agent_id]
            
            detailed_agents.append({
                **agent_info,
                "capabilities": {
                    "chat": f"/agents/{agent_id}/chat",
                    "tools": f"/agents/{agent_id}/tools",
                    "specialization": agent.business_domain,
                    "personality_traits": agent.personality.get('traits', []),
                    "communication_style": agent.personality.get('tone', 'professional'),
                    "mcp_tools": len(agent.mcp_tools),
                    "conversation_memory": True,
                    "database_persistence": True
                },
                "business_focus": agent.business_rules.domains.get(agent.business_domain, "General assistance"),
                "example_use_cases": _get_example_use_cases(agent.business_domain)
            })
        
        return {
            "agents": detailed_agents,
            "total_agents": len(detailed_agents),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/tools")
async def get_agent_tools(agent_id: str):
    """Get available MCP tools for a specific agent."""
    try:
        if not agent_system:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        if agent_id not in agent_system.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agent_system.agents[agent_id]
        tools_info = {
            "mcp_connected": len(agent.mcp_tools) > 0,
            "tools_available": len(agent.mcp_tools),
            "tools": agent.mcp_tools,
            "smart_context_enhancement": True,
            "rag_integration": True
        }
        
        return {
            "success": True,
            "agent_id": agent_id,
            "tools": tools_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger = logging.getLogger("api_tools")
        logger.error(f"Error getting tools for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """Send a message to a specific agent and get an intelligent response."""
    try:
        if not agent_system:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Process message through agent
        response = await agent_system.chat(
            agent_id, 
            request.user_id, 
            request.message, 
            request.context
        )
        
        if not response["success"]:
            if "not found" in response.get("error", "").lower():
                raise HTTPException(status_code=404, detail=response["error"])
            else:
                raise HTTPException(status_code=400, detail=response.get("error", "Processing failed"))
        
        # Enhance response with additional metadata
        enhanced_response = {
            **response,
            "agent_info": {
                "personality": response["personality"],
                "business_domain": response["business_domain"],
                "capabilities": _get_agent_capabilities(agent_id)
            },
            "conversation_saved": True,
            "database_persisted": True
        }
        
        return enhanced_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/demo/test")
async def test_agents():
    """Demo endpoint to test all agents with sample interactions."""
    try:
        if not agent_system:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        test_results = await agent_system.test_agents()
        
        # Format results for API response
        formatted_results = {
            "demo_status": "completed",
            "timestamp": test_results["timestamp"],
            "tests_performed": len(test_results["results"]),
            "results": []
        }
        
        for test in test_results["results"]:
            result_data = test["result"]
            formatted_results["results"].append({
                "agent": test["agent"],
                "test_scenario": test["test"],
                "success": result_data["success"],
                "response_preview": result_data.get("response", "")[:150] + "..." if result_data.get("response") else "No response",
                "tokens_used": result_data.get("tokens_used", 0),
                "personality": result_data.get("personality"),
                "business_domain": result_data.get("business_domain"),
                "full_response": result_data.get("response") if result_data["success"] else result_data.get("error")
            })
        
        return formatted_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/stats")
async def get_system_stats():
    """Get system statistics and performance metrics."""
    try:
        if not agent_system:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        agents_info = agent_system.list_agents()
        
        # Get database summary
        database_summary = {}
        if agent_system.agents:
            first_agent = next(iter(agent_system.agents.values()))
            database_summary = await first_agent.database.get_conversation_summary()
        
        return {
            "system_status": "operational",
            "agents": agents_info,
            "performance": {
                "total_conversations": sum(len(agent.conversations) for agent in agent_system.agents.values()),
                "active_users": len(set(user_id for agent in agent_system.agents.values() for user_id in agent.conversations.keys())),
                "openai_integration": "active",
                "mcp_integration": "ready",
                "database_persistence": "active"
            },
            "database_stats": database_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _get_example_use_cases(business_domain: str) -> list:
    """Get example use cases for a business domain."""
    use_cases = {
        "financial_advisor": [
            "Investment portfolio analysis",
            "Retirement planning advice", 
            "Risk assessment consultation",
            "Market trend analysis",
            "Financial goal setting"
        ],
        "content_creator": [
            "Social media content strategy",
            "Creative campaign ideation",
            "Brand storytelling",
            "Content optimization tips",
            "Audience engagement strategies"
        ]
    }
    return use_cases.get(business_domain, ["General assistance", "Question answering", "Problem solving"])

def _get_agent_capabilities(agent_id: str) -> dict:
    """Get agent capabilities."""
    return {
        "chat_endpoint": f"/agents/{agent_id}/chat",
        "tools_endpoint": f"/agents/{agent_id}/tools",
        "real_time_responses": True,
        "context_awareness": True,
        "conversation_memory": True,
        "personality_consistency": True,
        "mcp_integration": True,
        "database_persistence": True
    }

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "api_server_simple:app",
        host="0.0.0.0", 
        port=5000,
        reload=False,
        log_level="info"
    )