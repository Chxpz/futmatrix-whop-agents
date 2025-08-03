"""
RabbitMQ message broker implementation for agent-user communication.
"""
import asyncio
import json
import logging
import pika
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

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


class RabbitMQBroker:
    """RabbitMQ message broker for handling agent-user communication."""
    
    def __init__(self, rabbitmq_url: str = "amqp://localhost"):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger("message_broker")
        
        # Queue configurations
        self.queues = {
            "user_prompts": "user_prompts_queue",
            "agent_responses": "agent_responses_queue",
            "notifications": "notifications_queue",
            "system_events": "system_events_queue"
        }
        
        # Exchange configurations
        self.exchanges = {
            "direct": "agent_direct_exchange",
            "fanout": "agent_fanout_exchange",
            "topic": "agent_topic_exchange"
        }
        
        self.message_handlers = {}
    
    async def initialize(self) -> None:
        """Initialize RabbitMQ connection and setup queues."""
        try:
            # Create connection
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            
            # Declare exchanges
            for exchange_type, exchange_name in self.exchanges.items():
                self.channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type=exchange_type,
                    durable=True
                )
            
            # Declare queues
            for queue_name in self.queues.values():
                self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind queues to exchanges
            self._bind_queues()
            
            self.logger.info("RabbitMQ broker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RabbitMQ broker: {e}")
            raise MessageBrokerError(f"Broker initialization failed: {e}")
    
    def _bind_queues(self) -> None:
        """Bind queues to appropriate exchanges."""
        # Bind user prompts to direct exchange
        self.channel.queue_bind(
            exchange=self.exchanges["direct"],
            queue=self.queues["user_prompts"],
            routing_key="user.prompt"
        )
        
        # Bind agent responses to direct exchange
        self.channel.queue_bind(
            exchange=self.exchanges["direct"],
            queue=self.queues["agent_responses"],
            routing_key="agent.response"
        )
        
        # Bind notifications to fanout exchange
        self.channel.queue_bind(
            exchange=self.exchanges["fanout"],
            queue=self.queues["notifications"]
        )
        
        # Bind system events to topic exchange
        self.channel.queue_bind(
            exchange=self.exchanges["topic"],
            queue=self.queues["system_events"],
            routing_key="system.*"
        )
    
    def publish_user_prompt(self, message: Message) -> None:
        """Publish user prompt to the queue."""
        try:
            message_body = json.dumps({
                "id": message.id,
                "user_id": message.user_id,
                "agent_id": message.agent_id,
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.timestamp.isoformat(),
                "session_id": message.session_id,
                "metadata": message.metadata
            })
            
            self.channel.basic_publish(
                exchange=self.exchanges["direct"],
                routing_key="user.prompt",
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    correlation_id=message.id,
                    user_id=message.user_id
                )
            )
            
            self.logger.info(f"Published user prompt {message.id} for agent {message.agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish user prompt: {e}")
            raise MessageBrokerError(f"Failed to publish message: {e}")
    
    def publish_agent_response(self, message: Message) -> None:
        """Publish agent response to the queue."""
        try:
            message_body = json.dumps({
                "id": message.id,
                "user_id": message.user_id,
                "agent_id": message.agent_id,
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.timestamp.isoformat(),
                "session_id": message.session_id,
                "metadata": message.metadata
            })
            
            self.channel.basic_publish(
                exchange=self.exchanges["direct"],
                routing_key="agent.response",
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    correlation_id=message.id,
                    user_id=message.user_id
                )
            )
            
            self.logger.info(f"Published agent response {message.id} from agent {message.agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish agent response: {e}")
            raise MessageBrokerError(f"Failed to publish response: {e}")
    
    def publish_notification(self, message: Message) -> None:
        """Publish notification to all subscribers."""
        try:
            message_body = json.dumps({
                "id": message.id,
                "user_id": message.user_id,
                "agent_id": message.agent_id,
                "content": message.content,
                "message_type": message.message_type,
                "timestamp": message.timestamp.isoformat(),
                "session_id": message.session_id,
                "metadata": message.metadata
            })
            
            self.channel.basic_publish(
                exchange=self.exchanges["fanout"],
                routing_key="",  # Fanout ignores routing key
                body=message_body,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            self.logger.info(f"Published notification {message.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish notification: {e}")
            raise MessageBrokerError(f"Failed to publish notification: {e}")
    
    def consume_user_prompts(self, callback: Callable) -> None:
        """Start consuming user prompts."""
        try:
            def wrapper(ch, method, properties, body):
                try:
                    message_data = json.loads(body)
                    message = Message(
                        id=message_data["id"],
                        user_id=message_data["user_id"],
                        agent_id=message_data["agent_id"],
                        content=message_data["content"],
                        message_type=message_data["message_type"],
                        timestamp=datetime.fromisoformat(message_data["timestamp"]),
                        session_id=message_data["session_id"],
                        metadata=message_data["metadata"]
                    )
                    
                    callback(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    self.logger.error(f"Error processing user prompt: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queues["user_prompts"],
                on_message_callback=wrapper
            )
            
            self.logger.info("Started consuming user prompts")
            
        except Exception as e:
            self.logger.error(f"Failed to start consuming user prompts: {e}")
            raise MessageBrokerError(f"Failed to start consuming: {e}")
    
    def consume_agent_responses(self, callback: Callable) -> None:
        """Start consuming agent responses."""
        try:
            def wrapper(ch, method, properties, body):
                try:
                    message_data = json.loads(body)
                    message = Message(
                        id=message_data["id"],
                        user_id=message_data["user_id"],
                        agent_id=message_data["agent_id"],
                        content=message_data["content"],
                        message_type=message_data["message_type"],
                        timestamp=datetime.fromisoformat(message_data["timestamp"]),
                        session_id=message_data["session_id"],
                        metadata=message_data["metadata"]
                    )
                    
                    callback(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    self.logger.error(f"Error processing agent response: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queues["agent_responses"],
                on_message_callback=wrapper
            )
            
            self.logger.info("Started consuming agent responses")
            
        except Exception as e:
            self.logger.error(f"Failed to start consuming agent responses: {e}")
            raise MessageBrokerError(f"Failed to start consuming responses: {e}")
    
    def start_consuming(self) -> None:
        """Start consuming messages from all queues."""
        try:
            self.logger.info("Starting message consumption...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            self.logger.info("Stopping message consumption...")
            self.channel.stop_consuming()
    
    def close(self) -> None:
        """Close broker connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                self.logger.info("RabbitMQ connection closed")
                
        except Exception as e:
            self.logger.error(f"Error closing RabbitMQ connection: {e}")