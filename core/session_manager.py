"""
Redis-based session management for user-agent interactions.
"""
import json
import redis
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from utils.exceptions import SessionError


@dataclass
class UserSession:
    """User session data structure."""
    user_id: str
    session_id: str
    agent_id: str
    created_at: datetime
    last_activity: datetime
    context: Dict[str, Any]
    message_history: List[Dict[str, Any]]
    is_active: bool


class RedisSessionManager:
    """Redis-based session management for user-agent interactions."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.logger = logging.getLogger("session_manager")
        
        # Session configuration
        self.session_ttl = 3600  # 1 hour default TTL
        self.max_message_history = 100  # Maximum messages to keep in session
        
        # Redis key prefixes
        self.key_prefixes = {
            "session": "session:",
            "user_sessions": "user_sessions:",
            "agent_sessions": "agent_sessions:",
            "active_sessions": "active_sessions"
        }
    
    async def initialize(self) -> None:
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            await self._test_connection()
            
            self.logger.info("Redis session manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis session manager: {e}")
            raise SessionError(f"Session manager initialization failed: {e}")
    
    async def _test_connection(self) -> None:
        """Test Redis connection."""
        try:
            self.redis_client.ping()
        except Exception as e:
            raise SessionError(f"Redis connection failed: {e}")
    
    async def create_session(
        self,
        user_id: str,
        session_id: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> UserSession:
        """Create a new user session."""
        try:
            now = datetime.utcnow()
            
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                agent_id=agent_id,
                created_at=now,
                last_activity=now,
                context=context or {},
                message_history=[],
                is_active=True
            )
            
            # Store session data
            session_key = f"{self.key_prefixes['session']}{session_id}"
            session_data = self._serialize_session(session)
            
            # Set session with TTL
            self.redis_client.setex(
                session_key,
                self.session_ttl,
                json.dumps(session_data)
            )
            
            # Add to user sessions index
            user_sessions_key = f"{self.key_prefixes['user_sessions']}{user_id}"
            self.redis_client.sadd(user_sessions_key, session_id)
            self.redis_client.expire(user_sessions_key, self.session_ttl)
            
            # Add to agent sessions index
            agent_sessions_key = f"{self.key_prefixes['agent_sessions']}{agent_id}"
            self.redis_client.sadd(agent_sessions_key, session_id)
            self.redis_client.expire(agent_sessions_key, self.session_ttl)
            
            # Add to active sessions
            self.redis_client.sadd(self.key_prefixes["active_sessions"], session_id)
            
            self.logger.info(f"Created session {session_id} for user {user_id} with agent {agent_id}")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise SessionError(f"Session creation failed: {e}")
    
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Retrieve session by ID."""
        try:
            session_key = f"{self.key_prefixes['session']}{session_id}"
            session_data = self.redis_client.get(session_key)
            
            if not session_data:
                return None
            
            session_dict = json.loads(session_data)
            return self._deserialize_session(session_dict)
            
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {e}")
            raise SessionError(f"Session retrieval failed: {e}")
    
    async def update_session(self, session: UserSession) -> None:
        """Update session data."""
        try:
            session.last_activity = datetime.utcnow()
            
            session_key = f"{self.key_prefixes['session']}{session.session_id}"
            session_data = self._serialize_session(session)
            
            # Update with new TTL
            self.redis_client.setex(
                session_key,
                self.session_ttl,
                json.dumps(session_data)
            )
            
            self.logger.debug(f"Updated session {session.session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update session {session.session_id}: {e}")
            raise SessionError(f"Session update failed: {e}")
    
    async def add_message_to_session(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> None:
        """Add message to session history."""
        try:
            session = await self.get_session(session_id)
            if not session:
                raise SessionError(f"Session {session_id} not found")
            
            # Add timestamp to message
            message["timestamp"] = datetime.utcnow().isoformat()
            
            # Add to message history
            session.message_history.append(message)
            
            # Trim history if too long
            if len(session.message_history) > self.max_message_history:
                session.message_history = session.message_history[-self.max_message_history:]
            
            # Update session
            await self.update_session(session)
            
            self.logger.debug(f"Added message to session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to add message to session {session_id}: {e}")
            raise SessionError(f"Message addition failed: {e}")
    
    async def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user."""
        try:
            user_sessions_key = f"{self.key_prefixes['user_sessions']}{user_id}"
            return list(self.redis_client.smembers(user_sessions_key))
            
        except Exception as e:
            self.logger.error(f"Failed to get user sessions for {user_id}: {e}")
            raise SessionError(f"User sessions retrieval failed: {e}")
    
    async def get_agent_sessions(self, agent_id: str) -> List[str]:
        """Get all session IDs for an agent."""
        try:
            agent_sessions_key = f"{self.key_prefixes['agent_sessions']}{agent_id}"
            return list(self.redis_client.smembers(agent_sessions_key))
            
        except Exception as e:
            self.logger.error(f"Failed to get agent sessions for {agent_id}: {e}")
            raise SessionError(f"Agent sessions retrieval failed: {e}")
    
    async def end_session(self, session_id: str) -> None:
        """End a session and clean up."""
        try:
            session = await self.get_session(session_id)
            if not session:
                self.logger.warning(f"Session {session_id} not found for cleanup")
                return
            
            # Mark as inactive
            session.is_active = False
            await self.update_session(session)
            
            # Remove from active sessions
            self.redis_client.srem(self.key_prefixes["active_sessions"], session_id)
            
            # Remove from user and agent indices
            user_sessions_key = f"{self.key_prefixes['user_sessions']}{session.user_id}"
            agent_sessions_key = f"{self.key_prefixes['agent_sessions']}{session.agent_id}"
            
            self.redis_client.srem(user_sessions_key, session_id)
            self.redis_client.srem(agent_sessions_key, session_id)
            
            self.logger.info(f"Ended session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to end session {session_id}: {e}")
            raise SessionError(f"Session cleanup failed: {e}")
    
    async def get_active_sessions(self) -> List[str]:
        """Get all active session IDs."""
        try:
            return list(self.redis_client.smembers(self.key_prefixes["active_sessions"]))
            
        except Exception as e:
            self.logger.error(f"Failed to get active sessions: {e}")
            raise SessionError(f"Active sessions retrieval failed: {e}")
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count."""
        try:
            cleaned_count = 0
            active_sessions = await self.get_active_sessions()
            
            for session_id in active_sessions:
                session = await self.get_session(session_id)
                if not session:
                    # Session expired, remove from active list
                    self.redis_client.srem(self.key_prefixes["active_sessions"], session_id)
                    cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
            raise SessionError(f"Session cleanup failed: {e}")
    
    def _serialize_session(self, session: UserSession) -> Dict[str, Any]:
        """Serialize session object to dictionary."""
        session_dict = asdict(session)
        session_dict["created_at"] = session.created_at.isoformat()
        session_dict["last_activity"] = session.last_activity.isoformat()
        return session_dict
    
    def _deserialize_session(self, session_dict: Dict[str, Any]) -> UserSession:
        """Deserialize dictionary to session object."""
        session_dict["created_at"] = datetime.fromisoformat(session_dict["created_at"])
        session_dict["last_activity"] = datetime.fromisoformat(session_dict["last_activity"])
        
        return UserSession(**session_dict)
    
    async def close(self) -> None:
        """Close Redis connection."""
        try:
            if self.redis_client:
                self.redis_client.close()
                self.logger.info("Redis connection closed")
                
        except Exception as e:
            self.logger.error(f"Error closing Redis connection: {e}")