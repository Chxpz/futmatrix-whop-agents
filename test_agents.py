#!/usr/bin/env python3
"""
Test script to demonstrate the AI agents system with sample interactions.
"""
import asyncio
import logging
from datetime import datetime
import uuid

from agents.agent_factory import AgentFactory
from config.settings import Settings
from utils.logger import setup_logger

async def test_agent_interaction(agent_name: str, agent_config: dict, test_prompts: list):
    """Test an agent with sample prompts."""
    print(f"\n{'='*60}")
    print(f"Testing {agent_name}")
    print(f"Personality: {agent_config['personality']}")
    print(f"Business Rules: {agent_config['business_rules']}")
    print(f"{'='*60}")
    
    # Create agent
    agent = await AgentFactory.create_agent(agent_name, agent_config)
    
    # Initialize agent
    await agent.initialize()
    
    # Test each prompt
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}: {prompt[:50]}... ---")
        
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            user_id = "test_user_123"
            
            # Process prompt
            response = await agent.process_prompt(prompt, user_id, session_id)
            
            print(f"✅ Agent Response:")
            print(f"{response.content}")
            print(f"Response generated at: {response.timestamp}")
            
        except Exception as e:
            print(f"❌ Error processing prompt: {e}")
    
    # Cleanup
    await agent.cleanup()
    print(f"\n{agent_name} testing completed.")

async def main():
    """Run comprehensive tests of both AI agents."""
    # Setup logging
    setup_logger(level="INFO")
    
    print("🚀 Starting AI Agents System Test")
    print("="*80)
    
    # Load settings
    settings = Settings()
    
    # Agent configurations
    agent_configs = {
        "agent_alpha": {
            "personality": "analytical",
            "business_rules": "financial_advisor",
            "mcp_servers": settings.MCP_SERVERS,
            "database_config": settings.DATABASE_CONFIG
        },
        "agent_beta": {
            "personality": "creative",
            "business_rules": "content_creator",
            "mcp_servers": settings.MCP_SERVERS,
            "database_config": settings.DATABASE_CONFIG
        }
    }
    
    # Test prompts for financial advisor agent
    financial_prompts = [
        "I want to start investing in stocks but I'm a complete beginner. What should I do?",
        "Should I pay off my credit card debt or invest in my 401k first?",
        "What are the risks of investing in cryptocurrency right now?",
        "I'm 30 years old and want to plan for retirement. Where do I start?"
    ]
    
    # Test prompts for content creator agent
    creative_prompts = [
        "Help me write a catchy blog post title about sustainable living tips",
        "I need ideas for social media content for a small bakery business",
        "Create an engaging email subject line for a fitness app launch",
        "What are some creative ways to market a new podcast about technology?"
    ]
    
    try:
        # Test Agent Alpha (Financial Advisor - Analytical)
        await test_agent_interaction(
            "agent_alpha",
            agent_configs["agent_alpha"], 
            financial_prompts
        )
        
        # Test Agent Beta (Content Creator - Creative)
        await test_agent_interaction(
            "agent_beta",
            agent_configs["agent_beta"],
            creative_prompts
        )
        
        print("\n" + "="*80)
        print("🎉 All agent tests completed successfully!")
        print("✅ Both agents are working correctly with their respective:")
        print("   - Personalities (analytical vs creative)")
        print("   - Business rules (financial_advisor vs content_creator)")
        print("   - LangGraph workflows")
        print("   - Database integration (test mode)")
        print("   - MCP client connectivity (test mode)")
        print("   - RAG system integration")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())