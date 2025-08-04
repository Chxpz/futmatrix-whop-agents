# AI Agents System - API Reference

## Overview

The AI Agents API provides RESTful endpoints for interacting with intelligent AI agents. Each agent has unique personalities and business specializations, powered by OpenAI's GPT-4o model.

## Base Information

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`
- **Response Format**: JSON
- **Current Version**: 1.0.0

## Authentication

The system currently operates without authentication for development purposes. For production deployment, implement JWT-based authentication using the SecurityManager component.

## Rate Limiting

No rate limiting is currently implemented. For production, implement rate limiting based on user_id or IP address.

## Error Handling

All endpoints return structured error responses with appropriate HTTP status codes:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "path": "/requested/path",
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: System not initialized

## Endpoints

### System Endpoints

#### GET /

Get system information and overview.

**Response:**
```json
{
  "service": "AI Agents API",
  "status": "running",
  "version": "1.0.0",
  "description": "Backend API for intelligent AI agents with distinct personalities and business expertise",
  "timestamp": "2025-08-04T16:32:26.614Z",
  "agents_available": 2,
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
```

#### GET /health

Check system health and component status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T16:32:26.614Z",
  "agents_count": 2,
  "openai_connection": "working",
  "system_components": {
    "agent_system": "operational",
    "openai_integration": "active",
    "personality_system": "loaded",
    "business_rules": "loaded"
  }
}
```

**Error Response (503):**
```json
{
  "status": "unhealthy",
  "error": "Agent system not initialized",
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

#### GET /system/stats

Get detailed system statistics and performance metrics.

**Response:**
```json
{
  "system_status": "operational",
  "agents": {
    "agents": [
      {
        "agent_id": "agent_alpha",
        "personality": "analytical",
        "business_domain": "financial_advisor",
        "status": "active"
      }
    ],
    "total_agents": 2
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
      "Personality-based behavior",
      "Business domain expertise",
      "Conversation memory"
    ]
  },
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

### Agent Management Endpoints

#### GET /agents

List all available agents with their capabilities and information.

**Response:**
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
        "personality_traits": [
          "analytical",
          "data-driven",
          "logical-reasoning",
          "systematic-approach",
          "evidence-based-conclusions",
          "statistical-analysis-focus"
        ],
        "communication_style": "professional"
      },
      "business_focus": "Financial advisory and investment management",
      "example_use_cases": [
        "Investment portfolio analysis",
        "Retirement planning advice",
        "Risk assessment consultation",
        "Market trend analysis",
        "Financial goal setting"
      ]
    },
    {
      "agent_id": "agent_beta",
      "personality": "creative",
      "business_domain": "content_creator",
      "status": "active",
      "capabilities": {
        "chat": "/agents/agent_beta/chat",
        "specialization": "content_creator",
        "personality_traits": [
          "innovative",
          "imaginative",
          "creative-thinking",
          "artistic-expression",
          "out-of-the-box-ideas",
          "inspirational-approach"
        ],
        "communication_style": "enthusiastic"
      },
      "business_focus": "Content creation and marketing assistance",
      "example_use_cases": [
        "Social media content strategy",
        "Creative campaign ideation",
        "Brand storytelling",
        "Content optimization tips",
        "Audience engagement strategies"
      ]
    }
  ],
  "total_agents": 2,
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

#### GET /agents/{agent_id}/info

Get detailed information about a specific agent.

**Parameters:**
- `agent_id` (path): The ID of the agent (e.g., "agent_alpha", "agent_beta")

**Response:**
```json
{
  "agent_id": "agent_alpha",
  "personality": {
    "type": "analytical",
    "description": "Data-driven analysis with systematic approach to problem-solving",
    "traits": [
      "analytical",
      "data-driven",
      "logical-reasoning",
      "systematic-approach",
      "evidence-based-conclusions"
    ],
    "communication_style": "professional"
  },
  "business_domain": {
    "type": "financial_advisor",
    "description": "Financial advisory and investment management",
    "specializations": [
      "Portfolio Management",
      "Risk Analysis",
      "Investment Strategy",
      "Retirement Planning",
      "Market Research"
    ]
  },
  "capabilities": {
    "chat_endpoint": "/agents/agent_alpha/chat",
    "info_endpoint": "/agents/agent_alpha/info",
    "real_time_responses": true,
    "context_awareness": true,
    "conversation_memory": true,
    "personality_consistency": true
  },
  "example_conversations": [
    {
      "user": "I want to start investing but I'm new to this. Where should I begin?",
      "response_type": "Educational guidance with risk assessment and beginner-friendly investment options"
    },
    {
      "user": "Should I invest in tech stocks or diversify more?",
      "response_type": "Portfolio analysis with diversification strategy recommendations"
    }
  ],
  "status": "active",
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

#### GET /agents/{agent_id}/tools

Get available MCP tools and external integrations for a specific agent.

**Parameters:**
- `agent_id` (path): The ID of the agent (e.g., "agent_alpha", "agent_beta")

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_alpha",
  "tools": {
    "mcp_connected": true,
    "servers_connected": 2,
    "tools_available": 5,
    "tools": [
      {
        "name": "financial_data_search",
        "description": "Search for current financial market data and stock prices",
        "server": "https://financial-mcp.example.com"
      },
      {
        "name": "rag_query",
        "description": "Query knowledge base for relevant information",
        "server": "https://knowledge-mcp.example.com"
      }
    ]
  },
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

**Error Response (404):**
```json
{
  "error": "Resource not found",
  "detail": "Agent agent_gamma not found",
  "path": "/agents/agent_gamma/info",
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

### Chat Endpoints

#### POST /agents/{agent_id}/chat

Send a message to a specific agent and receive an intelligent response.

**Parameters:**
- `agent_id` (path): The ID of the agent to chat with

**Request Body:**
```json
{
  "user_id": "string",           // Required: Unique identifier for the user
  "message": "string",           // Required: The message to send to the agent
  "context": {                   // Optional: Additional context for the conversation
    "key": "value"
  }
}
```

**Example Request:**
```json
{
  "user_id": "user_12345",
  "message": "I have $50,000 to invest and I'm 35 years old. What investment strategy would you recommend?",
  "context": {
    "risk_tolerance": "moderate",
    "time_horizon": "long-term",
    "investment_experience": "beginner"
  }
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_alpha",
  "user_id": "user_12345",
  "response": "Given your age of 35 and a long investment timeline of over 10 years, you have a significant opportunity to capitalize on compound growth. With a moderate risk tolerance, a balanced approach that combines growth potential with some level of stability would be appropriate...",
  "personality": "analytical",
  "business_domain": "financial_advisor",
  "timestamp": "2025-08-04T16:32:26.614Z",
  "tokens_used": 610,
  "agent_info": {
    "personality": "analytical",
    "business_domain": "financial_advisor",
    "capabilities": {
      "chat_endpoint": "/agents/agent_alpha/chat",
      "info_endpoint": "/agents/agent_alpha/info",
      "real_time_responses": true,
      "context_awareness": true,
      "conversation_memory": true,
      "personality_consistency": true
    }
  },
  "conversation_metadata": {
    "message_length": 93,
    "response_length": 2134,
    "processing_time": "real-time",
    "context_used": true
  }
}
```

**Error Responses:**

400 Bad Request - Empty message:
```json
{
  "error": "Bad Request",
  "detail": "Message cannot be empty",
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

404 Not Found - Agent doesn't exist:
```json
{
  "success": false,
  "error": "Agent agent_gamma not found",
  "available_agents": ["agent_alpha", "agent_beta"]
}
```

500 Internal Server Error - Processing failed:
```json
{
  "success": false,
  "agent_id": "agent_alpha",
  "user_id": "user_12345",
  "error": "OpenAI API error: Rate limit exceeded",
  "timestamp": "2025-08-04T16:32:26.614Z"
}
```

### Demo and Testing Endpoints

#### POST /demo/test

Run comprehensive tests on all agents with predefined scenarios.

**Response:**
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
      "response_preview": "Given your age of 35 and a long-term investment horizon, you have the advantage of time on your side...",
      "tokens_used": 652,
      "personality": "analytical",
      "business_domain": "financial_advisor",
      "full_response": "Given your age of 35 and a long-term investment horizon, you have the advantage of time on your side, which allows you to potentially take on more risk for higher returns..."
    },
    {
      "agent": "agent_beta (Content Creator)",
      "test_scenario": "Content strategy",
      "success": true,
      "response_preview": "Creating viral content for a sustainable fashion brand on Instagram is a fantastic opportunity to blend creativity with purpose...",
      "tokens_used": 643,
      "personality": "creative",
      "business_domain": "content_creator",
      "full_response": "Creating viral content for a sustainable fashion brand on Instagram is a fantastic opportunity to blend creativity with purpose..."
    }
  ]
}
```

## Agent Specifications

### Agent Alpha - Financial Advisor

**Agent ID**: `agent_alpha`
**Personality**: Analytical
**Business Domain**: Financial Advisor

**Characteristics:**
- Data-driven decision making
- Systematic approach to analysis
- Evidence-based recommendations
- Professional communication style
- Focus on risk assessment and long-term planning

**Typical Use Cases:**
- Investment portfolio analysis
- Retirement planning advice
- Risk assessment consultation
- Market trend analysis
- Financial goal setting and tracking

**Context Parameters:**
- `risk_tolerance`: "conservative", "moderate", "aggressive"
- `time_horizon`: "short-term", "medium-term", "long-term"
- `investment_experience`: "beginner", "intermediate", "experienced"
- `financial_goals`: Array of goals
- `current_age`: Number
- `investment_amount`: Number

### Agent Beta - Content Creator

**Agent ID**: `agent_beta`
**Personality**: Creative
**Business Domain**: Content Creator

**Characteristics:**
- Innovative and imaginative approach
- Creative thinking and brainstorming
- Inspirational communication style
- Focus on engagement and viral potential
- Brand-aware content strategies

**Typical Use Cases:**
- Social media content strategy
- Creative campaign ideation
- Brand storytelling development
- Content optimization tips
- Audience engagement strategies

**Context Parameters:**
- `platform`: "instagram", "twitter", "tiktok", "linkedin", etc.
- `target_audience`: "gen_z", "millennials", "professionals", etc.
- `brand_focus`: "sustainability", "tech", "fashion", etc.
- `content_type`: "video", "image", "text", "story"
- `campaign_goal`: "awareness", "engagement", "conversion"

## Response Formats

### Successful Chat Response

```json
{
  "success": true,
  "agent_id": "string",
  "user_id": "string", 
  "response": "string",
  "personality": "string",
  "business_domain": "string",
  "timestamp": "ISO 8601 datetime",
  "tokens_used": number,
  "agent_info": {
    "personality": "string",
    "business_domain": "string",
    "capabilities": {
      "chat_endpoint": "string",
      "info_endpoint": "string",
      "real_time_responses": boolean,
      "context_awareness": boolean,
      "conversation_memory": boolean,
      "personality_consistency": boolean
    }
  },
  "conversation_metadata": {
    "message_length": number,
    "response_length": number,
    "processing_time": "string",
    "context_used": boolean
  }
}
```

### Error Response

```json
{
  "success": false,
  "agent_id": "string",
  "user_id": "string",
  "error": "string",
  "timestamp": "ISO 8601 datetime"
}
```

## SDK Examples

### JavaScript/TypeScript

```javascript
class AIAgentsClient {
  constructor(baseUrl = 'http://localhost:5000') {
    this.baseUrl = baseUrl;
  }

  async chatWithAgent(agentId, userId, message, context = null) {
    const response = await fetch(`${this.baseUrl}/agents/${agentId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message: message,
        context: context
      })
    });

    return await response.json();
  }

  async getAgents() {
    const response = await fetch(`${this.baseUrl}/agents`);
    return await response.json();
  }

  async getSystemHealth() {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }
}

// Usage
const client = new AIAgentsClient();

const response = await client.chatWithAgent(
  'agent_alpha',
  'user123',
  'I want to invest $10,000. What do you recommend?',
  { risk_tolerance: 'moderate' }
);

console.log(response.response);
```

### Python

```python
import requests
import json

class AIAgentsClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def chat_with_agent(self, agent_id, user_id, message, context=None):
        url = f"{self.base_url}/agents/{agent_id}/chat"
        payload = {
            "user_id": user_id,
            "message": message,
            "context": context
        }
        
        response = requests.post(url, json=payload)
        return response.json()

    def get_agents(self):
        url = f"{self.base_url}/agents"
        response = requests.get(url)
        return response.json()

    def get_system_health(self):
        url = f"{self.base_url}/health"
        response = requests.get(url)
        return response.json()

# Usage
client = AIAgentsClient()

response = client.chat_with_agent(
    'agent_alpha',
    'user123', 
    'I want to invest $10,000. What do you recommend?',
    {'risk_tolerance': 'moderate'}
)

print(response['response'])
```

### cURL Examples

```bash
# List all agents
curl -X GET http://localhost:5000/agents

# Chat with financial advisor
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I have $25,000 to invest. What strategy do you recommend?",
    "context": {
      "risk_tolerance": "moderate",
      "time_horizon": "long-term"
    }
  }'

# Chat with content creator
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "content_user",
    "message": "I need viral content ideas for my sustainable fashion brand",
    "context": {
      "platform": "instagram",
      "target_audience": "gen_z"
    }
  }'

# Check system health
curl -X GET http://localhost:5000/health

# Run demo tests
curl -X POST http://localhost:5000/demo/test
```

## Webhooks (Future)

Webhooks will be available in future versions for real-time notifications:

- Agent response ready
- System health changes
- Error notifications
- Usage threshold alerts

## Rate Limits (Production)

For production deployment, implement these rate limits:

- **Chat endpoints**: 60 requests per minute per user
- **System endpoints**: 1000 requests per hour per IP
- **Demo endpoints**: 10 requests per hour per IP

## Monitoring and Analytics

Available metrics (via `/system/stats`):

- Total conversations
- Active users
- Token usage
- Response times
- Error rates
- Agent utilization

---

*API Reference last updated: August 4, 2025*