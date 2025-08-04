# AI Agents System - Architecture Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Module Structure](#module-structure)
5. [Design Patterns](#design-patterns)
6. [Scalability](#scalability)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)

## Architecture Overview

The AI Agents System follows a modular, event-driven architecture designed for scalability, maintainability, and extensibility. The system supports multiple operational modes including standalone, distributed, and production configurations.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Web App       │ │   Mobile App    │ │   API Clients   │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────────┐
│                      API Gateway Layer                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              FastAPI REST API Server                       │ │
│  │  • CORS Support    • Error Handling   • Rate Limiting      │ │
│  │  • Authentication  • Request Routing  • Response Caching   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Business Logic Layer                         │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │  Agent Factory   │ │  Personality     │ │  Business Rules  │ │
│  │  • Agent Creation│ │  • Trait Mapping │ │  • Domain Logic  │ │
│  │  • Configuration │ │  • Behavior Defs │ │  • Validation    │ │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   AI Processing Layer                           │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │  OpenAI Client   │ │  Workflow Engine │ │  Context Manager │ │
│  │  • GPT-4o API    │ │  • LangGraph     │ │  • Conversation  │ │
│  │  • Prompt Mgmt   │ │  • State Machine │ │  • Memory Mgmt   │ │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   Infrastructure Layer                          │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │   Data Storage   │ │   Message Queue  │ │   Monitoring     │ │
│  │   • PostgreSQL   │ │   • RabbitMQ     │ │   • Logging      │ │
│  │   • Redis Cache  │ │   • WebSockets   │ │   • Health Check │ │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Operational Modes

#### 1. Standalone Mode (Current Implementation)
- **Purpose**: Development and testing
- **Components**: API Server + Simple Agent System
- **Features**: Full functionality without external dependencies
- **File**: `api_server.py` + `standalone_simple.py`

#### 2. Distributed Mode (Available)
- **Purpose**: Production with message queuing
- **Components**: Full system with RabbitMQ, Redis, WebSocket
- **Features**: Real-time messaging, session management, scalability
- **Files**: `main.py`, `start_system.py`

#### 3. Containerized Mode (Available)
- **Purpose**: Microservices deployment
- **Components**: Docker containers with service orchestration
- **Features**: Database services, message brokers, load balancing
- **File**: `docker-compose.yml`

## System Components

### 1. API Gateway Layer

#### FastAPI REST Server (`api_server.py`)
```python
# Core responsibilities:
- HTTP request routing
- Request/response validation
- Error handling and formatting
- CORS configuration
- Health monitoring endpoints
- API documentation generation

# Key features:
- Async request processing
- Structured error responses
- Comprehensive endpoint coverage
- Development and production modes
```

#### Request Processing Pipeline
```
Client Request → CORS Middleware → Route Matching → 
Input Validation → Agent Selection → Business Logic → 
Response Generation → Error Handling → Client Response
```

### 2. Business Logic Layer

#### Agent Factory (`agents/agent_factory.py`)
```python
class AgentFactory:
    """
    Responsibilities:
    - Agent instantiation and configuration
    - Personality and domain assignment
    - Agent lifecycle management
    - Configuration validation
    """
    
    def create_agent(self, config):
        # Validate configuration
        # Apply personality traits
        # Set business domain
        # Initialize agent instance
        return agent
```

#### Personality System (`agents/personalities.py`)
```python
# Personality definitions with traits and communication styles
PERSONALITIES = {
    "analytical": {
        "traits": ["data-driven", "systematic", "logical-reasoning"],
        "tone": "professional",
        "approach": "evidence-based"
    },
    "creative": {
        "traits": ["innovative", "imaginative", "inspirational"],
        "tone": "enthusiastic", 
        "approach": "out-of-the-box-thinking"
    }
}
```

#### Business Rules Engine (`agents/business_rules.py`)
```python
class BusinessRules:
    """
    Domain-specific logic and constraints:
    - Financial advisor: Risk assessment, compliance
    - Content creator: Brand guidelines, audience focus
    - Technical support: Accuracy, step-by-step approach
    """
```

### 3. AI Processing Layer

#### OpenAI Integration (`core/openai_integration.py`)
```python
class OpenAIIntegrationManager:
    """
    Responsibilities:
    - API client management
    - Prompt engineering and optimization
    - Response processing and validation
    - Error handling and retry logic
    - Token usage tracking
    """
    
    async def generate_response(self, messages, context):
        # Build system prompt with personality
        # Add conversation history
        # Apply business context
        # Make API call with error handling
        # Process and validate response
        return response
```

#### Context Management
```python
# Conversation context structure
{
    "user_id": "string",
    "agent_id": "string", 
    "conversation_history": [
        {"role": "user", "content": "message"},
        {"role": "assistant", "content": "response"}
    ],
    "personality_context": {
        "type": "analytical",
        "traits": ["data-driven", "systematic"]
    },
    "business_context": {
        "domain": "financial_advisor",
        "specialization": "investment_strategy"
    },
    "session_metadata": {
        "created_at": "timestamp",
        "last_activity": "timestamp",
        "message_count": 10
    }
}
```

### 4. Infrastructure Layer

#### Database Architecture (`core/database.py`)
```sql
-- Agent-specific schemas
CREATE SCHEMA agent_alpha;  -- Financial advisor data
CREATE SCHEMA agent_beta;   -- Content creator data

-- Shared public schema
CREATE TABLE public.users (
    user_id VARCHAR PRIMARY KEY,
    created_at TIMESTAMP,
    last_active TIMESTAMP
);

CREATE TABLE public.conversations (
    conversation_id UUID PRIMARY KEY,
    user_id VARCHAR,
    agent_id VARCHAR,
    created_at TIMESTAMP,
    message_count INTEGER
);

CREATE TABLE public.messages (
    message_id UUID PRIMARY KEY,
    conversation_id UUID,
    role VARCHAR CHECK (role IN ('user', 'assistant')),
    content TEXT,
    tokens_used INTEGER,
    created_at TIMESTAMP
);
```

#### Session Management (`core/session_manager.py`)
```python
class SessionManager:
    """
    Redis-based session management:
    - User session tracking
    - Conversation context storage
    - TTL-based cleanup
    - Session analytics
    """
```

#### Message Broker (`core/message_broker.py`)
```python
class MessageBroker:
    """
    RabbitMQ message queuing:
    - User message routing
    - Agent response delivery
    - System event notifications
    - Dead letter handling
    """
```

## Data Flow

### Request Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant AgentFactory
    participant Agent
    participant OpenAI
    participant Database

    Client->>API: POST /agents/agent_alpha/chat
    API->>API: Validate request
    API->>AgentFactory: Get agent instance
    AgentFactory->>Agent: Route to agent_alpha
    Agent->>Agent: Apply personality & business rules
    Agent->>Database: Retrieve conversation history
    Agent->>Agent: Build context & system prompt
    Agent->>OpenAI: Generate response
    OpenAI->>Agent: Return response
    Agent->>Database: Store conversation
    Agent->>API: Return formatted response
    API->>Client: JSON response
```

### Agent Processing Pipeline

```
User Message Input
    ↓
Input Validation & Sanitization
    ↓
Agent Selection (agent_alpha/agent_beta)
    ↓
Personality Application (analytical/creative)
    ↓
Business Rules Processing (financial/content)
    ↓
Context Retrieval (conversation history)
    ↓
System Prompt Construction
    ↓
OpenAI API Call (GPT-4o)
    ↓
Response Processing & Validation
    ↓
Context Storage (conversation update)
    ↓
Response Formatting
    ↓
Client Response Delivery
```

### Data Storage Flow

```
Conversation Data:
User Message → Validation → Storage → Context Building
                      ↓
Agent Response ← Processing ← OpenAI API ← Prompt Construction

Session Data:
User Session → Redis Cache → TTL Management → Cleanup
              ↓
Conversation Context → Memory Management → History Limiting
```

## Module Structure

### Core Modules

```
core/
├── agent.py              # Base agent class and interfaces
├── openai_integration.py # OpenAI API client and management
├── database.py           # Database connection and operations
├── security.py           # Authentication and authorization
├── monitoring.py         # Health checks and metrics
├── session_manager.py    # Redis session management
├── message_broker.py     # RabbitMQ message handling
├── websocket_server.py   # Real-time communication
├── workflow.py           # LangGraph workflow engine
├── rag_system.py         # RAG knowledge management
├── vector_database.py    # Vector storage for embeddings
└── mcp_client.py         # MCP server integration
```

### Agent Modules

```
agents/
├── agent_factory.py      # Agent creation and management
├── personalities.py      # Personality definitions and traits
└── business_rules.py     # Domain-specific business logic
```

### API Modules

```
api/
└── rest_api.py          # Alternative FastAPI implementation
```

### Configuration and Utilities

```
config/
└── settings.py          # Environment configuration management

utils/
├── exceptions.py        # Custom exception hierarchy
└── logger.py           # Logging configuration

models/
└── schemas.py          # Pydantic data models
```

## Design Patterns

### 1. Factory Pattern (Agent Creation)
```python
class AgentFactory:
    def create_agent(self, agent_type, personality, domain):
        # Factory method to create different agent types
        agent_class = self._get_agent_class(agent_type)
        personality_config = self._get_personality(personality)
        business_rules = self._get_business_rules(domain)
        
        return agent_class(personality_config, business_rules)
```

### 2. Strategy Pattern (Personality & Business Rules)
```python
class Agent:
    def __init__(self, personality_strategy, business_strategy):
        self.personality = personality_strategy
        self.business_rules = business_strategy
    
    def process_message(self, message):
        # Apply different strategies based on configuration
        processed = self.personality.apply_traits(message)
        validated = self.business_rules.validate(processed)
        return self.generate_response(validated)
```

### 3. Observer Pattern (Event Handling)
```python
class SystemEventManager:
    def __init__(self):
        self._observers = []
    
    def subscribe(self, observer):
        self._observers.append(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.handle_event(event)
```

### 4. Singleton Pattern (Configuration Management)
```python
class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Load configuration
        return cls._instance
```

### 5. Command Pattern (Request Processing)
```python
class ChatCommand:
    def __init__(self, agent_id, user_id, message, context):
        self.agent_id = agent_id
        self.user_id = user_id
        self.message = message
        self.context = context
    
    def execute(self):
        # Execute chat command with validation and processing
        return self._process_chat()
```

## Scalability

### Horizontal Scaling

#### Load Balancing
```
Client Requests
    ↓
Load Balancer (Nginx/HAProxy)
    ↓
┌─────────────┬─────────────┬─────────────┐
│ API Server  │ API Server  │ API Server  │
│ Instance 1  │ Instance 2  │ Instance 3  │
└─────────────┴─────────────┴─────────────┘
    ↓
Shared Infrastructure (Database, Redis, RabbitMQ)
```

#### Database Scaling
```sql
-- Read replicas for conversation history
Master Database (Write) → Read Replica 1 (Read)
                       → Read Replica 2 (Read)
                       → Read Replica 3 (Read)

-- Sharding by agent_id or user_id
Shard 1: agent_alpha conversations
Shard 2: agent_beta conversations
Shard 3: system data and metadata
```

#### Cache Scaling
```
Redis Cluster:
- Node 1: User sessions (0-5461 hash slots)
- Node 2: Conversation cache (5462-10922 hash slots)
- Node 3: System cache (10923-16383 hash slots)
```

### Vertical Scaling

#### Resource Optimization
```python
# Async processing for better resource utilization
async def process_multiple_requests(requests):
    tasks = [process_single_request(req) for req in requests]
    results = await asyncio.gather(*tasks)
    return results

# Connection pooling
async def get_db_connection():
    return await asyncpg.create_pool(
        database_url,
        min_size=10,
        max_size=100,
        command_timeout=60
    )
```

#### Memory Management
```python
# Conversation history limiting
MAX_CONVERSATION_HISTORY = 20
if len(conversation) > MAX_CONVERSATION_HISTORY:
    conversation = conversation[-MAX_CONVERSATION_HISTORY:]

# Lazy loading of agent configurations
@lru_cache(maxsize=128)
def get_agent_config(agent_id):
    return load_agent_configuration(agent_id)
```

### Performance Optimization

#### Response Caching
```python
@lru_cache(maxsize=1000)
def get_system_prompt(personality_type, business_domain):
    # Cache frequently used system prompts
    return build_system_prompt(personality_type, business_domain)

# Redis caching for expensive operations
async def get_cached_response(cache_key):
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None
```

#### Database Optimization
```sql
-- Indexes for common queries
CREATE INDEX idx_conversations_user_agent ON conversations(user_id, agent_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);

-- Partitioning for large tables
CREATE TABLE messages_2025_08 PARTITION OF messages
FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
```

## Security Architecture

### Authentication & Authorization
```python
class SecurityManager:
    def generate_jwt_token(self, user_id, permissions):
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    def verify_token(self, token):
        # Token validation and user authorization
        pass
```

### Input Validation
```python
class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=4000)
    context: Optional[Dict[str, Any]] = None
    
    @validator('message')
    def validate_message(cls, v):
        # Sanitize input and check for malicious content
        return sanitize_input(v)
```

### Data Protection
```python
# Environment variable management
SECRET_KEY = os.getenv('SECRET_KEY', generate_random_key())
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Never logged or exposed

# Database connection security
DATABASE_URL = "postgresql://user:pass@host:port/db?sslmode=require"
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/agents/{agent_id}/chat")
@limiter.limit("60/minute")
async def chat_with_agent(request: Request, ...):
    # Rate-limited endpoint
    pass
```

## Deployment Architecture

### Development Environment
```yaml
# Local development
Services:
- FastAPI server (localhost:5000)
- OpenAI API integration
- In-memory conversation storage
- File-based logging

Dependencies:
- Python 3.11+
- OpenAI API key
- Development libraries
```

### Staging Environment
```yaml
# Staging with external services
Services:
- FastAPI server (staging.domain.com)
- PostgreSQL database
- Redis cache
- Centralized logging

Infrastructure:
- Docker containers
- Load balancer
- SSL certificates
- Monitoring dashboard
```

### Production Environment
```yaml
# Production with full infrastructure
Services:
- Multiple API server instances
- PostgreSQL cluster (master + replicas)
- Redis cluster
- RabbitMQ cluster
- WebSocket servers

Infrastructure:
- Kubernetes orchestration
- Auto-scaling policies
- Multi-zone deployment
- Disaster recovery
- Security scanning
- Performance monitoring
```

### Container Architecture
```dockerfile
# API Server Container
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000
CMD ["python", "api_server.py"]
```

```yaml
# Docker Compose for local development
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: agents_db
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

### Monitoring & Observability

#### Health Checks
```python
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database_health(),
        "openai": await check_openai_health(),
        "redis": await check_redis_health(),
        "memory": check_memory_usage(),
        "disk": check_disk_usage()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    return {"status": overall_status, "checks": checks}
```

#### Metrics Collection
```python
# Custom metrics for monitoring
conversation_counter = Counter('conversations_total', 'Total conversations')
response_time_histogram = Histogram('response_time_seconds', 'Response time')
error_counter = Counter('errors_total', 'Total errors', ['error_type'])

@response_time_histogram.time()
async def process_chat_request(request):
    conversation_counter.inc()
    try:
        return await handle_chat(request)
    except Exception as e:
        error_counter.labels(error_type=type(e).__name__).inc()
        raise
```

#### Logging Strategy
```python
# Structured logging with context
logger = structlog.get_logger()

async def chat_handler(agent_id, user_id, message):
    log = logger.bind(
        agent_id=agent_id,
        user_id=user_id,
        message_length=len(message)
    )
    
    log.info("Processing chat request")
    
    try:
        response = await process_chat(agent_id, user_id, message)
        log.info("Chat request completed", 
                tokens_used=response.get('tokens_used'),
                response_length=len(response.get('response', '')))
        return response
    except Exception as e:
        log.error("Chat request failed", error=str(e))
        raise
```

---

*Architecture Documentation last updated: August 4, 2025*