# Overview

This is an AI agents system that creates and manages multiple independent AI agents with different personalities and business specializations. The system supports two main agent types: an analytical financial advisor agent and a creative content creator agent. Each agent operates with its own personality traits, business rules, and processing workflows built on LangGraph. The system integrates with Supabase for data persistence, implements RAG (Retrieval-Augmented Generation) for knowledge management, and connects to MCP (Model Context Protocol) servers for external tool integration.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Agent Management Architecture
The system uses a factory pattern to create configurable AI agents with different personalities (analytical, creative, helpful, professional) and business rules (financial_advisor, content_creator, technical_support, general_assistant). Each agent runs independently with its own processing loop and maintains separate state through the AgentState dataclass.

## Workflow Engine
Built on LangGraph, the workflow system processes user interactions through a structured pipeline: input validation, user notification, business rule processing, RAG retrieval, and response generation. The WorkflowEngine manages the flow between these stages and handles error recovery.

## Personality System
The PersonalityManager defines distinct agent behaviors through traits, response templates, and processing styles. Personalities include analytical (data-driven), creative (innovative), helpful (service-oriented), and professional (business-focused) approaches, each with specific tone and communication patterns.

## Business Rules Engine
A rule-based system that applies domain-specific logic based on agent specialization. Rules include financial compliance for advisor agents, content moderation for creator agents, and specialized processing logic for different business domains.

## Data Persistence Layer
Uses Supabase as the primary database with connection management, query optimization, and data validation through Pydantic schemas. Stores user interactions, agent responses, and system metadata with proper error handling and connection pooling.

## RAG Knowledge System
Implements document ingestion, vector search, and context retrieval for enhanced agent responses. Integrates with the database for document storage and uses content hashing for deduplication and efficient retrieval.

## MCP Integration
Connects to external MCP servers for tool integration and extended capabilities. Manages multiple server connections with health checks, authentication, and failover mechanisms for reliable external service integration.

## Configuration Management
Environment-based configuration system that handles database credentials, API keys, server endpoints, and operational parameters. Supports different deployment environments with secure credential management.

## Error Handling System
Comprehensive exception hierarchy with structured error reporting, logging, and recovery mechanisms. Custom exceptions for different system components with detailed error context and debugging information.

# External Dependencies

## Database Services
- **Supabase**: Primary database service for data persistence, user management, and real-time features
- **PostgreSQL**: Underlying database engine (via Supabase) for structured data storage

## AI/ML Services
- **OpenAI API**: Language model integration for agent responses and natural language processing
- **LangChain**: Framework for LLM application development and prompt management
- **LangGraph**: Workflow orchestration and state management for agent processing

## External APIs
- **MCP Servers**: Model Context Protocol servers for external tool integration and extended capabilities
- **Custom MCP Tools**: Domain-specific tools and services accessed through MCP protocol

## Python Libraries
- **aiohttp**: Async HTTP client for MCP server communication
- **pydantic**: Data validation and serialization for API schemas
- **asyncio**: Asynchronous programming support for concurrent agent operations

## Infrastructure
- **Environment Variables**: Configuration management for deployment-specific settings
- **Logging System**: Structured logging with configurable levels and formatting