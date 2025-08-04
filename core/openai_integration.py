"""
OpenAI integration for AI agents with personality-specific prompts.
Handles conversation context, prompt engineering, and response generation.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from utils.exceptions import LLMError
from agents.personalities import PersonalityManager
from config.settings import Settings


class OpenAIAgent:
    """OpenAI-powered agent with personality and business logic."""
    
    def __init__(self, agent_id: str, personality_type: str, business_domain: str, settings: Settings):
        self.agent_id = agent_id
        self.personality_type = personality_type
        self.business_domain = business_domain
        self.settings = settings
        self.logger = logging.getLogger(f"openai_{agent_id}")
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize personality manager
        self.personality_manager = PersonalityManager()
        self.personality = self.personality_manager.get_personality(personality_type)
        
        # Conversation context storage
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
        
        # Model configuration
        self.model = "gpt-4o"  # Latest OpenAI model
        self.max_tokens = 1000
        self.temperature = 0.7
        
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt based on personality and business domain."""
        base_prompt = f"""You are {self.agent_id}, an AI assistant with the following characteristics:

PERSONALITY: {self.personality_type.upper()}
{self.personality.get('description', '')}

BUSINESS DOMAIN: {self.business_domain.upper()}
{self._get_business_context()}

COMMUNICATION STYLE:
- Tone: {self.personality.get('tone', 'professional')}
- Approach: {self.personality.get('approach', 'helpful')}
- Response style: {self.personality.get('response_style', 'Clear and concise')}

CORE TRAITS:
{self._format_personality_traits()}

RESPONSE GUIDELINES:
1. Always stay in character with your personality type
2. Apply your business domain expertise to all responses
3. Be helpful, accurate, and professional
4. Ask clarifying questions when needed
5. Provide actionable advice when appropriate
6. Remember conversation context and refer to previous interactions

IMPORTANT: You are a backend AI agent. Focus on providing intelligent responses that a frontend application can display to users. Do not mention technical implementation details unless specifically asked."""

        return base_prompt
    
    def _get_business_context(self) -> str:
        """Get business domain specific context."""
        business_contexts = {
            "financial_advisor": """
You are a financial advisory specialist with expertise in:
- Portfolio analysis and optimization
- Risk assessment and management
- Investment recommendations
- Market analysis and trends
- Financial planning and goal setting
- Regulatory compliance and best practices

You help users make informed financial decisions based on their goals, risk tolerance, and market conditions.
""",
            "content_creator": """
You are a content creation specialist with expertise in:
- Content strategy and planning
- Brand voice development
- SEO and content optimization
- Social media strategy
- Creative ideation and brainstorming
- Content performance analysis
- Audience engagement strategies

You help users create compelling, engaging content that resonates with their target audience.
""",
            "technical_support": """
You are a technical support specialist with expertise in:
- Problem diagnosis and troubleshooting
- System analysis and optimization
- Technical documentation
- Best practices and recommendations
- Integration guidance

You help users solve technical problems and optimize their systems.
""",
            "general_assistant": """
You are a general purpose assistant capable of helping with:
- Information research and analysis
- Task planning and organization
- Problem-solving and decision support
- Communication and writing assistance
- Learning and explanation of concepts

You adapt to user needs and provide comprehensive assistance across various topics.
"""
        }
        
        return business_contexts.get(self.business_domain, business_contexts["general_assistant"])
    
    def _format_personality_traits(self) -> str:
        """Format personality traits for the system prompt."""
        traits = self.personality.get('traits', [])
        if not traits:
            return "- Professional and helpful"
        
        return "\n".join([f"- {trait}" for trait in traits])
    
    def _get_conversation_context(self, user_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context for user."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        # Return recent messages (limit to prevent token overflow)
        return self.conversations[user_id][-limit:]
    
    def _add_to_conversation(self, user_id: str, role: str, content: str) -> None:
        """Add message to conversation history."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Limit conversation history to prevent memory overflow
        max_history = 50
        if len(self.conversations[user_id]) > max_history:
            # Keep system message and recent messages
            system_msgs = [msg for msg in self.conversations[user_id] if msg["role"] == "system"]
            recent_msgs = self.conversations[user_id][-max_history+len(system_msgs):]
            self.conversations[user_id] = system_msgs + recent_msgs
    
    async def process_user_message(self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user message and generate intelligent response."""
        try:
            self.logger.info(f"Processing message from user {user_id}")
            
            # Add user message to conversation
            self._add_to_conversation(user_id, "user", message)
            
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ]
            
            # Add conversation context
            conversation_context = self._get_conversation_context(user_id)
            for msg in conversation_context:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add additional context if provided
            if context:
                context_str = f"Additional context: {json.dumps(context, indent=2)}"
                messages.append({"role": "system", "content": context_str})
            
            # Generate response
            response = await self._call_openai(messages)
            
            # Add assistant response to conversation
            self._add_to_conversation(user_id, "assistant", response["content"])
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "user_id": user_id,
                "response": response["content"],
                "personality": self.personality_type,
                "business_domain": self.business_domain,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": response.get("tokens_used", 0),
                "model": self.model
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
    
    async def _call_openai(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make API call to OpenAI."""
        try:
            # Adjust temperature based on personality
            temperature = self.temperature
            if self.personality_type == "analytical":
                temperature = 0.3  # More deterministic for analytical responses
            elif self.personality_type == "creative":
                temperature = 0.9  # More creative and varied responses
            
            completion: ChatCompletion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            response_content = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            
            self.logger.info(f"OpenAI response generated, tokens used: {tokens_used}")
            
            return {
                "content": response_content,
                "tokens_used": tokens_used,
                "model": completion.model,
                "finish_reason": completion.choices[0].finish_reason
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise LLMError(f"Failed to generate response: {e}")
    
    async def generate_business_analysis(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business-specific analysis based on agent's domain."""
        try:
            # Create specialized prompt based on business domain
            analysis_prompt = self._build_analysis_prompt(data)
            
            messages = [
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = await self._call_openai(messages)
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "analysis_type": f"{self.business_domain}_analysis",
                "analysis": response["content"],
                "data_analyzed": data,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": response.get("tokens_used", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Business analysis failed: {e}")
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Build analysis prompt based on business domain."""
        if self.business_domain == "financial_advisor":
            return f"""
Please analyze the following financial data and provide recommendations:

Data: {json.dumps(data, indent=2)}

Provide a comprehensive analysis including:
1. Key insights from the data
2. Risk assessment
3. Opportunities identified
4. Specific recommendations
5. Next steps

Format your response as a structured analysis that would be valuable for investment decision-making.
"""
        elif self.business_domain == "content_creator":
            return f"""
Please analyze the following content data and provide strategic recommendations:

Data: {json.dumps(data, indent=2)}

Provide a comprehensive analysis including:
1. Content performance insights
2. Audience engagement patterns
3. Content optimization opportunities
4. Strategic recommendations
5. Creative ideas for improvement

Format your response as actionable content strategy guidance.
"""
        else:
            return f"""
Please analyze the following data and provide insights:

Data: {json.dumps(data, indent=2)}

Provide a comprehensive analysis including:
1. Key patterns and insights
2. Areas for improvement
3. Recommendations
4. Next steps

Format your response as actionable guidance based on your expertise.
"""
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of conversation with user."""
        if user_id not in self.conversations:
            return {"message_count": 0, "messages": []}
        
        messages = self.conversations[user_id]
        return {
            "user_id": user_id,
            "agent_id": self.agent_id,
            "message_count": len(messages),
            "last_interaction": messages[-1]["timestamp"] if messages else None,
            "conversation_started": messages[0]["timestamp"] if messages else None
        }
    
    def clear_conversation(self, user_id: str) -> bool:
        """Clear conversation history for user."""
        if user_id in self.conversations:
            del self.conversations[user_id]
            self.logger.info(f"Cleared conversation history for user {user_id}")
            return True
        return False


class OpenAIIntegrationManager:
    """Manages OpenAI agents for the system."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("openai_manager")
        self.agents: Dict[str, OpenAIAgent] = {}
    
    async def initialize(self) -> None:
        """Initialize OpenAI integration."""
        try:
            # Test OpenAI connection
            client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            
            # Simple test call
            test_response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello, test connection."}],
                max_tokens=10
            )
            
            self.logger.info("OpenAI integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"OpenAI initialization failed: {e}")
            raise LLMError(f"OpenAI initialization failed: {e}")
    
    def create_agent(self, agent_id: str, personality_type: str, business_domain: str) -> OpenAIAgent:
        """Create and register an OpenAI agent."""
        agent = OpenAIAgent(agent_id, personality_type, business_domain, self.settings)
        self.agents[agent_id] = agent
        self.logger.info(f"Created OpenAI agent: {agent_id}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[OpenAIAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all registered agents."""
        return [
            {
                "agent_id": agent_id,
                "personality": agent.personality_type,
                "business_domain": agent.business_domain
            }
            for agent_id, agent in self.agents.items()
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of OpenAI integration."""
        try:
            client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            
            # Test call
            await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Health check"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "agents_count": len(self.agents),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }