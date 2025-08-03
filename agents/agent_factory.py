"""
Factory for creating and managing AI agents with different personalities and business rules.
Enhanced with OpenAI integration for intelligent responses.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.openai_integration import OpenAIIntegrationManager, OpenAIAgent
from agents.personalities import PersonalityManager
from agents.business_rules import BusinessRules
from utils.exceptions import AgentFactoryError
from config.settings import Settings

class Agent:
    """Simplified Agent class for standalone mode."""
    
    def __init__(self, agent_id: str, personality_type: str, business_domain: str):
        self.agent_id = agent_id
        self.personality_type = personality_type
        self.business_domain = business_domain
        self.is_active = False
        self.openai_agent = None
    
    async def initialize(self):
        """Initialize the agent."""
        self.is_active = True
    
    async def start(self):
        """Start the agent."""
        pass
    
    async def stop(self):
        """Stop the agent."""
        self.is_active = False
    
    async def health_check(self):
        """Check agent health."""
        return {"status": "healthy"}

class AgentFactory:
    """Factory for creating and managing AI agents with OpenAI integration."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("agent_factory")
        self.agents: Dict[str, Agent] = {}
        self.openai_agents: Dict[str, OpenAIAgent] = {}
        self.personality_manager = PersonalityManager()
        self.business_rules = BusinessRules()
        
        # Initialize OpenAI integration
        self.openai_manager = OpenAIIntegrationManager(settings)
    
    async def initialize(self) -> None:
        """Initialize the agent factory and OpenAI integration."""
        try:
            await self.openai_manager.initialize()
            self.logger.info("Agent factory initialized with OpenAI integration")
        except Exception as e:
            self.logger.error(f"Failed to initialize agent factory: {e}")
            raise AgentFactoryError(f"Factory initialization failed: {e}")
    
    def create_agent(self, agent_id: str, personality_type: str, business_domain: str) -> Agent:
        """Create a new agent with specified personality and business domain."""
        try:
            if agent_id in self.agents:
                raise AgentFactoryError(f"Agent {agent_id} already exists")
            
            # Validate personality type
            if not self.personality_manager.has_personality(personality_type):
                raise AgentFactoryError(f"Unknown personality type: {personality_type}")
            
            # Validate business domain
            if not self.business_rules.has_domain(business_domain):
                raise AgentFactoryError(f"Unknown business domain: {business_domain}")
            
            # Create OpenAI agent
            openai_agent = self.openai_manager.create_agent(
                agent_id, personality_type, business_domain
            )
            
            # Create main agent
            agent = Agent(
                agent_id=agent_id,
                personality_type=personality_type,
                business_domain=business_domain
            )
            
            # Link OpenAI agent to main agent
            agent.openai_agent = openai_agent
            
            self.agents[agent_id] = agent
            self.openai_agents[agent_id] = openai_agent
            
            self.logger.info(f"Created intelligent agent: {agent_id} ({personality_type}, {business_domain})")
            
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create agent {agent_id}: {e}")
            raise AgentFactoryError(f"Agent creation failed: {e}")
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an existing agent by ID."""
        return self.agents.get(agent_id)
    
    def get_openai_agent(self, agent_id: str) -> Optional[OpenAIAgent]:
        """Get OpenAI agent by ID."""
        return self.openai_agents.get(agent_id)
    
    async def process_user_message(self, agent_id: str, user_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user message through the specified agent."""
        try:
            openai_agent = self.get_openai_agent(agent_id)
            if not openai_agent:
                raise AgentFactoryError(f"Agent {agent_id} not found")
            
            # Process message through OpenAI agent
            response = await openai_agent.process_user_message(user_id, message, context)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process message for agent {agent_id}: {e}")
            return {
                "success": False,
                "agent_id": agent_id,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def generate_business_analysis(self, agent_id: str, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business analysis using the specified agent."""
        try:
            openai_agent = self.get_openai_agent(agent_id)
            if not openai_agent:
                raise AgentFactoryError(f"Agent {agent_id} not found")
            
            return await openai_agent.generate_business_analysis(user_id, data)
            
        except Exception as e:
            self.logger.error(f"Failed to generate analysis for agent {agent_id}: {e}")
            return {
                "success": False,
                "agent_id": agent_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all created agents."""
        return [
            {
                "agent_id": agent_id,
                "personality": agent.personality_type,
                "business_domain": agent.business_domain,
                "is_active": agent.is_active,
                "has_openai": agent_id in self.openai_agents
            }
            for agent_id, agent in self.agents.items()
        ]
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent."""
        try:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                # Stop agent if running
                if agent.is_active:
                    asyncio.create_task(agent.stop())
                
                del self.agents[agent_id]
                
                # Remove OpenAI agent
                if agent_id in self.openai_agents:
                    del self.openai_agents[agent_id]
                
                self.logger.info(f"Removed agent: {agent_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove agent {agent_id}: {e}")
            return False
    
    async def initialize_all_agents(self) -> None:
        """Initialize all created agents."""
        try:
            for agent_id, agent in self.agents.items():
                await agent.initialize()
                self.logger.info(f"Initialized agent: {agent_id}")
            
            self.logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise AgentFactoryError(f"Agent initialization failed: {e}")
    
    async def start_all_agents(self) -> None:
        """Start all agents."""
        try:
            for agent_id, agent in self.agents.items():
                await agent.start()
                self.logger.info(f"Started agent: {agent_id}")
            
            self.logger.info(f"Started {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to start agents: {e}")
            raise AgentFactoryError(f"Agent startup failed: {e}")
    
    async def stop_all_agents(self) -> None:
        """Stop all agents."""
        try:
            for agent_id, agent in self.agents.items():
                await agent.stop()
                self.logger.info(f"Stopped agent: {agent_id}")
            
            self.logger.info(f"Stopped {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to stop agents: {e}")
            raise AgentFactoryError(f"Agent shutdown failed: {e}")
    
    def get_conversation_summary(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """Get conversation summary for user with specific agent."""
        openai_agent = self.get_openai_agent(agent_id)
        if openai_agent:
            return openai_agent.get_conversation_summary(user_id)
        return {"error": "Agent not found"}
    
    def clear_conversation(self, agent_id: str, user_id: str) -> bool:
        """Clear conversation history for user with specific agent."""
        openai_agent = self.get_openai_agent(agent_id)
        if openai_agent:
            return openai_agent.clear_conversation(user_id)
        return False
    
    def get_factory_stats(self) -> Dict[str, Any]:
        """Get factory statistics."""
        personality_counts = {}
        domain_counts = {}
        active_count = 0
        
        for agent in self.agents.values():
            # Count personalities
            personality = agent.personality_type
            personality_counts[personality] = personality_counts.get(personality, 0) + 1
            
            # Count domains
            domain = agent.business_domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Count active agents
            if agent.is_active:
                active_count += 1
        
        return {
            "total_agents": len(self.agents),
            "active_agents": active_count,
            "openai_agents": len(self.openai_agents),
            "personalities": personality_counts,
            "business_domains": domain_counts,
            "available_personalities": self.personality_manager.list_personalities(),
            "available_domains": self.business_rules.list_domains()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents and OpenAI integration."""
        try:
            # Check OpenAI integration
            openai_health = await self.openai_manager.health_check()
            
            # Check individual agents
            agent_health = {}
            for agent_id, agent in self.agents.items():
                try:
                    health = await agent.health_check()
                    agent_health[agent_id] = health
                except Exception as e:
                    agent_health[agent_id] = {"status": "unhealthy", "error": str(e)}
            
            return {
                "factory_status": "healthy",
                "openai_integration": openai_health,
                "agents": agent_health,
                "total_agents": len(self.agents),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "factory_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Pre-configured agent templates
async def create_default_agents(factory: AgentFactory) -> List[str]:
    """Create default agents for the system."""
    default_agents = [
        {
            "agent_id": "agent_alpha",
            "personality": "analytical",
            "domain": "financial_advisor"
        },
        {
            "agent_id": "agent_beta", 
            "personality": "creative",
            "domain": "content_creator"
        }
    ]
    
    created_agents = []
    for config in default_agents:
        try:
            agent = factory.create_agent(
                config["agent_id"],
                config["personality"],
                config["domain"]
            )
            created_agents.append(config["agent_id"])
        except Exception as e:
            factory.logger.error(f"Failed to create default agent {config['agent_id']}: {e}")
    
    return created_agents
