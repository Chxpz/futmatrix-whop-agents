"""
LangGraph workflow implementation for AI agents.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from langchain.schema import AIMessage, HumanMessage
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate

from agents.personalities import PersonalityManager
from agents.business_rules import BusinessRuleEngine
from utils.exceptions import WorkflowError

class AgentWorkflow:
    """LangGraph workflow implementation for agent processing."""
    
    def __init__(self, agent):
        self.agent = agent
        self.logger = logging.getLogger(f"workflow_{agent.agent_id}")
        self.personality_manager = PersonalityManager()
        self.business_engine = BusinessRuleEngine()
    
    async def receive_input(self, state):
        """Receive and validate user input."""
        try:
            self.logger.info(f"Receiving input for session {state.session_id}")
            
            # Validate input
            if not state.messages or not state.user_id:
                raise WorkflowError("Invalid input: missing messages or user_id")
            
            # Update context
            state.context.update({
                "input_received_at": datetime.utcnow().isoformat(),
                "personality": self.agent.personality,
                "business_rules": self.agent.business_rules
            })
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error receiving input: {e}")
            raise WorkflowError(f"Failed to receive input: {e}")
    
    async def notify_user(self, state):
        """Notify user that processing has started."""
        try:
            self.logger.info(f"Notifying user {state.user_id} of processing start")
            
            # Get personality-specific notification
            notification = self.personality_manager.get_processing_notification(
                self.agent.personality
            )
            
            # Add notification to messages
            state.messages.append(AIMessage(content=notification))
            
            # Update context
            state.context["notification_sent"] = True
            state.context["notification_content"] = notification
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error notifying user: {e}")
            raise WorkflowError(f"Failed to notify user: {e}")
    
    async def query_database(self, state):
        """Query database for relevant information."""
        try:
            self.logger.info(f"Querying database for session {state.session_id}")
            
            # Get user's latest message
            latest_prompt = None
            for msg in reversed(state.messages):
                if isinstance(msg, HumanMessage):
                    latest_prompt = msg.content
                    break
            
            if not latest_prompt:
                raise WorkflowError("No user prompt found")
            
            # Query relevant data
            user_history = await self.agent.database.get_user_history(
                state.user_id, limit=10
            )
            
            # Query RAG system
            rag_results = await self.agent.rag_system.query(
                latest_prompt, top_k=5
            )
            
            # Update context with database results
            state.context.update({
                "user_history": user_history,
                "rag_results": rag_results,
                "database_queried_at": datetime.utcnow().isoformat()
            })
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error querying database: {e}")
            raise WorkflowError(f"Failed to query database: {e}")
    
    async def apply_business_logic(self, state):
        """Apply business rules and logic processing."""
        try:
            self.logger.info(f"Applying business logic for agent {self.agent.agent_id}")
            
            # Get latest user prompt
            latest_prompt = None
            for msg in reversed(state.messages):
                if isinstance(msg, HumanMessage):
                    latest_prompt = msg.content
                    break
            
            # Apply business rules
            business_result = await self.business_engine.process(
                business_rule_type=self.agent.business_rules,
                prompt=latest_prompt or "",
                context=state.context,
                user_id=state.user_id or ""
            )
            
            # Update context with business logic results
            state.context.update({
                "business_logic_result": business_result,
                "business_logic_applied_at": datetime.utcnow().isoformat()
            })
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error applying business logic: {e}")
            raise WorkflowError(f"Failed to apply business logic: {e}")
    
    async def generate_response(self, state):
        """Generate AI response based on processed information."""
        try:
            self.logger.info(f"Generating response for session {state.session_id}")
            
            # Get personality-specific prompt template
            prompt_template = self.personality_manager.get_response_template(
                self.agent.personality
            )
            
            # Prepare context for response generation
            response_context = {
                "user_prompt": state.messages[-2].content if len(state.messages) >= 2 else "",
                "user_history": state.context.get("user_history", []),
                "rag_results": state.context.get("rag_results", []),
                "business_result": state.context.get("business_logic_result", {}),
                "personality": self.agent.personality
            }
            
            # Use MCP tools for response generation if available
            try:
                mcp_response = await self.agent.mcp_client.generate_response(
                    prompt_template.format(**response_context)
                )
                if mcp_response:
                    response_content = mcp_response
                else:
                    # Fallback to template-based response
                    response_content = self._generate_fallback_response(response_context)
            except Exception as mcp_error:
                self.logger.debug(f"MCP response generation not available: {mcp_error}")
                # Fallback to template-based response
                response_content = self._generate_fallback_response(response_context)
            
            # Add response to messages
            state.messages.append(AIMessage(content=response_content))
            
            # Update context
            state.context.update({
                "response_generated_at": datetime.utcnow().isoformat(),
                "response_method": "mcp" if "mcp_response" in locals() else "fallback"
            })
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise WorkflowError(f"Failed to generate response: {e}")
    
    async def send_response(self, state):
        """Send final response to user."""
        try:
            self.logger.info(f"Sending response to user {state.user_id}")
            
            # Mark task as completed
            state.current_task = "completed"
            
            # Update context
            state.context.update({
                "response_sent_at": datetime.utcnow().isoformat(),
                "processing_completed": True
            })
            
            return state
            
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")
            raise WorkflowError(f"Failed to send response: {e}")
    
    def _generate_fallback_response(self, context: Dict[str, Any]) -> str:
        """Generate a fallback response when MCP is unavailable."""
        personality = context.get("personality", "neutral")
        
        fallback_responses = {
            "analytical": "Based on the available data and analysis, I can provide you with a structured response to your query.",
            "creative": "Let me craft a thoughtful and creative response to your interesting question!",
            "helpful": "I'm here to help! Let me provide you with the best assistance I can based on your request.",
            "professional": "Thank you for your inquiry. I'll provide you with a comprehensive professional response."
        }
        
        return fallback_responses.get(personality, "I'll do my best to assist you with your request.")
