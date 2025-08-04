# AI Agents System - Usage Examples

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Agent Alpha - Financial Advisor](#agent-alpha---financial-advisor)
3. [Agent Beta - Content Creator](#agent-beta---content-creator)
4. [Advanced Use Cases](#advanced-use-cases)
5. [SDK Integration Examples](#sdk-integration-examples)
6. [Frontend Integration](#frontend-integration)
7. [Business Applications](#business-applications)

## Basic Usage

### Getting Started

#### 1. Check System Status
```bash
# Verify the system is running
curl http://localhost:5000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-08-04T16:32:26.614Z",
  "agents_count": 2,
  "openai_connection": "working"
}
```

#### 2. List Available Agents
```bash
curl http://localhost:5000/agents

# Response shows two agents:
# - agent_alpha: Financial Advisor (analytical personality)
# - agent_beta: Content Creator (creative personality)
```

#### 3. Simple Chat Example
```bash
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, I need investment advice."
  }'
```

## Agent Alpha - Financial Advisor

Agent Alpha specializes in financial advice with an analytical, data-driven personality.

### Investment Consultation

#### Basic Investment Advice
```bash
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "investor_123",
    "message": "I have $10,000 to invest and I am 28 years old. What should I do?",
    "context": {
      "risk_tolerance": "moderate",
      "investment_timeline": "long-term",
      "current_savings": 15000,
      "monthly_income": 5000
    }
  }'
```

**Expected Response Type**: Systematic investment strategy with asset allocation recommendations, risk assessment, and step-by-step guidance.

#### Portfolio Analysis
```bash
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "investor_456",
    "message": "My current portfolio is 80% stocks, 15% bonds, 5% cash. Should I rebalance?",
    "context": {
      "age": 45,
      "risk_tolerance": "moderate",
      "portfolio_value": 250000,
      "investment_goals": ["retirement", "education_fund"]
    }
  }'
```

**Expected Response Type**: Portfolio analysis with rebalancing recommendations, risk evaluation, and diversification strategies.

#### Retirement Planning
```bash
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "retirement_planner",
    "message": "I want to retire at 60 with $1 million. I am currently 35. How much should I save monthly?",
    "context": {
      "current_age": 35,
      "retirement_age": 60,
      "retirement_goal": 1000000,
      "current_retirement_savings": 50000,
      "expected_return": 0.07
    }
  }'
```

**Expected Response Type**: Mathematical analysis of required monthly savings, compound growth projections, and strategy adjustments.

### Risk Assessment Scenarios

#### Market Volatility Consultation
```bash
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "worried_investor",
    "message": "The market is very volatile right now. Should I sell my stocks and wait?",
    "context": {
      "portfolio_value": 100000,
      "investment_timeline": "15_years",
      "risk_tolerance": "moderate",
      "recent_losses": 8000
    }
  }'
```

**Expected Response Type**: Evidence-based analysis of market timing, historical data references, and systematic approach to volatility management.

#### Emergency Fund Planning
```bash
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "budget_planner",
    "message": "How much should I keep in my emergency fund before I start investing?",
    "context": {
      "monthly_expenses": 4000,
      "job_stability": "stable",
      "dependents": 2,
      "current_emergency_fund": 8000
    }
  }'
```

**Expected Response Type**: Systematic calculation of emergency fund needs with risk factors and step-by-step savings plan.

## Agent Beta - Content Creator

Agent Beta specializes in creative content strategies with an innovative, imaginative personality.

### Social Media Strategy

#### Instagram Content Strategy
```bash
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "brand_manager",
    "message": "I need a viral Instagram strategy for my sustainable fashion brand targeting Gen Z.",
    "context": {
      "platform": "instagram",
      "target_audience": "gen_z",
      "brand_focus": "sustainable_fashion",
      "current_followers": 5000,
      "budget": "low"
    }
  }'
```

**Expected Response Type**: Creative content ideas with viral potential, platform-specific strategies, and engagement tactics.

#### TikTok Marketing Campaign
```bash
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "marketing_team",
    "message": "Create a TikTok campaign for our new tech product launch targeting millennials.",
    "context": {
      "platform": "tiktok",
      "target_audience": "millennials",
      "product_type": "tech_gadget",
      "launch_date": "next_month",
      "campaign_goal": "awareness"
    }
  }'
```

**Expected Response Type**: Innovative campaign concepts, trending hashtag strategies, and creative video ideas.

### Brand Development

#### Brand Storytelling
```bash
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "startup_founder",
    "message": "Help me create a compelling brand story for my food delivery startup.",
    "context": {
      "industry": "food_delivery",
      "unique_value_proposition": "local_restaurants_focus", 
      "target_market": "urban_professionals",
      "brand_personality": "community_focused"
    }
  }'
```

**Expected Response Type**: Creative narrative development, emotional connection strategies, and brand positioning ideas.

#### Content Calendar Planning
```bash
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "content_manager",
    "message": "Plan a month-long content calendar for our fitness brand across all social platforms.",
    "context": {
      "brand": "fitness",
      "platforms": ["instagram", "facebook", "twitter"],
      "content_types": ["posts", "stories", "videos"],
      "posting_frequency": "daily"
    }
  }'
```

**Expected Response Type**: Comprehensive content calendar with creative themes, platform-specific adaptations, and engagement strategies.

### Creative Campaigns

#### Influencer Collaboration Ideas
```bash
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "pr_manager",
    "message": "Design unique influencer collaboration ideas for our skincare brand.",
    "context": {
      "brand": "skincare",
      "target_influencers": "micro_influencers",
      "campaign_goal": "product_awareness",
      "budget_range": "medium",
      "unique_angle": "natural_ingredients"
    }
  }'
```

**Expected Response Type**: Innovative collaboration concepts, creative campaign mechanics, and engagement strategies.

## Advanced Use Cases

### Multi-Agent Conversations

#### Financial Planning with Creative Marketing
```bash
# Step 1: Get financial advice from Agent Alpha
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "entrepreneur",
    "message": "I am starting a business and need to plan my finances. I have $50,000 startup capital.",
    "context": {
      "business_type": "e-commerce",
      "monthly_expenses": 3000,
      "revenue_projection": "growing",
      "risk_tolerance": "moderate"
    }
  }'

# Step 2: Use financial insights to create marketing strategy with Agent Beta
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "entrepreneur", 
    "message": "Based on my $50,000 budget, create a cost-effective marketing strategy for my e-commerce startup.",
    "context": {
      "budget": 50000,
      "business_type": "e-commerce",
      "target_market": "online_shoppers",
      "marketing_channels": ["social_media", "content_marketing"]
    }
  }'
```

### Context-Aware Conversations

#### Building on Previous Conversations
```bash
# First conversation with context building
curl -X POST http://localhost:5000/agents/agent_alpha/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "returning_client",
    "message": "I previously asked about investing $25,000. Now I have additional $15,000. How should I adjust my strategy?",
    "context": {
      "previous_investment": 25000,
      "additional_funds": 15000,
      "time_since_last_investment": "6_months",
      "market_performance": "positive"
    }
  }'
```

**Expected Behavior**: Agent Alpha will remember the conversation context and provide continuity in advice.

### Complex Business Scenarios

#### Comprehensive Business Strategy
```bash
curl -X POST http://localhost:5000/agents/agent_beta/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "business_owner",
    "message": "My restaurant has been struggling. I need a complete rebranding and marketing overhaul to attract younger customers.",
    "context": {
      "business_type": "restaurant",
      "current_situation": "declining_sales",
      "target_demographic": "millennials_gen_z",
      "budget": "limited",
      "location": "urban",
      "cuisine_type": "italian"
    }
  }'
```

**Expected Response Type**: Comprehensive rebranding strategy with creative solutions, cost-effective marketing tactics, and actionable implementation steps.

## SDK Integration Examples

### JavaScript/TypeScript Integration

#### React Component Example
```javascript
import React, { useState } from 'react';

const AIAgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (agentId, message, context = null) => {
    setLoading(true);
    
    try {
      const response = await fetch(`http://localhost:5000/agents/${agentId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user123',
          message: message,
          context: context
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setMessages(prev => [...prev, 
          { role: 'user', content: message },
          { role: 'assistant', content: data.response, agent: agentId }
        ]);
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : `Agent ${msg.agent}`}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}
      </div>
      
      <div className="input-section">
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the financial advisor or content creator..."
        />
        <button 
          onClick={() => sendMessage('agent_alpha', input)}
          disabled={loading}
        >
          Ask Financial Advisor
        </button>
        <button 
          onClick={() => sendMessage('agent_beta', input)}
          disabled={loading}
        >
          Ask Content Creator
        </button>
      </div>
    </div>
  );
};

export default AIAgentChat;
```

#### Node.js Backend Integration
```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

class AIAgentsClient {
  constructor(baseUrl = 'http://localhost:5000') {
    this.baseUrl = baseUrl;
  }

  async chatWithAgent(agentId, userId, message, context = null) {
    try {
      const response = await axios.post(`${this.baseUrl}/agents/${agentId}/chat`, {
        user_id: userId,
        message: message,
        context: context
      });
      
      return response.data;
    } catch (error) {
      throw new Error(`Agent chat failed: ${error.message}`);
    }
  }

  async getAgentInfo(agentId) {
    try {
      const response = await axios.get(`${this.baseUrl}/agents/${agentId}/info`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get agent info: ${error.message}`);
    }
  }
}

const aiClient = new AIAgentsClient();

// Financial advice endpoint
app.post('/api/financial-advice', async (req, res) => {
  try {
    const { userId, question, userProfile } = req.body;
    
    const response = await aiClient.chatWithAgent(
      'agent_alpha',
      userId,
      question,
      userProfile
    );
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Content strategy endpoint
app.post('/api/content-strategy', async (req, res) => {
  try {
    const { userId, brief, brandContext } = req.body;
    
    const response = await aiClient.chatWithAgent(
      'agent_beta',
      userId,
      brief,
      brandContext
    );
    
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Backend server running on port 3000');
});
```

### Python Integration

#### Django Integration Example
```python
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

class AIAgentsClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
    
    def chat_with_agent(self, agent_id, user_id, message, context=None):
        url = f"{self.base_url}/agents/{agent_id}/chat"
        payload = {
            "user_id": user_id,
            "message": message,
            "context": context
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

ai_client = AIAgentsClient()

@csrf_exempt
@require_http_methods(["POST"])
def financial_consultation(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        question = data.get('question')
        financial_profile = data.get('financial_profile', {})
        
        response = ai_client.chat_with_agent(
            'agent_alpha',
            user_id,
            question,
            financial_profile
        )
        
        return JsonResponse(response)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def content_strategy(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        brief = data.get('brief')
        brand_context = data.get('brand_context', {})
        
        response = ai_client.chat_with_agent(
            'agent_beta',
            user_id,
            brief,
            brand_context
        )
        
        return JsonResponse(response)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

#### Flask Integration Example
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

class AIAgentsService:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
    
    def get_financial_advice(self, user_id, question, context=None):
        return self._chat_with_agent('agent_alpha', user_id, question, context)
    
    def get_content_strategy(self, user_id, brief, context=None):
        return self._chat_with_agent('agent_beta', user_id, brief, context)
    
    def _chat_with_agent(self, agent_id, user_id, message, context):
        url = f"{self.base_url}/agents/{agent_id}/chat"
        payload = {
            "user_id": user_id,
            "message": message,
            "context": context
        }
        
        response = requests.post(url, json=payload)
        return response.json()

ai_service = AIAgentsService()

@app.route('/financial-advice', methods=['POST'])
def financial_advice():
    data = request.json
    
    response = ai_service.get_financial_advice(
        user_id=data['user_id'],
        question=data['question'],
        context=data.get('financial_context')
    )
    
    return jsonify(response)

@app.route('/content-strategy', methods=['POST']) 
def content_strategy():
    data = request.json
    
    response = ai_service.get_content_strategy(
        user_id=data['user_id'],
        brief=data['brief'],
        context=data.get('brand_context')
    )
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```

## Frontend Integration

### Vue.js Integration
```vue
<template>
  <div class="ai-agents-interface">
    <div class="agent-selector">
      <button 
        @click="selectedAgent = 'agent_alpha'"
        :class="{ active: selectedAgent === 'agent_alpha' }"
      >
        Financial Advisor
      </button>
      <button 
        @click="selectedAgent = 'agent_beta'"
        :class="{ active: selectedAgent === 'agent_beta' }"
      >
        Content Creator
      </button>
    </div>

    <div class="conversation">
      <div 
        v-for="message in conversation" 
        :key="message.id"
        :class="['message', message.role]"
      >
        <div class="message-content">{{ message.content }}</div>
        <div class="message-meta">
          {{ message.timestamp }} | {{ message.agent }}
        </div>
      </div>
    </div>

    <div class="input-area">
      <textarea 
        v-model="currentMessage"
        placeholder="Ask your question..."
        @keyup.enter="sendMessage"
      />
      <button @click="sendMessage" :disabled="loading">
        {{ loading ? 'Thinking...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedAgent: 'agent_alpha',
      currentMessage: '',
      conversation: [],
      loading: false,
      userId: 'user_' + Math.random().toString(36).substr(2, 9)
    };
  },
  
  methods: {
    async sendMessage() {
      if (!this.currentMessage.trim() || this.loading) return;
      
      const userMessage = {
        id: Date.now(),
        role: 'user',
        content: this.currentMessage,
        timestamp: new Date().toLocaleTimeString(),
        agent: 'user'
      };
      
      this.conversation.push(userMessage);
      this.loading = true;
      
      try {
        const response = await this.callAgent(
          this.selectedAgent,
          this.currentMessage
        );
        
        if (response.success) {
          this.conversation.push({
            id: Date.now() + 1,
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toLocaleTimeString(),
            agent: response.agent_id
          });
        }
      } catch (error) {
        console.error('Error calling agent:', error);
      } finally {
        this.currentMessage = '';
        this.loading = false;
      }
    },
    
    async callAgent(agentId, message, context = null) {
      const response = await fetch(`http://localhost:5000/agents/${agentId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          message: message,
          context: context
        })
      });
      
      return await response.json();
    }
  }
};
</script>
```

## Business Applications

### Financial Services Platform

#### Personal Finance Dashboard Integration
```javascript
// Financial planning dashboard component
class FinancialDashboard {
  constructor(apiClient) {
    this.aiAgent = apiClient;
    this.userId = getCurrentUserId();
  }

