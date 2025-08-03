"""
In-memory message broker simulation for environments without RabbitMQ.
Provides the same interface as RabbitMQBroker for testing and development.
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass
from collections import deque

from utils.exceptions import MessageBrokerError


@dataclass
class Message:
    """Message structure for broker communication."""
    id: str
    user_id: str
    agent_id: str
    content: str
    message_type: str  # 'user_prompt', 'agent_response', 'notification'
    timestamp: datetime
    session_id: str
    metadata: Dict[str, Any]


class MockMessageBroker:
    """In-memory message broker that simulates RabbitMQ functionality."""
    
    def __init__(self, broker_url: str = "mock://localhost"):
        self.broker_url = broker_url
        self.logger = logging.getLogger("mock_message_broker")
        
        # In-memory message queues
        self.queues = {
            "user_prompts": deque(),
            "agent_responses": deque(),
            "notifications": deque(),
            "system_events": deque()
        }
        
        # Message handlers
        self.message_handlers = {}
        self.is_consuming = False
        
        # Statistics
        self.stats = {
            "messages_published": 0,
            "messages_consumed": 0,
            "user_prompts": 0,
            "agent_responses": 0,
            "notifications": 0
        }
    
    async def initialize(self) -> None:
        """Initialize mock message broker."""
        try:
            # Simulate broker initialization
            await asyncio.sleep(0.1)
            
            self.logger.info("Mock message broker initialized successfully")
            self.logger.info("This is a simulation - messages are stored in memory only")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize mock message broker: {e}")
            raise MessageBrokerError(f"Mock broker initialization failed: {e}")
    
    def publish_user_prompt(self, message: Message) -> None:
        """Publish user prompt to the queue."""
        try:
            self.queues["user_prompts"].append(message)
            self.stats["messages_published"] += 1
            self.stats["user_prompts"] += 1
            
            self.logger.info(f"Published user prompt {message.id} for agent {message.agent_id}")
            
            # Trigger handlers if consuming
            if self.is_consuming and "user_prompts" in self.message_handlers:
                asyncio.create_task(self._process_message("user_prompts", message))
            
        except Exception as e:
            self.logger.error(f"Failed to publish user prompt: {e}")
            raise MessageBrokerError(f"Failed to publish message: {e}")
    
    def publish_agent_response(self, message: Message) -> None:
        """Publish agent response to the queue."""
        try:
            self.queues["agent_responses"].append(message)
            self.stats["messages_published"] += 1
            self.stats["agent_responses"] += 1
            
            self.logger.info(f"Published agent response {message.id} from agent {message.agent_id}")
            
            # Trigger handlers if consuming
            if self.is_consuming and "agent_responses" in self.message_handlers:
                asyncio.create_task(self._process_message("agent_responses", message))
            
        except Exception as e:
            self.logger.error(f"Failed to publish agent response: {e}")
            raise MessageBrokerError(f"Failed to publish response: {e}")
    
    def publish_notification(self, message: Message) -> None:
        """Publish notification to all subscribers."""
        try:
            self.queues["notifications"].append(message)
            self.stats["messages_published"] += 1
            self.stats["notifications"] += 1
            
            self.logger.info(f"Published notification {message.id}")
            
            # Trigger handlers if consuming
            if self.is_consuming and "notifications" in self.message_handlers:
                asyncio.create_task(self._process_message("notifications", message))
            
        except Exception as e:
            self.logger.error(f"Failed to publish notification: {e}")
            raise MessageBrokerError(f"Failed to publish notification: {e}")
    
    def consume_user_prompts(self, callback: Callable) -> None:
        """Start consuming user prompts."""
        try:
            self.message_handlers["user_prompts"] = callback
            self.logger.info("Started consuming user prompts (mock)")
            
        except Exception as e:
            self.logger.error(f"Failed to start consuming user prompts: {e}")
            raise MessageBrokerError(f"Failed to start consuming: {e}")
    
    def consume_agent_responses(self, callback: Callable) -> None:
        """Start consuming agent responses."""
        try:
            self.message_handlers["agent_responses"] = callback
            self.logger.info("Started consuming agent responses (mock)")
            
        except Exception as e:
            self.logger.error(f"Failed to start consuming agent responses: {e}")
            raise MessageBrokerError(f"Failed to start consuming responses: {e}")
    
    async def _process_message(self, queue_name: str, message: Message) -> None:
        """Process a message through its handler."""
        try:
            handler = self.message_handlers.get(queue_name)
            if handler:
                await asyncio.sleep(0.01)  # Simulate processing delay
                handler(message)
                self.stats["messages_consumed"] += 1
                
        except Exception as e:
            self.logger.error(f"Error processing message from {queue_name}: {e}")
    
    def start_consuming(self) -> None:
        """Start consuming messages from all queues."""
        try:
            self.is_consuming = True
            self.logger.info("Started message consumption (mock mode)")
            
        except Exception as e:
            self.logger.error(f"Failed to start consuming: {e}")
            raise MessageBrokerError(f"Failed to start consuming: {e}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queues": {name: len(queue) for name, queue in self.queues.items()},
            "statistics": self.stats.copy(),
            "is_consuming": self.is_consuming,
            "handlers": list(self.message_handlers.keys())
        }
    
    def get_messages(self, queue_name: str, limit: int = 10) -> List[Message]:
        """Get recent messages from a queue."""
        if queue_name not in self.queues:
            return []
        
        queue = self.queues[queue_name]
        return list(queue)[-limit:] if queue else []
    
    def clear_queue(self, queue_name: str) -> int:
        """Clear a specific queue and return count of removed messages."""
        if queue_name not in self.queues:
            return 0
        
        count = len(self.queues[queue_name])
        self.queues[queue_name].clear()
        self.logger.info(f"Cleared {count} messages from {queue_name} queue")
        return count
    
    def close(self) -> None:
        """Close broker connection."""
        try:
            self.is_consuming = False
            self.message_handlers.clear()
            
            # Log final statistics
            total_messages = sum(len(queue) for queue in self.queues.values())
            self.logger.info(f"Mock message broker closed. Final stats: {total_messages} messages in queues")
            
        except Exception as e:
            self.logger.error(f"Error closing mock message broker: {e}")


class MockRedisSession:
    """Mock Redis session manager for environments without Redis."""
    
    def __init__(self, redis_url: str = "mock://localhost:6379"):
        self.redis_url = redis_url
        self.logger = logging.getLogger("mock_session_manager")
        
        # In-memory storage
        self.sessions = {}
        self.user_sessions = {}  # user_id -> set of session_ids
        self.agent_sessions = {}  # agent_id -> set of session_ids
        self.active_sessions = set()
        
        # Configuration
        self.session_ttl = 3600
        self.max_message_history = 100
    
    async def initialize(self) -> None:
        """Initialize mock session manager."""
        try:
            await asyncio.sleep(0.1)  # Simulate connection
            self.logger.info("Mock session manager initialized successfully")
            self.logger.info("This is a simulation - sessions are stored in memory only")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize mock session manager: {e}")
            raise MessageBrokerError(f"Mock session manager initialization failed: {e}")
    
    async def create_session(
        self,
        user_id: str,
        session_id: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new user session."""
        try:
            now = datetime.utcnow()
            
            session = {
                "user_id": user_id,
                "session_id": session_id,
                "agent_id": agent_id,
                "created_at": now,
                "last_activity": now,
                "context": context or {},
                "message_history": [],
                "is_active": True
            }
            
            # Store session
            self.sessions[session_id] = session
            
            # Update indices
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
            
            if agent_id not in self.agent_sessions:
                self.agent_sessions[agent_id] = set()
            self.agent_sessions[agent_id].add(session_id)
            
            self.active_sessions.add(session_id)
            
            self.logger.info(f"Created session {session_id} for user {user_id} with agent {agent_id}")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise MessageBrokerError(f"Session creation failed: {e}")
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session by ID."""
        return self.sessions.get(session_id)
    
    async def add_message_to_session(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> None:
        """Add message to session history."""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise MessageBrokerError(f"Session {session_id} not found")
            
            # Add timestamp to message
            message["timestamp"] = datetime.utcnow().isoformat()
            
            # Add to message history
            session["message_history"].append(message)
            
            # Trim history if too long
            if len(session["message_history"]) > self.max_message_history:
                session["message_history"] = session["message_history"][-self.max_message_history:]
            
            # Update last activity
            session["last_activity"] = datetime.utcnow()
            
            self.logger.debug(f"Added message to session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to add message to session {session_id}: {e}")
            raise MessageBrokerError(f"Message addition failed: {e}")
    
    async def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user."""
        return list(self.user_sessions.get(user_id, set()))
    
    async def get_agent_sessions(self, agent_id: str) -> List[str]:
        """Get all session IDs for an agent."""
        return list(self.agent_sessions.get(agent_id, set()))
    
    async def end_session(self, session_id: str) -> None:
        """End a session and clean up."""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return
            
            # Mark as inactive
            session["is_active"] = False
            
            # Remove from active sessions
            self.active_sessions.discard(session_id)
            
            self.logger.info(f"Ended session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to end session {session_id}: {e}")
            raise MessageBrokerError(f"Session cleanup failed: {e}")
    
    async def get_active_sessions(self) -> List[str]:
        """Get all active session IDs."""
        return list(self.active_sessions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session manager statistics."""
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len(self.active_sessions),
            "users_with_sessions": len(self.user_sessions),
            "agents_with_sessions": len(self.agent_sessions)
        }
    
    async def close(self) -> None:
        """Close session manager."""
        try:
            total_sessions = len(self.sessions)
            self.logger.info(f"Mock session manager closed. Total sessions: {total_sessions}")
            
        except Exception as e:
            self.logger.error(f"Error closing mock session manager: {e}")