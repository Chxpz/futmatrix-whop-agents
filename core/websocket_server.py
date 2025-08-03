"""
WebSocket server for real-time agent-user communication.
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Optional
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol

from core.message_broker import RabbitMQBroker, Message
from core.session_manager import RedisSessionManager
from utils.exceptions import WebSocketError


class WebSocketManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(
        self,
        message_broker: RabbitMQBroker,
        session_manager: RedisSessionManager
    ):
        self.message_broker = message_broker
        self.session_manager = session_manager
        self.logger = logging.getLogger("websocket_manager")
        
        # Connection tracking
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.agent_connections: Dict[str, Set[str]] = {}  # agent_id -> connection_ids
        
        # Message handlers
        self.message_handlers = {
            "user_prompt": self._handle_user_prompt,
            "agent_response": self._handle_agent_response,
            "ping": self._handle_ping,
            "subscribe": self._handle_subscribe,
            "unsubscribe": self._handle_unsubscribe
        }
    
    async def register_connection(
        self,
        websocket: WebSocketServerProtocol,
        user_id: str,
        connection_type: str = "user"
    ) -> str:
        """Register a new WebSocket connection."""
        connection_id = str(uuid.uuid4())
        
        try:
            self.active_connections[connection_id] = websocket
            
            if connection_type == "user":
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
            elif connection_type == "agent":
                if user_id not in self.agent_connections:
                    self.agent_connections[user_id] = set()
                self.agent_connections[user_id].add(connection_id)
            
            self.logger.info(f"Registered {connection_type} connection {connection_id} for {user_id}")
            
            # Send connection confirmation
            await self._send_to_connection(connection_id, {
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return connection_id
            
        except Exception as e:
            self.logger.error(f"Failed to register connection: {e}")
            raise WebSocketError(f"Connection registration failed: {e}")
    
    async def unregister_connection(self, connection_id: str) -> None:
        """Unregister a WebSocket connection."""
        try:
            if connection_id in self.active_connections:
                # Remove from active connections
                del self.active_connections[connection_id]
                
                # Remove from user connections
                for user_id, conn_ids in self.user_connections.items():
                    if connection_id in conn_ids:
                        conn_ids.remove(connection_id)
                        if not conn_ids:
                            del self.user_connections[user_id]
                        break
                
                # Remove from agent connections
                for agent_id, conn_ids in self.agent_connections.items():
                    if connection_id in conn_ids:
                        conn_ids.remove(connection_id)
                        if not conn_ids:
                            del self.agent_connections[agent_id]
                        break
                
                self.logger.info(f"Unregistered connection {connection_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to unregister connection {connection_id}: {e}")
    
    async def handle_message(
        self,
        connection_id: str,
        message_data: Dict
    ) -> None:
        """Handle incoming WebSocket message."""
        try:
            message_type = message_data.get("type")
            if not message_type:
                await self._send_error(connection_id, "Missing message type")
                return
            
            handler = self.message_handlers.get(message_type)
            if not handler:
                await self._send_error(connection_id, f"Unknown message type: {message_type}")
                return
            
            await handler(connection_id, message_data)
            
        except Exception as e:
            self.logger.error(f"Error handling message from {connection_id}: {e}")
            await self._send_error(connection_id, f"Message handling error: {str(e)}")
    
    async def _handle_user_prompt(
        self,
        connection_id: str,
        message_data: Dict
    ) -> None:
        """Handle user prompt message."""
        try:
            # Validate required fields
            required_fields = ["user_id", "agent_id", "content", "session_id"]
            for field in required_fields:
                if field not in message_data:
                    await self._send_error(connection_id, f"Missing field: {field}")
                    return
            
            # Create message
            message = Message(
                id=str(uuid.uuid4()),
                user_id=message_data["user_id"],
                agent_id=message_data["agent_id"],
                content=message_data["content"],
                message_type="user_prompt",
                timestamp=datetime.utcnow(),
                session_id=message_data["session_id"],
                metadata=message_data.get("metadata", {})
            )
            
            # Add to session
            await self.session_manager.add_message_to_session(
                message.session_id,
                {
                    "id": message.id,
                    "type": "user_prompt",
                    "content": message.content,
                    "user_id": message.user_id
                }
            )
            
            # Publish to message broker
            self.message_broker.publish_user_prompt(message)
            
            # Send acknowledgment
            await self._send_to_connection(connection_id, {
                "type": "message_received",
                "message_id": message.id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Processed user prompt {message.id} from connection {connection_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling user prompt: {e}")
            await self._send_error(connection_id, f"Failed to process prompt: {str(e)}")
    
    async def _handle_agent_response(
        self,
        connection_id: str,
        message_data: Dict
    ) -> None:
        """Handle agent response message."""
        try:
            # Validate required fields
            required_fields = ["user_id", "agent_id", "content", "session_id"]
            for field in required_fields:
                if field not in message_data:
                    await self._send_error(connection_id, f"Missing field: {field}")
                    return
            
            # Create message
            message = Message(
                id=str(uuid.uuid4()),
                user_id=message_data["user_id"],
                agent_id=message_data["agent_id"],
                content=message_data["content"],
                message_type="agent_response",
                timestamp=datetime.utcnow(),
                session_id=message_data["session_id"],
                metadata=message_data.get("metadata", {})
            )
            
            # Add to session
            await self.session_manager.add_message_to_session(
                message.session_id,
                {
                    "id": message.id,
                    "type": "agent_response",
                    "content": message.content,
                    "agent_id": message.agent_id
                }
            )
            
            # Publish to message broker
            self.message_broker.publish_agent_response(message)
            
            # Send to user connections
            await self._send_to_user(message.user_id, {
                "type": "agent_response",
                "message_id": message.id,
                "agent_id": message.agent_id,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "session_id": message.session_id
            })
            
            self.logger.info(f"Processed agent response {message.id} from connection {connection_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling agent response: {e}")
            await self._send_error(connection_id, f"Failed to process response: {str(e)}")
    
    async def _handle_ping(
        self,
        connection_id: str,
        message_data: Dict
    ) -> None:
        """Handle ping message."""
        await self._send_to_connection(connection_id, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_subscribe(
        self,
        connection_id: str,
        message_data: Dict
    ) -> None:
        """Handle subscription to agent updates."""
        agent_id = message_data.get("agent_id")
        if not agent_id:
            await self._send_error(connection_id, "Missing agent_id for subscription")
            return
        
        # Add connection to agent subscriptions
        if agent_id not in self.agent_connections:
            self.agent_connections[agent_id] = set()
        self.agent_connections[agent_id].add(connection_id)
        
        await self._send_to_connection(connection_id, {
            "type": "subscribed",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_unsubscribe(
        self,
        connection_id: str,
        message_data: Dict
    ) -> None:
        """Handle unsubscription from agent updates."""
        agent_id = message_data.get("agent_id")
        if not agent_id:
            await self._send_error(connection_id, "Missing agent_id for unsubscription")
            return
        
        # Remove connection from agent subscriptions
        if agent_id in self.agent_connections:
            self.agent_connections[agent_id].discard(connection_id)
            if not self.agent_connections[agent_id]:
                del self.agent_connections[agent_id]
        
        await self._send_to_connection(connection_id, {
            "type": "unsubscribed",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _send_to_connection(
        self,
        connection_id: str,
        message: Dict
    ) -> None:
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                await self.unregister_connection(connection_id)
            except Exception as e:
                self.logger.error(f"Error sending to connection {connection_id}: {e}")
    
    async def _send_to_user(self, user_id: str, message: Dict) -> None:
        """Send message to all user connections."""
        if user_id in self.user_connections:
            tasks = []
            for connection_id in list(self.user_connections[user_id]):
                tasks.append(self._send_to_connection(connection_id, message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_to_agent_subscribers(self, agent_id: str, message: Dict) -> None:
        """Send message to all agent subscribers."""
        if agent_id in self.agent_connections:
            tasks = []
            for connection_id in list(self.agent_connections[agent_id]):
                tasks.append(self._send_to_connection(connection_id, message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_error(self, connection_id: str, error_message: str) -> None:
        """Send error message to connection."""
        await self._send_to_connection(connection_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def broadcast_notification(self, message: Dict) -> None:
        """Broadcast notification to all connections."""
        tasks = []
        for connection_id in list(self.active_connections.keys()):
            tasks.append(self._send_to_connection(connection_id, {
                "type": "notification",
                **message,
                "timestamp": datetime.utcnow().isoformat()
            }))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


async def websocket_handler(
    websocket: WebSocketServerProtocol,
    path: str,
    websocket_manager: WebSocketManager
) -> None:
    """Handle WebSocket connections."""
    connection_id = None
    
    try:
        # Wait for authentication message
        auth_message = await websocket.recv()
        auth_data = json.loads(auth_message)
        
        user_id = auth_data.get("user_id")
        connection_type = auth_data.get("type", "user")
        
        if not user_id:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Missing user_id in authentication"
            }))
            return
        
        # Register connection
        connection_id = await websocket_manager.register_connection(
            websocket, user_id, connection_type
        )
        
        # Handle messages
        async for message in websocket:
            try:
                message_data = json.loads(message)
                await websocket_manager.handle_message(connection_id, message_data)
            except json.JSONDecodeError:
                await websocket_manager._send_error(connection_id, "Invalid JSON message")
            except Exception as e:
                logging.getLogger("websocket_handler").error(f"Message handling error: {e}")
                await websocket_manager._send_error(connection_id, "Message processing error")
    
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logging.getLogger("websocket_handler").error(f"WebSocket handler error: {e}")
    finally:
        if connection_id:
            await websocket_manager.unregister_connection(connection_id)


class WebSocketServer:
    """WebSocket server for real-time communication."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        message_broker: RabbitMQBroker = None,
        session_manager: RedisSessionManager = None
    ):
        self.host = host
        self.port = port
        self.message_broker = message_broker
        self.session_manager = session_manager
        self.websocket_manager = WebSocketManager(message_broker, session_manager)
        self.logger = logging.getLogger("websocket_server")
        self.server = None
    
    async def start(self) -> None:
        """Start WebSocket server."""
        try:
            self.server = await websockets.serve(
                lambda ws, path: websocket_handler(ws, path, self.websocket_manager),
                self.host,
                self.port
            )
            
            self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise WebSocketError(f"Server startup failed: {e}")
    
    async def stop(self) -> None:
        """Stop WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("WebSocket server stopped")