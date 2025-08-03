"""
Simplified Standalone AI Agents System - Core functionality only
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from openai import AsyncOpenAI
from config.settings import Settings
from agents.personalities import PersonalityManager
from agents.business_rules import BusinessRules
from utils.logger import setup_logger

class SimpleAgent:
    """Simplified AI agent with OpenAI integration."""
    
    def __init__(self, agent_id: str, personality_type: str, business_domain: str, openai_key: str):
        self.agent_id = agent_id
        self.personality_type = personality_type
        self.business_domain = business_domain
        self.logger = logging.getLogger(f"agent_{agent_id}")
        
        # OpenAI client
        self.openai_client = AsyncOpenAI(api_key=openai_key)
        
        # Conversation storage
        self.conversations = {}
        
        # Personality and business context
        self.personality_manager = PersonalityManager()
        self.business_rules = BusinessRules()
        
        self.personality = self.personality_manager.get_personality(personality_type)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the agent."""
        return f"""You are {self.agent_id}, an AI assistant with the following profile:

PERSONALITY: {self.personality_type.upper()}
- {self.personality.get('description', 'Professional and helpful assistant')}
- Traits: {', '.join(self.personality.get('traits', ['Professional', 'Helpful']))}
- Tone: {self.personality.get('tone', 'professional and friendly')}

BUSINESS SPECIALIZATION: {self.business_domain.upper()}
- {self.business_rules.domains.get(self.business_domain, 'General assistance')}

INSTRUCTIONS:
1. Always respond in character with your personality
2. Apply your business expertise to provide valuable insights
3. Be helpful, accurate, and professional
4. Ask clarifying questions when needed
5. Provide actionable advice when appropriate

Remember: You are a backend AI agent providing intelligent responses for a frontend application."""
    
    async def process_message(self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user message and generate response."""
        try:
            self.logger.info(f"Processing message from user {user_id}")
            
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self._build_system_prompt()}]
            
            # Add conversation history
            if user_id in self.conversations:
                for msg in self.conversations[user_id][-5:]:  # Last 5 messages
                    messages.append(msg)
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Add context if provided
            if context:
                context_msg = f"Additional context: {json.dumps(context)}"
                messages.append({"role": "system", "content": context_msg})
            
            # Generate response
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                temperature=0.7 if self.personality_type == "creative" else 0.3
            )
            
            assistant_response = response.choices[0].message.content
            
            # Store conversation
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            self.conversations[user_id].extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_response}
            ])
            
            # Keep only recent conversation
            if len(self.conversations[user_id]) > 20:
                self.conversations[user_id] = self.conversations[user_id][-20:]
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "user_id": user_id,
                "response": assistant_response,
                "personality": self.personality_type,
                "business_domain": self.business_domain,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "agent_id": self.agent_id,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class SimpleAgentSystem:
    """Simple system to manage multiple AI agents."""
    
    def __init__(self):
        self.logger = logging.getLogger("agent_system")
        self.agents = {}
        
        # Load settings
        self.settings = Settings()
        
        if not self.settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
    
    async def initialize(self):
        """Initialize the system and create default agents."""
        self.logger.info("Initializing Simple AI Agent System")
        
        # Create default agents
        agents_config = [
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
        
        for config in agents_config:
            agent = SimpleAgent(
                config["agent_id"],
                config["personality"],
                config["domain"],
                self.settings.OPENAI_API_KEY
            )
            self.agents[config["agent_id"]] = agent
            self.logger.info(f"Created agent: {config['agent_id']}")
        
        self.logger.info(f"System initialized with {len(self.agents)} agents")
    
    async def chat(self, agent_id: str, user_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send message to specific agent."""
        if agent_id not in self.agents:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
                "available_agents": list(self.agents.keys())
            }
        
        return await self.agents[agent_id].process_message(user_id, message, context)
    
    def list_agents(self) -> Dict[str, Any]:
        """List all available agents."""
        return {
            "agents": [
                {
                    "agent_id": agent_id,
                    "personality": agent.personality_type,
                    "business_domain": agent.business_domain,
                    "status": "active"
                }
                for agent_id, agent in self.agents.items()
            ],
            "total_agents": len(self.agents)
        }
    
    async def test_agents(self) -> Dict[str, Any]:
        """Test both agents with sample messages."""
        test_results = []
        
        # Test financial advisor
        financial_test = await self.chat(
            "agent_alpha",
            "test_user",
            "I have $50,000 to invest and I'm 35 years old. What investment strategy would you recommend?",
            {"risk_tolerance": "moderate", "time_horizon": "long-term"}
        )
        test_results.append({
            "agent": "agent_alpha (Financial Advisor)",
            "test": "Investment consultation",
            "result": financial_test
        })
        
        # Test content creator
        content_test = await self.chat(
            "agent_beta", 
            "test_user",
            "I need to create viral social media content for a sustainable fashion brand. What are some creative ideas?",
            {"platform": "instagram", "target_audience": "millennials"}
        )
        test_results.append({
            "agent": "agent_beta (Content Creator)",
            "test": "Content strategy",
            "result": content_test
        })
        
        return {
            "test_completed": True,
            "timestamp": datetime.utcnow().isoformat(),
            "results": test_results
        }


async def main():
    """Main function to run the system."""
    # Setup logging
    setup_logger()
    logger = logging.getLogger("main")
    
    try:
        # Initialize system
        system = SimpleAgentSystem()
        await system.initialize()
        
        # List agents
        agents_info = system.list_agents()
        logger.info(f"Available agents: {agents_info}")
        
        # Test agents
        logger.info("Running agent tests...")
        test_results = await system.test_agents()
        
        # Display results
        print("\n" + "="*80)
        print("AI AGENTS SYSTEM - STANDALONE MODE")
        print("="*80)
        print(f"System Status: RUNNING")
        print(f"Agents Created: {len(system.agents)}")
        print(f"OpenAI Integration: ACTIVE")
        print("="*80)
        
        for agent_id, agent in system.agents.items():
            print(f"\nAgent: {agent_id}")
            print(f"  Personality: {agent.personality_type}")
            print(f"  Business Domain: {agent.business_domain}")
            print(f"  Status: Active")
        
        print("\n" + "="*80)
        print("TEST RESULTS")
        print("="*80)
        
        for test in test_results["results"]:
            print(f"\n{test['agent']} - {test['test']}:")
            result = test["result"]
            if result["success"]:
                response = result["response"]
                print(f"  Response: {response[:200]}...")
                print(f"  Tokens Used: {result.get('tokens_used', 0)}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*80)
        print("SYSTEM READY FOR API INTEGRATION")
        print("="*80)
        
        # Keep the system running
        logger.info("System is ready. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("System shutdown requested")
    except Exception as e:
        logger.error(f"System error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())