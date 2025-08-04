"""
Base AI Agent implementation with LangGraph workflow integration.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from langgraph.graph import StateGraph
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel

from core.workflow import WorkflowEngine
from core.database import DatabaseManager
from core.mcp_client import MCPClient
from core.rag_system import RAGSystem
from core.message_broker import RabbitMQBroker
from core.session_manager import RedisSessionManager
from models.schemas import UserInteraction, AgentResponse, AgentState
from utils.exceptions import AgentError, DatabaseError, MCPError

class Agent:
    """Base AI Agent with LangGraph workflow and MCP integration."""
    
    def __init__(
        self,
        agent_id: str,
        personality: str,
        business_rules: str,
        database_config: Dict[str, Any],
        mcp_servers: List[str],
        message_broker: Optional[RabbitMQBroker] = None,
        session_manager: Optional[RedisSessionManager] = None
    ):
        self.agent_id = agent_id
        self.personality = personality
        self.business_rules = business_rules
        self.logger = logging.getLogger(f"agent_{agent_id}")
        
        # Initialize components
        self.database = DatabaseManager(database_config)
        self.mcp_client = MCPClient(mcp_servers)
        self.rag_system = RAGSystem(self.database, self.mcp_client)
        self.workflow = WorkflowEngine(self)
        self.message_broker = message_broker
        self.session_manager = session_manager
        
        # Agent state
        self.state = AgentState(
            user_id=None,
            session_id=None,
            messages=[],
            context={}
        )
        
        # LangGraph workflow
        self.graph = self._build_workflow_graph()
        
    async def initialize(self) -> None:
        """Initialize agent components."""
        try:
            await self.database.initialize()
            await self.mcp_client.connect()
            await self.rag_system.initialize()
            
            self.logger.info(f"Agent {self.agent_id} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            raise AgentError(f"Agent initialization failed: {e}")
    
    def _build_workflow_graph(self):
        """Build the LangGraph workflow graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("receive_input", self.workflow.receive_input)
        workflow.add_node("notify_user", self.workflow.notify_user)
        workflow.add_node("query_database", self.workflow.query_database)
        workflow.add_node("apply_business_logic", self.workflow.apply_business_logic)
        workflow.add_node("generate_response", self.workflow.generate_response)
        workflow.add_node("send_response", self.workflow.send_response)
        
        # Define edges
        workflow.set_entry_point("receive_input")
        workflow.add_edge("receive_input", "notify_user")
        workflow.add_edge("notify_user", "query_database")
        workflow.add_edge("query_database", "apply_business_logic")
        workflow.add_edge("apply_business_logic", "generate_response")
        workflow.add_edge("generate_response", "send_response")
        
        return workflow.compile()
    
    async def process_prompt(self, prompt: str, user_id: str, session_id: str) -> AgentResponse:
        """Process user prompt through the workflow."""
        try:
            # Update agent state
            self.state.messages.append(HumanMessage(content=prompt))
            self.state.user_id = user_id
            self.state.session_id = session_id
            # Set current task in metadata since current_task doesn't exist in AgentState
            if not hasattr(self.state, 'metadata'):
                self.state.metadata = {}
            self.state.metadata["current_task"] = "processing_prompt"
            
            # Log interaction
            interaction = UserInteraction(
                user_id=user_id,
                session_id=session_id,
                agent_id=self.agent_id,
                prompt=prompt,
                timestamp=datetime.utcnow()
            )
            
            await self.database.save_interaction(interaction)
            
            # Run workflow
            result = await self.graph.ainvoke(self.state)
            
            # Extract response - handle both dict and AgentState returns
            if hasattr(result, 'messages'):
                messages = result.messages
            elif isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
            else:
                messages = self.state.messages
            
            if messages and isinstance(messages[-1], AIMessage):
                response_content = messages[-1].content
            else:
                response_content = "I apologize, but I couldn't process your request."
            
            # Create response
            context_metadata = {}
            if hasattr(result, 'context'):
                context_metadata = result.context
            elif isinstance(result, dict) and 'context' in result:
                context_metadata = result['context']
            else:
                # Use metadata instead of context as context doesn't exist in AgentState
                context_metadata = getattr(self.state, 'metadata', {})
                
            response = AgentResponse(
                agent_id=self.agent_id,
                user_id=user_id,
                session_id=session_id,
                content=response_content,
                timestamp=datetime.utcnow(),
                metadata=context_metadata
            )
            
            # Save response
            await self.database.save_response(response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing prompt: {e}")
            raise AgentError(f"Failed to process prompt: {e}")
    
    async def start(self) -> None:
        """Start the agent processing loop."""
        await self.initialize()
        
        self.logger.info(f"Agent {self.agent_id} started and ready for processing")
        
        # Keep agent alive
        try:
            while True:
                await asyncio.sleep(1)
                # Here you would implement your message queue or API endpoint listening
                # For now, we'll just keep the agent alive
                
        except asyncio.CancelledError:
            self.logger.info(f"Agent {self.agent_id} shutdown requested")
        except Exception as e:
            self.logger.error(f"Agent {self.agent_id} error: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        try:
            await self.mcp_client.disconnect()
            await self.database.close()
            self.logger.info(f"Agent {self.agent_id} cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
