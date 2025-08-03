"""
Pydantic schemas for data validation and serialization.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator

class UserInteraction(BaseModel):
    """Schema for user interaction data."""
    
    user_id: str = Field(..., description="Unique identifier for the user")
    session_id: str = Field(..., description="Session identifier for the conversation")
    agent_id: str = Field(..., description="Agent identifier")
    prompt: str = Field(..., min_length=1, description="User's input prompt")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Interaction timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @validator('prompt')
    def prompt_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()
    
    @validator('user_id', 'session_id', 'agent_id')
    def ids_not_empty(cls, v):
        if not v.strip():
            raise ValueError('ID fields cannot be empty')
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentResponse(BaseModel):
    """Schema for agent response data."""
    
    agent_id: str = Field(..., description="Agent identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    content: str = Field(..., min_length=1, description="Agent's response content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Response metadata")
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Response content cannot be empty')
        return v.strip()
    
    @validator('agent_id', 'user_id', 'session_id')
    def ids_not_empty(cls, v):
        if not v.strip():
            raise ValueError('ID fields cannot be empty')
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentConfiguration(BaseModel):
    """Schema for agent configuration."""
    
    agent_id: str = Field(..., description="Unique agent identifier")
    personality: str = Field(..., description="Agent personality type")
    business_rules: str = Field(..., description="Business rules type")
    mcp_servers: List[str] = Field(default_factory=list, description="List of MCP server URLs")
    database_config: Dict[str, Any] = Field(..., description="Database configuration")
    is_active: bool = Field(default=True, description="Whether the agent is active")
    configuration: Optional[Dict[str, Any]] = Field(default=None, description="Additional configuration")
    
    @validator('personality')
    def validate_personality(cls, v):
        valid_personalities = ['analytical', 'creative', 'helpful', 'professional']
        if v not in valid_personalities:
            raise ValueError(f'Personality must be one of: {valid_personalities}')
        return v
    
    @validator('business_rules')
    def validate_business_rules(cls, v):
        valid_rules = ['financial_advisor', 'content_creator', 'technical_support', 'general_assistant']
        if v not in valid_rules:
            raise ValueError(f'Business rules must be one of: {valid_rules}')
        return v
    
    @validator('mcp_servers')
    def validate_mcp_servers(cls, v):
        if not isinstance(v, list):
            raise ValueError('MCP servers must be a list')
        
        for server in v:
            if not isinstance(server, str) or not server.startswith(('http://', 'https://')):
                raise ValueError('MCP server URLs must be valid HTTP/HTTPS URLs')
        
        return v

class RAGDocument(BaseModel):
    """Schema for RAG document data."""
    
    document_id: str = Field(..., description="Unique document identifier")
    content: str = Field(..., min_length=1, description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Document metadata")
    embeddings: Optional[List[float]] = Field(default=None, description="Document embeddings")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Document content cannot be empty')
        return v.strip()
    
    @validator('document_id')
    def document_id_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Document ID cannot be empty')
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RAGQueryResult(BaseModel):
    """Schema for RAG query results."""
    
    document_id: str = Field(..., description="Document identifier")
    content: str = Field(..., description="Document content")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Document metadata")
    
    class Config:
        validate_assignment = True

class MCPToolCall(BaseModel):
    """Schema for MCP tool call data."""
    
    tool_name: str = Field(..., description="Name of the MCP tool")
    server_url: str = Field(..., description="MCP server URL")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Call timestamp")
    
    @validator('tool_name')
    def tool_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Tool name cannot be empty')
        return v.strip()
    
    @validator('server_url')
    def validate_server_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Server URL must be a valid HTTP/HTTPS URL')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MCPToolResult(BaseModel):
    """Schema for MCP tool call results."""
    
    tool_call: MCPToolCall = Field(..., description="Original tool call")
    result: Dict[str, Any] = Field(..., description="Tool execution result")
    success: bool = Field(..., description="Whether the call was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if call failed")
    execution_time: float = Field(..., ge=0.0, description="Execution time in seconds")
    
    class Config:
        validate_assignment = True

class BusinessRuleResult(BaseModel):
    """Schema for business rule processing results."""
    
    category: str = Field(..., description="Business rule category")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    recommendations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Business recommendations")
    compliance_info: Optional[Dict[str, Any]] = Field(default=None, description="Compliance information")
    risk_assessment: Optional[str] = Field(default=None, description="Risk assessment level")
    
    @validator('category')
    def category_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip()

class WorkflowState(BaseModel):
    """Schema for workflow state data."""
    
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    agent_id: str = Field(..., description="Agent identifier")
    current_step: str = Field(..., description="Current workflow step")
    context: Dict[str, Any] = Field(default_factory=dict, description="Workflow context")
    completed_steps: List[str] = Field(default_factory=list, description="Completed workflow steps")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="State timestamp")
    
    @validator('session_id', 'user_id', 'agent_id', 'current_step')
    def ids_not_empty(cls, v):
        if not v.strip():
            raise ValueError('ID and step fields cannot be empty')
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Utility functions for schema validation

def validate_user_interaction(data: Dict[str, Any]) -> UserInteraction:
    """Validate and create UserInteraction from dictionary."""
    return UserInteraction(**data)

def validate_agent_response(data: Dict[str, Any]) -> AgentResponse:
    """Validate and create AgentResponse from dictionary."""
    return AgentResponse(**data)

def validate_agent_configuration(data: Dict[str, Any]) -> AgentConfiguration:
    """Validate and create AgentConfiguration from dictionary."""
    return AgentConfiguration(**data)

def validate_rag_document(data: Dict[str, Any]) -> RAGDocument:
    """Validate and create RAGDocument from dictionary."""
    return RAGDocument(**data)

def serialize_for_database(model: BaseModel) -> Dict[str, Any]:
    """Serialize Pydantic model for database storage."""
    return model.dict(exclude_none=True)

def deserialize_from_database(data: Dict[str, Any], model_class: type) -> BaseModel:
    """Deserialize database data to Pydantic model."""
    return model_class(**data)
