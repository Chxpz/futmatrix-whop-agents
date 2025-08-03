"""
REST API Server for AI Agents System
Provides API endpoints for frontend communication with intelligent agents
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
    description="REST API for intelligent AI agents with personality-specific responses",
    version="1.0.0",
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
        logger.info("Starting AI Agents API Server")
        
        # Initialize agent system
        agent_system = SimpleAgentSystem()
        await agent_system.initialize()
        
        logger.info("AI Agents API Server ready!")
        logger.info("Available endpoints:")
        logger.info("  GET  /                    - System info")
        logger.info("  GET  /health              - Health check")
        logger.info("  GET  /agents              - List agents")
        logger.info("  POST /agents/{agent_id}/chat - Chat with agent")
        logger.info("  POST /demo/test           - Test agents")
        logger.info("  GET  /docs                - API documentation")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger = logging.getLogger("api_shutdown")
    logger.info("AI Agents API Server shutdown")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "service": "AI Agents API",
        "status": "running",
        "version": "1.0.0",
        "description": "Backend API for intelligent AI agents with distinct personalities and business expertise",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_available": len(agent_system.agents) if agent_system else 0,
        "features": [
            "OpenAI-powered intelligent responses",
            "Personality-based agent behavior",
            "Business domain specialization", 
            "Conversation context management",
            "RESTful API interface"
        ],
        "endpoints": {
            "health": "/health",
            "agents_list": "/agents",
            "chat": "/agents/{agent_id}/chat",
            "demo": "/demo/test",
            "documentation": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
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
                    "specialization": agent.business_domain,
                    "personality_traits": agent.personality.get('traits', []),
                    "communication_style": agent.personality.get('tone', 'professional')
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
            "conversation_metadata": {
                "message_length": len(request.message),
                "response_length": len(response["response"]),
                "processing_time": "real-time",
                "context_used": bool(request.context)
            }
        }
        
        return enhanced_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/info")
async def get_agent_info(agent_id: str):
    """Get detailed information about a specific agent."""
    try:
        if not agent_system:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        if agent_id not in agent_system.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agent_system.agents[agent_id]
        
        return {
            "agent_id": agent_id,
            "personality": {
                "type": agent.personality_type,
                "description": agent.personality.get('description', ''),
                "traits": agent.personality.get('traits', []),
                "communication_style": agent.personality.get('tone', 'professional')
            },
            "business_domain": {
                "type": agent.business_domain,
                "description": agent.business_rules.domains.get(agent.business_domain, ''),
                "specializations": _get_business_specializations(agent.business_domain)
            },
            "capabilities": _get_agent_capabilities(agent_id),
            "example_conversations": _get_example_conversations(agent.business_domain),
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }
        
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
        
        return {
            "system_status": "operational",
            "agents": agents_info,
            "performance": {
                "total_conversations": sum(len(agent.conversations) for agent in agent_system.agents.values()),
                "active_users": len(set(user_id for agent in agent_system.agents.values() for user_id in agent.conversations.keys())),
                "openai_integration": "active"
            },
            "capabilities": {
                "personality_types": ["analytical", "creative"],
                "business_domains": ["financial_advisor", "content_creator"],
                "supported_features": [
                    "Real-time chat",
                    "Context-aware responses", 
                    "Personality-based behavior",
                    "Business domain expertise",
                    "Conversation memory"
                ]
            },
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
    return use_cases.get(business_domain, ["General assistance", "Q&A support"])

def _get_agent_capabilities(agent_id: str) -> dict:
    """Get capabilities for a specific agent."""
    return {
        "chat_endpoint": f"/agents/{agent_id}/chat",
        "info_endpoint": f"/agents/{agent_id}/info", 
        "real_time_responses": True,
        "context_awareness": True,
        "conversation_memory": True,
        "personality_consistency": True
    }

def _get_business_specializations(business_domain: str) -> list:
    """Get specializations for a business domain."""
    specializations = {
        "financial_advisor": [
            "Portfolio Management",
            "Risk Analysis", 
            "Investment Strategy",
            "Retirement Planning",
            "Market Research"
        ],
        "content_creator": [
            "Social Media Strategy",
            "Brand Development",
            "Creative Writing",
            "SEO Optimization",
            "Audience Analysis"
        ]
    }
    return specializations.get(business_domain, ["General Knowledge"])

def _get_example_conversations(business_domain: str) -> list:
    """Get example conversations for a business domain."""
    examples = {
        "financial_advisor": [
            {
                "user": "I want to start investing but I'm new to this. Where should I begin?",
                "response_type": "Educational guidance with risk assessment and beginner-friendly investment options"
            },
            {
                "user": "Should I invest in tech stocks or diversify more?",
                "response_type": "Portfolio analysis with diversification strategy recommendations"
            }
        ],
        "content_creator": [
            {
                "user": "I need viral content ideas for my startup's social media.",
                "response_type": "Creative content strategies tailored to startup marketing goals"
            },
            {
                "user": "How can I improve engagement on my Instagram posts?",
                "response_type": "Data-driven engagement optimization tips and creative suggestions"
            }
        ]
    }
    return examples.get(business_domain, [])

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "detail": str(exc.detail),
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error", 
            "detail": str(exc.detail),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )