# Overview

This is a production-ready AI agents system with comprehensive REST API and intelligent agent management. The system creates and manages multiple independent AI agents with different personalities and business specializations, each powered by OpenAI's GPT-4o model. The system features a complete REST API architecture using FastAPI for system management and client communication. The system supports two main agent types: an analytical financial advisor agent (Agent Alpha) and a creative content creator agent (Agent Beta). Each agent operates with its own personality traits, business rules, and conversation context management. The system integrates with OpenAI API for intelligent responses and implements comprehensive conversation memory and context awareness.

## Current Implementation Status

✅ **Operational Components:**
- FastAPI REST API server running on port 5000 (Production Ready)
- Two fully functional AI agents (agent_alpha, agent_beta)  
- OpenAI GPT-4o integration with conversation context
- MCP (Model Context Protocol) integration for external tools and data
- Smart context enhancement with automatic data retrieval
- Personality-based response generation (analytical vs creative)
- Business domain specialization (financial advisor vs content creator)
- Database persistence with conversation history
- Type-safe implementation with resolved LSP diagnostics
- Comprehensive API endpoints for frontend integration
- Real-time chat functionality with memory management
- Health monitoring and system statistics
- Complete API documentation and testing endpoints

✅ **Available Modes:**
- **Standalone Mode** (Currently Active): Simple, efficient implementation for development and production
- **Distributed Mode** (Available): Full system with RabbitMQ, Redis, WebSocket for enterprise deployment
- **Containerized Mode** (Available): Docker-based deployment with PostgreSQL/Supabase integration

## Complete Documentation

📚 **Comprehensive documentation has been created covering all aspects of the system:**

- **README.md**: Project overview, quick start, and feature guide
- **docs/API_REFERENCE.md**: Complete API documentation with examples and SDKs
- **docs/SYSTEM_ARCHITECTURE.md**: Detailed technical architecture and design patterns
- **docs/DEPLOYMENT_GUIDE.md**: Deployment instructions for all platforms (Replit, Docker, Cloud)
- **docs/USAGE_EXAMPLES.md**: Practical usage examples and integration patterns
- **docs/INDEX.md**: Documentation index and navigation guide
- **CHANGELOG.md**: Version history and feature tracking

📊 **Current System Status:**
- Two fully operational AI agents with distinct personalities and specializations
- Complete REST API with 8 endpoints for comprehensive functionality
- OpenAI GPT-4o integration with conversation context management
- Database persistence with SQLite conversation storage
- Type-safe implementation with all code quality issues resolved
- Production-ready with health monitoring and error handling
- Full documentation with examples for all major programming languages
- Ready for frontend integration and production deployment

🔧 **Recent Fixes (August 2025):**
- ✅ Fixed OpenAI message format compatibility
- ✅ Added database conversation persistence 
- ✅ Resolved all LSP type safety diagnostics
- ✅ Created production-ready API server (api_server_simple.py)
- ✅ Implemented comprehensive health checks and error handling

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Message Flow Control Architecture
Complete message flow system using RabbitMQ for reliable message queuing between users and agents, Redis for session state management and caching, WebSocket server for real-time bidirectional communication, and FastAPI REST API for system management. The system gracefully degrades to standalone mode when message broker services are unavailable.

## Agent Management Architecture
The system uses a factory pattern to create configurable AI agents with different personalities (analytical, creative, helpful, professional) and business rules (financial_advisor, content_creator, technical_support, general_assistant). Each agent runs independently with its own processing loop and maintains separate state through the AgentState dataclass. Agents are now integrated with message brokers and session managers for production-ready communication.

## Workflow Engine
Built on LangGraph, the workflow system processes user interactions through a structured pipeline: input validation, user notification, business rule processing, RAG retrieval, and response generation. The WorkflowEngine manages the flow between these stages and handles error recovery.

## Message Broker System (RabbitMQ)
Production-ready message queuing with dedicated exchanges (direct, fanout, topic) and queues for user prompts, agent responses, notifications, and system events. Implements message persistence, delivery guarantees, and error handling with message acknowledgments and retry mechanisms.

