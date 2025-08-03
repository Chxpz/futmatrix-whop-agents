"""
Logging utilities for the AI agents system.
"""
import logging
import sys
from typing import Optional
from datetime import datetime
import os

def setup_logger(
    name: Optional[str] = None,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """Setup logger with consistent formatting."""
    
    if not format_string:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Get log level from environment or parameter
    log_level = getattr(logging, os.getenv("LOG_LEVEL", level).upper())
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

class AgentLogger:
    """Specialized logger for agent operations."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = setup_logger(f"agent_{agent_id}")
    
    def log_interaction(self, user_id: str, session_id: str, prompt: str) -> None:
        """Log user interaction."""
        self.logger.info(
            f"USER_INTERACTION | Agent: {self.agent_id} | User: {user_id} | "
            f"Session: {session_id} | Prompt: {prompt[:100]}..."
        )
    
    def log_response(self, user_id: str, session_id: str, response_length: int) -> None:
        """Log agent response."""
        self.logger.info(
            f"AGENT_RESPONSE | Agent: {self.agent_id} | User: {user_id} | "
            f"Session: {session_id} | Response Length: {response_length}"
        )
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log error with context."""
        self.logger.error(
            f"AGENT_ERROR | Agent: {self.agent_id} | Context: {context} | "
            f"Error: {str(error)}"
        )
    
    def log_workflow_step(self, step: str, duration: float, success: bool) -> None:
        """Log workflow step execution."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"WORKFLOW_STEP | Agent: {self.agent_id} | Step: {step} | "
            f"Duration: {duration:.2f}s | Status: {status}"
        )
    
    def log_database_operation(self, operation: str, table: str, success: bool) -> None:
        """Log database operation."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.debug(
            f"DATABASE_OP | Agent: {self.agent_id} | Operation: {operation} | "
            f"Table: {table} | Status: {status}"
        )
    
    def log_mcp_operation(self, operation: str, server: str, success: bool) -> None:
        """Log MCP operation."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.debug(
            f"MCP_OP | Agent: {self.agent_id} | Operation: {operation} | "
            f"Server: {server} | Status: {status}"
        )

class SystemLogger:
    """System-wide logger for application events."""
    
    def __init__(self):
        self.logger = setup_logger("system")
    
    def log_startup(self, component: str) -> None:
        """Log component startup."""
        self.logger.info(f"STARTUP | Component: {component} | Status: STARTED")
    
    def log_shutdown(self, component: str, reason: str = "normal") -> None:
        """Log component shutdown."""
        self.logger.info(f"SHUTDOWN | Component: {component} | Reason: {reason}")
    
    def log_health_check(self, component: str, status: str, details: str = "") -> None:
        """Log health check results."""
        self.logger.info(f"HEALTH_CHECK | Component: {component} | Status: {status} | Details: {details}")
    
    def log_configuration(self, config_item: str, value: str) -> None:
        """Log configuration settings (sanitized)."""
        # Sanitize sensitive values
        if any(sensitive in config_item.lower() for sensitive in ["key", "password", "secret", "token"]):
            value = "***REDACTED***"
        
        self.logger.debug(f"CONFIG | {config_item}: {value}")
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "") -> None:
        """Log performance metrics."""
        self.logger.info(f"PERFORMANCE | Metric: {metric_name} | Value: {value} {unit}")
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO") -> None:
        """Log security-related events."""
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(f"SECURITY | Event: {event_type} | Details: {details}")

# Initialize system logger
system_logger = SystemLogger()
