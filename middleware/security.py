"""
Production Security Middleware for AI Agents API
"""
import time
import logging
from collections import defaultdict
from typing import Dict, Optional
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

class ProductionSecurityMiddleware(BaseHTTPMiddleware):
    """Simple production security middleware with rate limiting and API key validation."""
    
    def __init__(self, app, api_keys: Optional[list] = None, rate_limit: int = 100):
        super().__init__(app)
        self.api_keys = set(api_keys) if api_keys else None
        self.rate_limit = rate_limit  # requests per minute per IP
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.logger = logging.getLogger("security_middleware")
    
    async def dispatch(self, request: Request, call_next):
        """Process request with security checks."""
        client_ip = request.client.host
        current_time = time.time()
        
        # Rate limiting
        if self._check_rate_limit(client_ip, current_time):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # API key validation (if configured)
        if self.api_keys and not self._validate_api_key(request):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _check_rate_limit(self, client_ip: str, current_time: float) -> bool:
        """Check if IP has exceeded rate limit."""
        # Clean old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.rate_limit:
            return True
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        return False
    
    def _validate_api_key(self, request: Request) -> bool:
        """Validate API key from Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return False
        
        try:
            # Expect "Bearer <api_key>" format
            scheme, api_key = auth_header.split(" ", 1)
            if scheme.lower() != "bearer":
                return False
            
            return api_key in self.api_keys
        except ValueError:
            return False
    
    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"


class APIKeyManager:
    """Simple API key management."""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a simple API key."""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return 'ai_' + ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def get_demo_keys() -> list:
        """Get demo API keys for testing."""
        return [
            "ai_demo_key_12345",
            "ai_test_key_67890",
            "ai_prod_key_abcdef"
        ]