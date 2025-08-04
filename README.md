# AI Agents System - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [System Architecture](#system-architecture)
4. [API Documentation](#api-documentation)
5. [Agent Configuration](#agent-configuration)
6. [Development Guide](#development-guide)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

## Overview

The AI Agents System is a production-ready, multi-agent AI platform that creates and manages intelligent AI agents with distinct personalities and business specializations. The system provides a comprehensive REST API for frontend integration and supports real-time interactions with OpenAI-powered agents.

### Key Features

- **Multi-Agent Architecture**: Deploy multiple AI agents with different personalities and business domains
- **OpenAI Integration**: Powered by GPT-4o for intelligent, context-aware responses
- **REST API**: Comprehensive API endpoints for frontend integration
- **Personality System**: Analytical, creative, and professional personality types
- **Business Specialization**: Financial advisor, content creator, technical support domains
- **Real-time Communication**: WebSocket support for live interactions
- **Conversation Memory**: Context-aware conversations with message history
- **Scalable Design**: Modular architecture with graceful degradation

### Current Agents

- **Agent Alpha** (`agent_alpha`): Analytical Financial Advisor
  - Personality: Data-driven, systematic, evidence-based
  - Specialization: Investment advice, portfolio analysis, financial planning
  
- **Agent Beta** (`agent_beta`): Creative Content Creator
  - Personality: Innovative, imaginative, inspirational
  - Specialization: Social media strategy, brand development, creative campaigns

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API Key
- Replit environment (recommended) or local Python environment

### Installation & Setup

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd ai-agents-system
   ```

2. **Environment Variables**:
   Set your OpenAI API key in Replit secrets or environment:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the System**:
   ```bash
   python api_server.py
   ```

4. **Verify Installation**:
   ```bash
   curl http://localhost:5000/health
   ```

### First API Call

Test the financial advisor agent:
```bash
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I have $10,000 to invest. What do you recommend?",
    "context": {"risk_tolerance": "moderate"}
  }'
```

## System Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   REST API       │    │   AI Agents     │
│   Application   │◄──►│   (FastAPI)      │◄──►│   System        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   OpenAI API     │    │   Personality   │
                       │   Integration    │    │   & Business    │
                       └──────────────────┘    │   Rules Engine  │
                                              └─────────────────┘
```

### Directory Structure

```
ai-agents-system/
├── agents/                 # Agent management and configuration
│   ├── agent_factory.py   # Agent creation and management
│   ├── business_rules.py  # Business domain logic
│   └── personalities.py   # Personality definitions
├── api/                   # API layer
│   └── rest_api.py       # FastAPI endpoints (alternative)
├── core/                  # Core system components
│   ├── openai_integration.py  # OpenAI API client
│   ├── database.py        # Database management
│   ├── security.py        # Authentication & security
│   ├── monitoring.py      # System monitoring
│   └── workflow.py        # Agent workflow processing
├── config/               # Configuration management
│   └── settings.py       # Environment settings
├── utils/                # Utilities
│   ├── exceptions.py     # Custom exceptions
│   └── logger.py         # Logging configuration
├── tests/                # Test suite
├── api_server.py         # Main API server
├── standalone_simple.py  # Simplified standalone implementation
└── replit.md            # System documentation
```

### Data Flow

1. **Request Processing**:
   ```
   Client Request → FastAPI Router → Agent Selection → Message Processing
   ```

2. **Agent Processing**:
   ```
   User Message → Personality Filter → Business Rules → OpenAI API → Response Generation
   ```

3. **Response Delivery**:
   ```
   Generated Response → Context Storage → API Response → Client
   ```

## API Documentation

### Base URL
```
http://localhost:5000
```

### Authentication
Currently, the system operates without authentication for development. For production deployment, implement authentication using the SecurityManager component.

### Core Endpoints

#### System Information

**GET /** - System overview
```json
{
  "service": "AI Agents API",
  "status": "running",
  "version": "1.0.0",
  "agents_available": 2,
  "features": [
    "OpenAI-powered intelligent responses",
    "Personality-based agent behavior",
    "Business domain specialization"
  ]
}
```

**GET /health** - Health check
```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T16:32:26.614Z",
  "agents_count": 2,
  "openai_connection": "working",
  "system_components": {
    "agent_system": "operational",
    "openai_integration": "active"
  }
}
```

#### Agent Management

**GET /agents** - List all agents
```json
{
  "agents": [
    {
      "agent_id": "agent_alpha",
      "personality": "analytical",
      "business_domain": "financial_advisor",
      "status": "active",
      "capabilities": {
        "chat": "/agents/agent_alpha/chat",
        "specialization": "financial_advisor",
        "personality_traits": ["analytical", "data-driven", "logical-reasoning"],
        "communication_style": "professional"
      },
      "example_use_cases": [
        "Investment portfolio analysis",
        "Retirement planning advice",
        "Risk assessment consultation"
      ]
    }
  ],
  "total_agents": 2
}
```

**GET /agents/{agent_id}/info** - Agent details
```json
{
  "agent_id": "agent_alpha",
  "personality": {
    "type": "analytical",
    "description": "Data-driven analysis and systematic approach",
    "traits": ["analytical", "systematic", "evidence-based"],
    "communication_style": "professional"
  },
  "business_domain": {
    "type": "financial_advisor",
    "description": "Financial advisory and investment management",
    "specializations": ["Portfolio Management", "Risk Analysis"]
  },
  "status": "active"
}
```

#### Chat Interface

**POST /agents/{agent_id}/chat** - Chat with an agent

Request:
```json
{
  "user_id": "string",
  "message": "string",
  "context": {
    "key": "value"
  }
}
```

Response:
```json
{
  "success": true,
  "agent_id": "agent_alpha",
  "user_id": "user123",
  "response": "Based on your moderate risk tolerance and $10,000 investment...",
  "personality": "analytical",
  "business_domain": "financial_advisor",
  "timestamp": "2025-08-04T16:32:26.614Z",
  "tokens_used": 450,
  "agent_info": {
    "personality": "analytical",
    "business_domain": "financial_advisor",
    "capabilities": {
      "real_time_responses": true,
      "context_awareness": true,
      "conversation_memory": true
    }
  },
  "conversation_metadata": {
    "message_length": 45,
    "response_length": 1200,
    "processing_time": "real-time",
    "context_used": true
  }
}
```

#### Testing & Demo

**POST /demo/test** - Test all agents
```json
{
  "demo_status": "completed",
  "timestamp": "2025-08-04T16:32:26.614Z",
  "tests_performed": 2,
  "results": [
    {
      "agent": "agent_alpha (Financial Advisor)",
      "test_scenario": "Investment consultation",
      "success": true,
      "response_preview": "Given your age of 35 and a long-term investment...",
      "tokens_used": 650,
      "full_response": "Complete response text..."
    }
  ]
}
```

**GET /system/stats** - System statistics
```json
{
  "system_status": "operational",
  "agents": {
    "total_agents": 2,
    "active_agents": 2
  },
  "performance": {
    "total_conversations": 150,
    "active_users": 25,
    "openai_integration": "active"
  },
  "capabilities": {
    "personality_types": ["analytical", "creative"],
    "business_domains": ["financial_advisor", "content_creator"],
    "supported_features": [
      "Real-time chat",
      "Context-aware responses",
      "Personality-based behavior"
    ]
  }
}
```

### Error Responses

All endpoints return structured error responses:

```json
{
  "error": "Resource not found",
  "detail": "Agent agent_gamma not found",
  "path": "/agents/agent_gamma/chat",
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (agent doesn't exist)
- `500`: Internal Server Error
- `503`: Service Unavailable (system not initialized)

## Agent Configuration

### Personality Types

#### Analytical
- **Traits**: Data-driven, systematic, logical-reasoning, evidence-based
- **Communication**: Professional, structured, fact-based
- **Best for**: Financial advice, technical analysis, research

#### Creative
- **Traits**: Innovative, imaginative, inspirational, artistic-expression
- **Communication**: Enthusiastic, engaging, idea-focused
- **Best for**: Content creation, marketing, brainstorming

### Business Domains

#### Financial Advisor
- **Specializations**: Portfolio management, risk analysis, investment strategy
- **Use cases**: Investment advice, retirement planning, financial goal setting
- **Context awareness**: Risk tolerance, time horizon, financial goals

#### Content Creator
- **Specializations**: Social media strategy, brand development, creative campaigns
- **Use cases**: Content ideation, audience engagement, brand storytelling
- **Context awareness**: Platform, target audience, brand voice

### Creating Custom Agents

To add a new agent, modify `agents/agent_factory.py`:

```python
# Add to default agents configuration
agents_config = [
    {
        "agent_id": "agent_gamma",
        "personality": "professional", 
        "domain": "technical_support"
    }
]
```

Add personality in `agents/personalities.py`:
```python
"professional": {
    "description": "Professional and solution-oriented approach",
    "traits": ["helpful", "systematic", "problem-solving"],
    "tone": "professional and supportive"
}
```

Add business domain in `agents/business_rules.py`:
```python
"technical_support": "Technical support and troubleshooting assistance"
```

## Development Guide

### Setting Up Development Environment

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn openai pydantic aiohttp
   ```

2. **Environment Configuration**:
   Create `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   LOG_LEVEL=DEBUG
   API_PORT=5000
   ```

3. **Run Development Server**:
   ```bash
   uvicorn api_server:app --reload --host 0.0.0.0 --port 5000
   ```

### Code Structure

#### Adding New Endpoints

1. **Define endpoint in `api_server.py`**:
   ```python
   @app.get("/new-endpoint")
   async def new_endpoint():
       return {"message": "New endpoint"}
   ```

2. **Add business logic in appropriate module**:
   - Agent logic: `agents/`
   - Core functionality: `core/`
   - Utilities: `utils/`

#### Error Handling

Use custom exceptions from `utils/exceptions.py`:
```python
from utils.exceptions import AgentError

try:
    # Agent operation
    pass
except Exception as e:
    raise AgentError(f"Operation failed: {e}")
```

#### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Operation started")
logger.error(f"Operation failed: {error}")
```

### Testing

Run the test suite:
```bash
pytest tests/
```

Test specific components:
```bash
pytest tests/test_agent_core.py -v
```

Create integration tests:
```python
async def test_agent_chat():
    system = SimpleAgentSystem()
    await system.initialize()
    
    response = await system.chat(
        "agent_alpha", 
        "test_user", 
        "Test message"
    )
    
    assert response["success"] == True
    assert "response" in response
```

## Deployment

### Replit Deployment (Recommended)

1. **Configure Secrets**:
   - Add `OPENAI_API_KEY` in Replit Secrets

2. **Configure Replit Run Command**:
   ```bash
   python api_server.py
   ```

3. **Port Configuration**:
   The system automatically uses port 5000, which is accessible in Replit.

### Local Deployment

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export OPENAI_API_KEY="your_key_here"
   ```

3. **Run Server**:
   ```bash
   python api_server.py
   ```

### Production Deployment

1. **Security Configuration**:
   - Enable authentication in `core/security.py`
   - Configure CORS for specific domains
   - Set up API rate limiting

2. **Monitoring**:
   - Enable system monitoring in `core/monitoring.py`
   - Set up log aggregation
   - Configure health check endpoints

3. **Scaling**:
   - Use load balancer for multiple instances
   - Configure database connection pooling
   - Implement caching layer

## Troubleshooting

### Common Issues

#### 1. OpenAI API Key Issues
**Error**: `Authentication failed`
**Solution**: 
- Verify API key is set correctly
- Check API key permissions and billing
- Test with curl: `curl -H "Authorization: Bearer your_key" https://api.openai.com/v1/models`

#### 2. Agent Not Responding
**Error**: `Agent not found` or timeout
**Solution**:
- Check agent initialization in logs
- Verify agent_id matches available agents
- Test with `/agents` endpoint to list available agents

#### 3. Port Already in Use
**Error**: `Port 5000 already in use`
**Solution**:
- Kill existing process: `pkill -f api_server.py`
- Use different port: Set `PORT` environment variable
- Check running processes: `lsof -i :5000`

#### 4. Memory Issues
**Error**: Out of memory or slow responses
**Solution**:
- Monitor conversation history size
- Implement conversation cleanup
- Reduce max_tokens in OpenAI calls

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check system health:
```bash
curl http://localhost:5000/health
curl http://localhost:5000/system/stats
```

### Performance Optimization

1. **Response Time**:
   - Use async/await for all I/O operations
   - Implement response caching
   - Optimize OpenAI API calls

2. **Memory Usage**:
   - Limit conversation history
   - Implement session cleanup
   - Monitor agent state size

3. **Scalability**:
   - Use connection pooling
   - Implement load balancing
   - Cache frequently accessed data

## Contributing

### Development Workflow

1. **Fork and Clone**:
   ```bash
   git clone <your-fork-url>
   cd ai-agents-system
   ```

2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-agent-type
   ```

3. **Make Changes**:
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

4. **Test Changes**:
   ```bash
   pytest tests/
   python api_server.py  # Manual testing
   ```

5. **Submit Pull Request**:
   - Describe changes clearly
   - Include test results
   - Update documentation

### Code Standards

- **Python Style**: Follow PEP 8
- **Type Hints**: Use type annotations
- **Documentation**: Add docstrings to all functions
- **Error Handling**: Use custom exceptions
- **Logging**: Add appropriate log levels

### Adding New Features

1. **New Agent Personality**:
   - Add to `agents/personalities.py`
   - Update `agents/agent_factory.py`
   - Add tests in `tests/test_personalities.py`

2. **New Business Domain**:
   - Add to `agents/business_rules.py`
   - Create domain-specific logic
   - Add integration tests

3. **New API Endpoints**:
   - Add to `api_server.py`
   - Follow RESTful conventions
   - Add error handling and documentation

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review system logs
- Test with health endpoints
- Contact the development team

---

*Last updated: August 4, 2025*