  async getInvestmentRecommendations(portfolioData) {
    const context = {
      current_portfolio: portfolioData,
      risk_tolerance: getUserRiskProfile(),
      investment_timeline: getUserTimeline(),
      financial_goals: getUserGoals()
    };

    const response = await this.aiAgent.chatWithAgent(
      'agent_alpha',
      this.userId,
      'Analyze my current portfolio and provide rebalancing recommendations.',
      context
    );

    return this.formatFinancialAdvice(response);
  }

  async planRetirement(retirementData) {
    const context = {
      current_age: retirementData.age,
      retirement_age: retirementData.targetAge,
      current_savings: retirementData.currentSavings,
      monthly_income: retirementData.monthlyIncome,
      expected_expenses: retirementData.expectedExpenses
    };

    return await this.aiAgent.chatWithAgent(
      'agent_alpha',
      this.userId,
      `Help me plan for retirement. I want to retire at ${retirementData.targetAge}.`,
      context
    );
  }

  formatFinancialAdvice(response) {
    return {
      recommendations: this.extractRecommendations(response.response),
      riskAssessment: this.extractRiskAnalysis(response.response),
      actionItems: this.extractActionItems(response.response),
      reasoning: response.response
    };
  }
}
```

### Marketing Agency Platform

#### Campaign Strategy Generator
```javascript
class MarketingCampaignGenerator {
  constructor(apiClient) {
    this.aiAgent = apiClient;
  }

