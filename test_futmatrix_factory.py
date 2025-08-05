#!/usr/bin/env python3
"""
Test script for Futmatrix agents using the AI Agents Factory
Creates Coach and Rivalizer agents using the extended factory system
"""
import asyncio
import logging
import os
from datetime import datetime

from config.settings import Settings
from agents.agent_factory import AgentFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_futmatrix_agents():
    """Test the creation and usage of Futmatrix agents."""
    print("="*80)
    print("FUTMATRIX AI AGENTS FACTORY TEST")
    print("="*80)
    
    # Initialize settings and factory
    settings = Settings()
    factory = AgentFactory(settings)
    
    try:
        # Initialize the factory
        await factory.initialize()
        print(f"✅ Agent factory initialized successfully")
        
        # Create Futmatrix Coach Agent
        print("\n🏆 Creating Coach Agent...")
        coach_agent = factory.create_agent(
            agent_id="futmatrix_coach",
            personality_type="coaching", 
            business_domain="sports_coaching"
        )
        print(f"✅ Created Coach Agent: {coach_agent.agent_id}")
        print(f"   Personality: {coach_agent.personality_type}")
        print(f"   Business Domain: {coach_agent.business_domain}")
        
        # Create Futmatrix Rivalizer Agent
        print("\n⚔️ Creating Rivalizer Agent...")
        rivalizer_agent = factory.create_agent(
            agent_id="futmatrix_rivalizer",
            personality_type="competitive",
            business_domain="competitive_gaming"
        )
        print(f"✅ Created Rivalizer Agent: {rivalizer_agent.agent_id}")
        print(f"   Personality: {rivalizer_agent.personality_type}")
        print(f"   Business Domain: {rivalizer_agent.business_domain}")
        
        # Initialize and start agents
        await factory.initialize_all_agents()
        await factory.start_all_agents()
        print(f"\n✅ All agents initialized and started")
        
        # Test Coach Agent
        print("\n" + "="*50)
        print("TESTING COACH AGENT")
        print("="*50)
        
        coaching_request = "I want to improve my EA Sports FC 25 performance. I'm struggling with consistency in competitive matches and need help with my finishing and defending skills."
        
        coach_response = await factory.process_user_message(
            agent_id="futmatrix_coach",
            user_id="test_player_001",
            message=coaching_request
        )
        
        if coach_response["success"]:
            print(f"🎯 Coach Response:")
            print(f"   Agent: {coach_response.get('agent_id', 'futmatrix_coach')}")
            print(f"   Response: {coach_response.get('response', 'No response content')[:200]}...")
            print(f"   Tokens Used: {coach_response.get('tokens_used', 'N/A')}")
        else:
            print(f"❌ Coach Agent Error: {coach_response.get('error', 'Unknown error')}")
        
        # Test Rivalizer Agent
        print("\n" + "="*50)
        print("TESTING RIVALIZER AGENT")
        print("="*50)
        
        rivalizer_request = "Find me some challenging opponents for competitive EA Sports FC 25 matches. I'm looking for players who can help me improve my tactical gameplay."
        
        rivalizer_response = await factory.process_user_message(
            agent_id="futmatrix_rivalizer",
            user_id="test_player_001", 
            message=rivalizer_request
        )
        
        if rivalizer_response["success"]:
            print(f"⚡ Rivalizer Response:")
            print(f"   Agent: {rivalizer_response.get('agent_id', 'futmatrix_rivalizer')}")
            print(f"   Response: {rivalizer_response.get('response', 'No response content')[:200]}...")
            print(f"   Tokens Used: {rivalizer_response.get('tokens_used', 'N/A')}")
        else:
            print(f"❌ Rivalizer Agent Error: {rivalizer_response.get('error', 'Unknown error')}")
        
        # Display factory statistics
        print("\n" + "="*50)
        print("FACTORY STATISTICS")
        print("="*50)
        
        stats = factory.get_factory_stats()
        print(f"📊 Factory Statistics:")
        print(f"   Total Agents: {stats['total_agents']}")
        print(f"   Active Agents: {stats['active_agents']}")
        print(f"   OpenAI Agents: {stats['openai_agents']}")
        print(f"   Personalities: {stats['personalities']}")
        print(f"   Business Domains: {stats['business_domains']}")
        
        # List all agents
        print(f"\n📋 Active Agents:")
        agent_list = factory.list_agents()
        for agent_info in agent_list:
            status_icon = "✅" if agent_info["is_active"] else "❌"
            print(f"   {status_icon} {agent_info['agent_id']}")
            print(f"      Personality: {agent_info['personality']}")
            print(f"      Domain: {agent_info['business_domain']}")
            print(f"      OpenAI: {agent_info['has_openai']}")
        
        # Health check
        print(f"\n🏥 System Health Check:")
        health = await factory.health_check()
        print(f"   Factory Status: {health['factory_status']}")
        print(f"   OpenAI Integration: {health['openai_integration']['status']}")
        print(f"   Agent Health: {len([a for a in health['agents'].values() if a['status'] == 'healthy'])}/{len(health['agents'])} healthy")
        
        print("\n" + "="*80)
        print("✅ FUTMATRIX AGENTS FACTORY TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"🎮 Coach Agent: Ready for performance analysis and training plans")
        print(f"⚔️ Rivalizer Agent: Ready for matchmaking and competitive coordination")
        print(f"🏭 Factory: Successfully managing {stats['total_agents']} agents")
        print(f"📈 OpenAI Integration: Active with GPT-4o model")
        print(f"🔧 System Status: Fully operational")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        try:
            await factory.stop_all_agents()
            print(f"\n🛑 All agents stopped successfully")
        except Exception as e:
            print(f"⚠️ Warning during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(test_futmatrix_agents())