"""
Custom exceptions for the AI agents system.
"""

class BaseAgentException(Exception):
    """Base exception for all agent-related errors."""
    
    def __init__(self, message: str, error_code: str | None = None, details: dict | None = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for logging/API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }

class AgentError(BaseAgentException):
    """General agent operation errors."""
    pass

class DatabaseError(BaseAgentException):
    """Database-related errors."""
    pass

class MCPError(BaseAgentException):
    """MCP (Model Context Protocol) related errors."""
    pass

class WorkflowError(BaseAgentException):
    """LangGraph workflow execution errors."""
    pass

class BusinessRuleError(BaseAgentException):
    """Business rule processing errors."""
    pass

class RAGError(BaseAgentException):
    """RAG system errors."""
    pass

class ConfigurationError(BaseAgentException):
    """Configuration and settings errors."""
    pass

class ValidationError(BaseAgentException):
    """Data validation errors."""
    pass

class AuthenticationError(BaseAgentException):
    """Authentication and authorization errors."""
    pass

class RateLimitError(BaseAgentException):
    """Rate limiting errors."""
    pass

class TimeoutError(BaseAgentException):
    """Operation timeout errors."""
    pass

# Error handlers for common exceptions

def handle_database_error(func):
    """Decorator to handle database errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "connection" in str(e).lower():
                raise DatabaseError(
                    "Database connection failed",
                    error_code="DB_CONNECTION_FAILED",
                    details={"original_error": str(e)}
                )
            elif "timeout" in str(e).lower():
                raise DatabaseError(
                    "Database operation timed out",
                    error_code="DB_TIMEOUT",
                    details={"original_error": str(e)}
                )
            else:
                raise DatabaseError(
                    f"Database operation failed: {str(e)}",
                    error_code="DB_OPERATION_FAILED",
                    details={"original_error": str(e)}
                )
    return wrapper

def handle_mcp_error(func):
    """Decorator to handle MCP errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                raise MCPError(
                    "MCP server connection failed",
                    error_code="MCP_CONNECTION_FAILED",
                    details={"original_error": str(e)}
                )
            elif "timeout" in str(e).lower():
                raise MCPError(
                    "MCP operation timed out",
                    error_code="MCP_TIMEOUT",
                    details={"original_error": str(e)}
                )
            elif "404" in str(e) or "not found" in str(e).lower():
                raise MCPError(
                    "MCP tool or resource not found",
                    error_code="MCP_NOT_FOUND",
                    details={"original_error": str(e)}
                )
            else:
                raise MCPError(
                    f"MCP operation failed: {str(e)}",
                    error_code="MCP_OPERATION_FAILED",
                    details={"original_error": str(e)}
                )
    return wrapper

def handle_workflow_error(func):
    """Decorator to handle workflow errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise WorkflowError(
                f"Workflow execution failed: {str(e)}",
                error_code="WORKFLOW_EXECUTION_FAILED",
                details={"original_error": str(e)}
            )
    return wrapper

# Exception context manager for consistent error handling

class ErrorContext:
    """Context manager for consistent error handling and logging."""
    
    def __init__(self, operation_name: str, logger=None):
        self.operation_name = operation_name
        self.logger = logger
    
    def __enter__(self):
        if self.logger:
            self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_msg = f"Operation '{self.operation_name}' failed: {str(exc_val)}"
            
            if self.logger:
                self.logger.error(error_msg)
            
            # Re-raise with additional context if it's not already our custom exception
            if not isinstance(exc_val, BaseAgentException):
                raise AgentError(
                    error_msg,
                    error_code="OPERATION_FAILED",
                    details={
                        "operation": self.operation_name,
                        "original_error": str(exc_val),
                        "error_type": exc_type.__name__
                    }
                ) from exc_val
        else:
            if self.logger:
                self.logger.debug(f"Operation completed successfully: {self.operation_name}")

# Validation utilities

def validate_required_fields(data: dict, required_fields: list, error_prefix: str = ""):
    """Validate that required fields are present in data."""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            f"{error_prefix}Missing required fields: {', '.join(missing_fields)}",
            error_code="MISSING_REQUIRED_FIELDS",
            details={"missing_fields": missing_fields}
        )

def validate_field_types(data: dict, field_types: dict, error_prefix: str = ""):
    """Validate that fields have the correct types."""
    type_errors = []
    
    for field, expected_type in field_types.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                type_errors.append(f"{field} should be {expected_type.__name__}, got {type(data[field]).__name__}")
    
    if type_errors:
        raise ValidationError(
            f"{error_prefix}Type validation errors: {'; '.join(type_errors)}",
            error_code="INVALID_FIELD_TYPES",
            details={"type_errors": type_errors}
        )