  async generateCampaignStrategy(briefData) {
    const context = {
      brand: briefData.brand,
      target_audience: briefData.targetAudience,
      campaign_goals: briefData.goals,
      budget: briefData.budget,
      timeline: briefData.timeline,
      channels: briefData.preferredChannels
    };

    const response = await this.aiAgent.chatWithAgent(
      'agent_beta',
      briefData.clientId,
      `Create a comprehensive marketing campaign strategy for ${briefData.brand}.`,
      context
    );

    return this.formatCampaignStrategy(response);
  }

  async generateContentIdeas(contentBrief) {
    const context = {
      platform: contentBrief.platform,
      content_type: contentBrief.type,
      brand_voice: contentBrief.brandVoice,
      trending_topics: contentBrief.trends,
      target_engagement: contentBrief.engagementGoals
    };

    return await this.aiAgent.chatWithAgent(
      'agent_beta',
      contentBrief.userId,
      `Generate viral content ideas for ${contentBrief.platform}.`,
      context
    );
  }

  formatCampaignStrategy(response) {
    return {
      strategy: this.extractStrategy(response.response),
      tactics: this.extractTactics(response.response),
      timeline: this.extractTimeline(response.response),
      metrics: this.extractMetrics(response.response),
      creative_concepts: this.extractCreativeConcepts(response.response)
    };
  }
}
```

### Customer Service Integration

#### Intelligent Routing System
```javascript
class IntelligentCustomerService {
  constructor(aiClient) {
    this.aiClient = aiClient;
  }

