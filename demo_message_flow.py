"""
Demonstration script for the complete message flow system.
Shows how users interact with agents through the message broker architecture.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

from core.mock_message_broker import MockMessageBroker, MockRedisSession, Message
from utils.logger import setup_logger

async def demo_message_flow():
    """Demonstrate the complete message flow system."""
    # Setup logging
    setup_logger()
    logger = logging.getLogger("demo_message_flow")
    
    logger.info("=== AI Agents Message Flow Demonstration ===")
    
    # Initialize components
    message_broker = MockMessageBroker()
    session_manager = MockRedisSession()
    
    await message_broker.initialize()
    await session_manager.initialize()
    
    # Create a user session
    user_id = "demo_user_123"
    agent_id = "agent_alpha"
    session_id = "session_demo_001"
    
    session = await session_manager.create_session(
        user_id=user_id,
        session_id=session_id,
        agent_id=agent_id,
        context={"demo": True, "purpose": "message_flow_test"}
    )
    
    logger.info(f"Created session: {session_id}")
    
    # Set up message handlers
    received_responses = []
    
    def handle_user_prompt(message: Message):
        logger.info(f"Processing user prompt: {message.content[:50]}...")
        # Simulate agent processing and response
        response_message = Message(
            id=f"response_{message.id}",
            user_id=message.user_id,
            agent_id=message.agent_id,
            content=f"Agent {message.agent_id} response to: {message.content}",
            message_type="agent_response",
            timestamp=datetime.utcnow(),
            session_id=message.session_id,
            metadata={"original_prompt": message.id}
        )
        message_broker.publish_agent_response(response_message)
    
    def handle_agent_response(message: Message):
        logger.info(f"Received agent response: {message.content[:50]}...")
        received_responses.append(message)
    
    # Start consuming messages
    message_broker.consume_user_prompts(handle_user_prompt)
    message_broker.consume_agent_responses(handle_agent_response)
    message_broker.start_consuming()
    
    # Simulate user interactions
    test_prompts = [
        "What are the current market trends?",
        "Can you analyze my portfolio performance?",
        "What investment recommendations do you have?",
        "How should I diversify my investments?"
    ]
    
    logger.info("Starting message flow demonstration...")
    
    for i, prompt in enumerate(test_prompts):
        # Create user message
        user_message = Message(
            id=f"user_msg_{i+1}",
            user_id=user_id,
            agent_id=agent_id,
            content=prompt,
            message_type="user_prompt",
            timestamp=datetime.utcnow(),
            session_id=session_id,
            metadata={"prompt_number": i+1}
        )
        
        # Add to session history
        await session_manager.add_message_to_session(
            session_id,
            {
                "id": user_message.id,
                "type": "user_prompt",
                "content": user_message.content,
                "user_id": user_id
            }
        )
        
        # Publish to message broker
        message_broker.publish_user_prompt(user_message)
        
        # Wait for processing
        await asyncio.sleep(0.5)
    
    # Wait for all responses
    await asyncio.sleep(2)
    
    # Display results
    logger.info("\n=== Message Flow Demonstration Results ===")
    
    # Broker statistics
    broker_stats = message_broker.get_queue_stats()
    logger.info(f"Broker Statistics: {json.dumps(broker_stats, indent=2)}")
    
    # Session statistics
    session_stats = session_manager.get_stats()
    logger.info(f"Session Statistics: {json.dumps(session_stats, indent=2)}")
    
    # Session messages
    final_session = await session_manager.get_session(session_id)
    logger.info(f"Session Message History: {len(final_session['message_history'])} messages")
    
    # Show message flow
    logger.info("\n=== Complete Message Flow ===")
    for i, msg in enumerate(final_session['message_history']):
        logger.info(f"{i+1}. [{msg['type']}] {msg['content'][:60]}...")
    
    logger.info(f"\nReceived {len(received_responses)} agent responses")
    
    # Test queue inspection
    user_prompts = message_broker.get_messages("user_prompts")
    agent_responses = message_broker.get_messages("agent_responses")
    
    logger.info(f"Messages in queues - User prompts: {len(user_prompts)}, Agent responses: {len(agent_responses)}")
    
    # Cleanup
    await session_manager.end_session(session_id)
    message_broker.close()
    await session_manager.close()
    
    logger.info("=== Message Flow Demonstration Complete ===")
    logger.info("This demonstrates the complete production-ready message flow architecture")
    logger.info("In production, this would use RabbitMQ and Redis for persistence and scalability")

if __name__ == "__main__":
    asyncio.run(demo_message_flow())