## Session Management System (Redis)
Redis-based session management for user-agent interactions with configurable TTL, message history tracking, user/agent session indexing, and automatic cleanup of expired sessions. Supports session context persistence and real-time state updates.

## WebSocket Communication Server
Real-time bidirectional communication server supporting user connections, agent subscriptions, message broadcasting, and connection management. Handles authentication, ping/pong heartbeat, and automatic connection cleanup with comprehensive error handling.

## REST API System (FastAPI)
Complete API management system with endpoints for session creation/management, message sending, agent status monitoring, and health checks. Features CORS support, comprehensive error handling, and integration with all message flow components.

## Personality System
The PersonalityManager defines distinct agent behaviors through traits, response templates, and processing styles. Personalities include analytical (data-driven), creative (innovative), helpful (service-oriented), and professional (business-focused) approaches, each with specific tone and communication patterns.

## Business Rules Engine
A rule-based system that applies domain-specific logic based on agent specialization. Rules include financial compliance for advisor agents, content moderation for creator agents, and specialized processing logic for different business domains.

## Data Persistence Layer
Uses PostgreSQL/Supabase with agent-specific schema architecture. Each agent has its own dedicated database schema (agent_alpha, agent_beta) with business-specific tables, while shared data lives in the public schema. Features connection management, query optimization, data validation through Pydantic schemas, and automated table creation based on business rules. Stores user interactions, agent responses, and system metadata with proper error handling and connection pooling.

## RAG Knowledge System
Implements document ingestion, vector search, and context retrieval for enhanced agent responses. Integrates with the database for document storage and uses content hashing for deduplication and efficient retrieval.

## MCP Integration
Connects to external MCP servers for tool integration and extended capabilities. Manages multiple server connections with health checks, authentication, and failover mechanisms for reliable external service integration.

## Configuration Management
Environment-based configuration system that handles database credentials, API keys, server endpoints, message broker URLs, and operational parameters. Supports different deployment environments with secure credential management.

## Error Handling System
Comprehensive exception hierarchy with structured error reporting, logging, and recovery mechanisms. Custom exceptions for different system components including message broker, session management, and WebSocket errors with detailed error context and debugging information.

# External Dependencies

## Database Services  
- **PostgreSQL**: Primary database engine with agent-specific schema architecture (agent_alpha, agent_beta schemas)
- **Supabase Stack**: Complete database stack including PostgREST API, Kong gateway, and Supabase Studio for management
- **Agent Schema Management**: Automated schema creation and management for agent-specific business tables
- **Docker Integration**: Full containerized database stack with initialization scripts

## AI/ML Services
- **OpenAI API**: Language model integration for agent responses and natural language processing
- **LangChain**: Framework for LLM application development and prompt management
- **LangGraph**: Workflow orchestration and state management for agent processing

## Message Flow Services
- **RabbitMQ**: Message broker for reliable queuing and delivery of user-agent communications
- **Redis**: Session state management and caching for user interactions and agent context
- **WebSocket**: Real-time bidirectional communication for live user-agent interactions

## External APIs
- **MCP Servers**: Model Context Protocol servers for external tool integration and extended capabilities
- **Custom MCP Tools**: Domain-specific tools and services accessed through MCP protocol

## Python Libraries
- **aiohttp**: Async HTTP client for MCP server communication and WebSocket support
- **pydantic**: Data validation and serialization for API schemas and message structures
- **asyncio**: Asynchronous programming support for concurrent agent operations
- **pika**: RabbitMQ client for message broker operations
- **redis**: Redis client for session management and caching
- **websockets**: WebSocket server implementation for real-time communication
- **fastapi**: REST API framework for system management endpoints
- **uvicorn**: ASGI server for running the FastAPI application

## Infrastructure
- **Environment Variables**: Configuration management for deployment-specific settings including broker URLs
- **Logging System**: Structured logging with configurable levels and formatting
- **Health Monitoring**: System health checks and component status monitoring
- **Graceful Degradation**: Fallback to standalone mode when external services are unavailable