  async routeCustomerQuery(query, customerProfile) {
    // Determine which agent is best suited for the query
    const routingResponse = await this.determineAgent(query);
    
    if (routingResponse.agent === 'financial') {
      return await this.handleFinancialQuery(query, customerProfile);
    } else if (routingResponse.agent === 'marketing') {
      return await this.handleMarketingQuery(query, customerProfile);
    }
  }

  async handleFinancialQuery(query, profile) {
    const context = {
      customer_segment: profile.segment,
      account_type: profile.accountType,
      risk_profile: profile.riskProfile,
      previous_interactions: profile.history
    };

    return await this.aiClient.chatWithAgent(
      'agent_alpha',
      profile.customerId,
      query,
      context
    );
  }

  async handleMarketingQuery(query, profile) {
    const context = {
      business_type: profile.businessType,
      industry: profile.industry,
      marketing_budget: profile.budget,
      current_challenges: profile.challenges
    };

    return await this.aiClient.chatWithAgent(
      'agent_beta',
      profile.customerId,
      query,
      context
    );
  }
}
```

### Analytics and Reporting

#### Conversation Analytics
```javascript
class ConversationAnalytics {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }

  async analyzeConversationTrends() {
    // Get system statistics
    const stats = await fetch('http://localhost:5000/system/stats');
    const data = await stats.json();

    return {
      totalConversations: data.performance.total_conversations,
      activeUsers: data.performance.active_users,
      agentUtilization: this.calculateAgentUtilization(data),
      commonTopics: await this.identifyCommonTopics(),
      satisfactionMetrics: await this.calculateSatisfaction()
    };
  }

  async generateUsageReport(timeRange) {
    // Implementation for usage reporting
    return {
      period: timeRange,
      agentPerformance: await this.getAgentPerformance(),
      userEngagement: await this.getUserEngagement(),
      responseQuality: await this.assessResponseQuality()
    };
  }
}
```

---

*Usage Examples last updated: August 4, 2025*