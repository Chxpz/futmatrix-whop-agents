"""
Standalone AI Agents System - Works without Docker
Fully functional backend with OpenAI integration and REST API endpoints
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import Settings
from agents.agent_factory import AgentFactory
from core.openai_integration import OpenAIIntegrationManager
from core.security import SecurityManager
from core.monitoring import MonitoringManager
from utils.logger import setup_logger
from utils.exceptions import AgentFactoryError, LLMError

# Initialize FastAPI app
app = FastAPI(
    title="AI Agents System",
    description="Production-ready AI agents with OpenAI integration",
    version="1.0.0"
)

# Global managers
settings = Settings()
agent_factory = None
security_manager = None
monitoring_manager = None

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the AI agents system."""
    global agent_factory, security_manager, monitoring_manager
    
    setup_logger()
    logger = logging.getLogger("startup")
    
    try:
        logger.info("Starting AI Agents System (Standalone Mode)")
        
        # Enable test mode for standalone operation
        settings.DATABASE_CONFIG["test_mode"] = True
        
        # Initialize security manager
        security_manager = SecurityManager(settings)
        logger.info("Security manager initialized")
        
        # Initialize monitoring
        monitoring_manager = MonitoringManager(settings)
        await monitoring_manager.start_monitoring()
        logger.info("Monitoring system started")
        
        # Initialize agent factory with OpenAI
        agent_factory = AgentFactory(settings)
        await agent_factory.initialize()
        logger.info("Agent factory initialized with OpenAI integration")
        
        # Create default agents
        from agents.agent_factory import create_default_agents
        created_agents = await create_default_agents(agent_factory)
        logger.info(f"Created default agents: {created_agents}")
        
        # Initialize and start agents
        await agent_factory.initialize_all_agents()
        await agent_factory.start_all_agents()
        
        logger.info("AI Agents System startup complete!")
        logger.info("API endpoints available at: http://localhost:5000")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global agent_factory, monitoring_manager
    
    logger = logging.getLogger("shutdown")
    
    try:
        if agent_factory:
            await agent_factory.stop_all_agents()
        
        if monitoring_manager:
            await monitoring_manager.stop_monitoring()
        
        logger.info("AI Agents System shutdown complete")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "service": "AI Agents System",
        "status": "running",
        "mode": "standalone",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "agents": "/api/agents",
            "chat": "/api/agents/{agent_id}/chat",
            "analysis": "/api/agents/{agent_id}/analysis",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        if not agent_factory or not monitoring_manager:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": "System not initialized"}
            )
        
        # Get system health status
        health_status = await monitoring_manager.get_health_summary()
        
        # Get agent factory health
        factory_health = await agent_factory.health_check()
        
        return {
            "status": health_status.get("overall_status", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "system": health_status,
            "agents": factory_health,
            "mode": "standalone"
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

@app.get("/api/agents")
async def list_agents():
    """List all available agents."""
    try:
        if not agent_factory:
            raise HTTPException(status_code=503, detail="Agent factory not initialized")
        
        agents = agent_factory.list_agents()
        stats = agent_factory.get_factory_stats()
        
        return {
            "agents": agents,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, request: Request):
    """Send message to specific agent and get intelligent response."""
    try:
        if not agent_factory:
            raise HTTPException(status_code=503, detail="Agent factory not initialized")
        
        # Parse request body
        body = await request.json()
        user_id = body.get("user_id", "anonymous")
        message = body.get("message", "")
        context = body.get("context", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Record request metrics
        start_time = datetime.utcnow()
        
        # Process message through agent
        response = await agent_factory.process_user_message(
            agent_id, user_id, message, context
        )
        
        # Record metrics
        if monitoring_manager:
            process_time = (datetime.utcnow() - start_time).total_seconds()
            monitoring_manager.record_api_request(
                f"/api/agents/{agent_id}/chat", 
                process_time, 
                response.get("success", False)
            )
        
        if not response.get("success"):
            raise HTTPException(status_code=400, detail=response.get("error", "Processing failed"))
        
        return {
            "success": True,
            "agent_id": agent_id,
            "user_id": user_id,
            "response": response["response"],
            "metadata": {
                "personality": response.get("personality"),
                "business_domain": response.get("business_domain"),
                "tokens_used": response.get("tokens_used", 0),
                "model": response.get("model", "unknown")
            },
            "timestamp": response.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/{agent_id}/analysis")
async def generate_analysis(agent_id: str, request: Request):
    """Generate business analysis using specific agent."""
    try:
        if not agent_factory:
            raise HTTPException(status_code=503, detail="Agent factory not initialized")
        
        # Parse request body
        body = await request.json()
        user_id = body.get("user_id", "anonymous")
        data = body.get("data", {})
        
        if not data:
            raise HTTPException(status_code=400, detail="Analysis data cannot be empty")
        
        # Generate analysis
        response = await agent_factory.generate_business_analysis(agent_id, user_id, data)
        
        if not response.get("success"):
            raise HTTPException(status_code=400, detail=response.get("error", "Analysis failed"))
        
        return {
            "success": True,
            "agent_id": agent_id,
            "user_id": user_id,
            "analysis": response["analysis"],
            "analysis_type": response.get("analysis_type"),
            "data_analyzed": response.get("data_analyzed"),
            "tokens_used": response.get("tokens_used", 0),
            "timestamp": response.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}/conversation/{user_id}")
async def get_conversation_summary(agent_id: str, user_id: str):
    """Get conversation summary for user with specific agent."""
    try:
        if not agent_factory:
            raise HTTPException(status_code=503, detail="Agent factory not initialized")
        
        summary = agent_factory.get_conversation_summary(agent_id, user_id)
        
        return {
            "agent_id": agent_id,
            "user_id": user_id,
            "conversation_summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/agents/{agent_id}/conversation/{user_id}")
async def clear_conversation(agent_id: str, user_id: str):
    """Clear conversation history for user with specific agent."""
    try:
        if not agent_factory:
            raise HTTPException(status_code=503, detail="Agent factory not initialized")
        
        success = agent_factory.clear_conversation(agent_id, user_id)
        
        return {
            "success": success,
            "agent_id": agent_id,
            "user_id": user_id,
            "message": "Conversation cleared" if success else "Agent not found",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/stats")
async def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        stats = {}
        
        if agent_factory:
            stats["agents"] = agent_factory.get_factory_stats()
        
        if monitoring_manager:
            stats["system"] = await monitoring_manager.get_system_status()
        
        stats["timestamp"] = datetime.utcnow().isoformat()
        stats["mode"] = "standalone"
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/test-agent")
async def test_agent_demo():
    """Demo endpoint to test agent functionality."""
    try:
        if not agent_factory:
            raise HTTPException(status_code=503, detail="Agent factory not initialized")
        
        # Test both agents with different messages
        test_results = []
        
        # Test financial advisor
        financial_response = await agent_factory.process_user_message(
            "agent_alpha", 
            "demo_user", 
            "I have $10,000 to invest and I'm 30 years old. What should I do?",
            {"risk_tolerance": "moderate", "investment_horizon": "long-term"}
        )
        test_results.append({
            "agent": "agent_alpha (Financial Advisor)",
            "test": "Investment advice",
            "response": financial_response
        })
        
        # Test content creator
        content_response = await agent_factory.process_user_message(
            "agent_beta",
            "demo_user",
            "I need to create engaging social media content for a tech startup. Any ideas?",
            {"platform": "linkedin", "audience": "tech professionals"}
        )
        test_results.append({
            "agent": "agent_beta (Content Creator)",
            "test": "Content strategy",
            "response": content_response
        })
        
        return {
            "demo_status": "completed",
            "tests_run": len(test_results),
            "results": test_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "AI service temporarily unavailable",
            "details": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(AgentFactoryError)
async def agent_error_handler(request: Request, exc: AgentFactoryError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Agent operation failed",
            "details": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    # Run the standalone system
    uvicorn.run(
        "standalone_main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )