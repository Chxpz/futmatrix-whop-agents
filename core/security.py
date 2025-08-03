"""
Security middleware and utilities for the AI agents system.
Handles authentication, rate limiting, API key validation, and security headers.
"""
import logging
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio
from functools import wraps

from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.base import BaseHTTPMiddleware
import jwt as pyjwt

from utils.exceptions import SecurityError
from config.settings import Settings


class RateLimiter:
    """Token bucket rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.logger = logging.getLogger("rate_limiter")
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limits."""
        now = time.time()
        window_start = now - self.time_window
        
        # Clean old requests
        client_requests = self.requests[client_id]
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        self.logger.warning(f"Rate limit exceeded for client: {client_id}")
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = time.time()
        window_start = now - self.time_window
        
        client_requests = self.requests[client_id]
        # Clean old requests
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))
    
    def get_reset_time(self, client_id: str) -> Optional[datetime]:
        """Get when rate limit resets for client."""
        client_requests = self.requests[client_id]
        if not client_requests:
            return None
        
        oldest_request = client_requests[0]
        reset_time = oldest_request + self.time_window
        return datetime.fromtimestamp(reset_time)


class APIKeyManager:
    """Manages API keys for external access."""
    
    def __init__(self):
        self.logger = logging.getLogger("api_keys")
        # In production, this would be stored in database
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
    
    def generate_api_key(self, 
                        client_name: str, 
                        permissions: List[str] = None,
                        rate_limit: int = 1000) -> str:
        """Generate new API key for client."""
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        
        self.api_keys[api_key] = {
            "client_name": client_name,
            "permissions": permissions or ["read", "write"],
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "active": True
        }
        
        # Create rate limiter for this API key
        self.rate_limiters[api_key] = RateLimiter(max_requests=rate_limit)
        
        self.logger.info(f"Generated API key for {client_name}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return client info."""
        if api_key not in self.api_keys:
            return None
        
        key_info = self.api_keys[api_key]
        if not key_info.get("active", False):
            return None
        
        # Update usage
        key_info["last_used"] = datetime.utcnow().isoformat()
        key_info["usage_count"] += 1
        
        return key_info
    
    def check_rate_limit(self, api_key: str) -> bool:
        """Check rate limit for API key."""
        if api_key not in self.rate_limiters:
            return False
        
        return self.rate_limiters[api_key].is_allowed(api_key)
    
    def get_rate_limit_info(self, api_key: str) -> Dict[str, Any]:
        """Get rate limit information for API key."""
        if api_key not in self.rate_limiters:
            return {"error": "API key not found"}
        
        limiter = self.rate_limiters[api_key]
        return {
            "remaining_requests": limiter.get_remaining_requests(api_key),
            "reset_time": limiter.get_reset_time(api_key),
            "max_requests": limiter.max_requests,
            "time_window": limiter.time_window
        }
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key."""
        if api_key in self.api_keys:
            self.api_keys[api_key]["active"] = False
            self.logger.info(f"Revoked API key: {api_key[:8]}...")
            return True
        return False


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for FastAPI application."""
    
    def __init__(self, app, settings: Settings, api_key_manager: APIKeyManager):
        super().__init__(app)
        self.settings = settings
        self.api_key_manager = api_key_manager
        self.logger = logging.getLogger("security_middleware")
        
        # Rate limiter for IP addresses
        self.ip_rate_limiter = RateLimiter(max_requests=1000, time_window=3600)
        
        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through security middleware."""
        start_time = time.time()
        
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Check IP rate limit
            if not self.ip_rate_limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests from this IP address"
                )
            
            # Validate API key if required
            api_key_valid = await self._validate_request_auth(request)
            
            # Add security context to request
            request.state.client_ip = client_ip
            request.state.api_key_valid = api_key_valid
            request.state.request_start_time = start_time
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            # Add rate limit headers
            remaining = self.ip_rate_limiter.get_remaining_requests(client_ip)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Limit"] = str(self.ip_rate_limiter.max_requests)
            
            # Add timing header
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Security middleware error: {e}")
            raise HTTPException(status_code=500, detail="Internal security error")
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (from load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    async def _validate_request_auth(self, request: Request) -> bool:
        """Validate request authentication."""
        # Skip auth for health check and docs
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return True
        
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            key_info = self.api_key_manager.validate_api_key(api_key)
            if key_info:
                # Check rate limit for this API key
                if not self.api_key_manager.check_rate_limit(api_key):
                    raise HTTPException(
                        status_code=429,
                        detail="API key rate limit exceeded"
                    )
                
                request.state.api_key_info = key_info
                return True
        
        # For development, allow requests without API key
        if self.settings.DATABASE_CONFIG.get("test_mode", False):
            return True
        
        # In production, require API key for protected endpoints
        if request.url.path.startswith("/api/"):
            raise HTTPException(
                status_code=401,
                detail="API key required"
            )
        
        return False


class JWTManager:
    """JWT token management for user sessions."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", expire_hours: int = 24):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_hours = expire_hours
        self.logger = logging.getLogger("jwt_manager")
    
    def create_token(self, user_id: str, agent_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Create JWT token for user session."""
        now = datetime.utcnow()
        expire = now + timedelta(hours=self.expire_hours)
        
        payload = {
            "user_id": user_id,
            "agent_id": agent_id,
            "iat": now,
            "exp": expire,
            "iss": "ai_agents_system"
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = pyjwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self.logger.info(f"Created JWT token for user {user_id}")
        
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = pyjwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
            
        except pyjwt.ExpiredSignatureError:
            self.logger.warning("JWT token expired")
            return None
        except pyjwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token if valid."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        # Create new token with same claims but new expiry
        user_id = payload.get("user_id")
        agent_id = payload.get("agent_id")
        
        if user_id and agent_id:
            return self.create_token(user_id, agent_id)
        
        return None


class SecurityManager:
    """Main security manager for the AI agents system."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("security_manager")
        
        # Initialize components
        self.api_key_manager = APIKeyManager()
        self.jwt_manager = JWTManager(
            secret_key=settings.OPENAI_API_KEY,  # Use as secret for now
            expire_hours=24
        )
        
        # Create default API keys for development
        self._create_default_api_keys()
    
    def _create_default_api_keys(self) -> None:
        """Create default API keys for development."""
        if self.settings.DATABASE_CONFIG.get("test_mode", False):
            # Create test API keys
            test_key = self.api_key_manager.generate_api_key(
                "development_client",
                permissions=["read", "write", "admin"],
                rate_limit=10000
            )
            
            self.logger.info(f"Created development API key: {test_key}")
    
    def get_middleware(self):
        """Get security middleware for FastAPI."""
        return SecurityMiddleware(None, self.settings, self.api_key_manager)
    
    def get_api_key_manager(self) -> APIKeyManager:
        """Get API key manager."""
        return self.api_key_manager
    
    def get_jwt_manager(self) -> JWTManager:
        """Get JWT manager."""
        return self.jwt_manager
    
    async def validate_agent_access(self, user_id: str, agent_id: str, api_key: str = None) -> bool:
        """Validate if user can access specific agent."""
        # Basic validation - in production, this would check user permissions
        
        if api_key:
            key_info = self.api_key_manager.validate_api_key(api_key)
            if not key_info:
                return False
            
            # Check if API key has permission for this agent
            permissions = key_info.get("permissions", [])
            if "admin" in permissions or "write" in permissions:
                return True
        
        # For development, allow all access
        if self.settings.DATABASE_CONFIG.get("test_mode", False):
            return True
        
        return False
    
    def hash_password(self, password: str) -> str:
        """Hash password for storage."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, stored_hash = password_hash.split(":")
            password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash_check.hex() == stored_hash
        except Exception:
            return False
    
    async def audit_log(self, 
                       event_type: str, 
                       user_id: str, 
                       details: Dict[str, Any],
                       client_ip: str = None) -> None:
        """Log security events for auditing."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "client_ip": client_ip,
            "details": details
        }
        
        # In production, this would be stored in a secure audit log
        self.logger.info(f"AUDIT: {event_type} - {user_id} - {details}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check security system health."""
        return {
            "status": "healthy",
            "active_api_keys": len([k for k, v in self.api_key_manager.api_keys.items() if v.get("active")]),
            "rate_limiters_active": len(self.api_key_manager.rate_limiters),
            "timestamp": datetime.utcnow().isoformat()
        }