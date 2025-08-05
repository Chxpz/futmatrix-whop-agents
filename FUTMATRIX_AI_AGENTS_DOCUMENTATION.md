# Futmatrix AI Agents Layer - Complete Documentation
**Version 1.0.0 - LangGraph Implementation**

## Overview

This repository implements the **AI Agents Layer** for the Futmatrix competitive gaming platform. It provides two specialized LangGraph-based AI agents designed for EA Sports FC 25 competitive gaming:

- **Coach Agent**: Performance analysis, training plan management, and personalized coaching
- **Rivalizer Agent**: Intelligent matchmaking, opponent suggestions, and competitive coordination

## Architecture Overview

### System Integration
The AI Agents Layer sits within the broader Futmatrix ecosystem and integrates with:
- **Supabase Database**: Player data, match history, performance metrics
- **Discord Bot**: User interactions and notifications
- **Web Platform**: Dashboard data and user interface
- **Smart Contracts**: Token rewards, penalties, and staking mechanisms
- **Microservices**: Match processing, OCR analysis, ranking computation

### Technology Stack
- **LangGraph**: State-based agent orchestration and workflow management
- **OpenAI GPT-4o**: Advanced language model for intelligent responses
- **Supabase**: PostgreSQL database with real-time capabilities
- **FastAPI**: Production-ready API server with comprehensive security
- **Python 3.11+**: Modern Python with async/await support

## Agent Specifications

### Coach Agent (LangGraph Implementation)

**Purpose**: Analyze player performance and provide personalized coaching advice

**Input**: `user_id` and optional coaching request message

**Tools**:
- **Supabase DB Query Tool**: Fetch last 5 matches with performance metrics
- **Metrics Analyzer Tool**: Compute performance trends and consistency
- **Training Plan Tool**: Generate or update personalized training plans

**Workflow Nodes**:
1. `analyze_user` - Fetch and analyze recent performance data
2. `generate_response` - Create personalized coaching advice
3. `update_training_plan` - Create/update training plans based on analysis
4. `log_interaction` - Record coaching session in database

**Decision Logic**:
- **No recent matches**: Suggest playing matches to generate data
- **Below performance threshold**: Adjust training plan with focus areas
- **Consistent progress**: Increase challenge level and issue token rewards
- **Declining performance**: Create intensive improvement plan

**Output**: Performance summary, coaching advice, updated training goals, token recommendations

### Rivalizer Agent (LangGraph Implementation)

**Purpose**: Facilitate competitive matchmaking and opponent suggestions

**Input**: `user_id` and optional matchmaking preferences

**Tools**:
- **Supabase DB Tool**: Access match history and user statistics
- **Matchmaking Tool**: Query `rivalizer_matchmaking_view` for eligible opponents
- **Discord + Platform Integration Tool**: Send match invites and notifications
- **Smart Contract Trigger Tool**: Handle staking and payout mechanisms

**Workflow Nodes**:
1. `find_opponents` - Identify eligible opponents based on skill level
2. `rank_matches` - Score potential matches using multiple factors
3. `generate_suggestions` - Create compelling match descriptions
4. `log_interaction` - Record matchmaking activity

**Matchmaking Algorithm**:
- **Performance Matching**: ±1.5 performance points for competitive balance
- **Experience Weighting**: Similar match counts preferred
- **Recency Bonus**: Recently active players prioritized
- **Avoid Repeats**: Filter out recent opponents (7-day window)

**Output**: 3 ranked opponent suggestions with strategic insights and booking options

## Database Integration

### Core Tables Used
- `users` - Player profiles and authentication data
- `user_stats_summary` - Aggregated performance metrics
- `matches` - Individual match records with detailed stats
- `processed_metrics` - Computed performance indicators
- `training_plans` - Coach-generated training programs
- `agent_interactions` - Complete log of AI agent activities

### Specialized Views
- `coach_user_view` - Optimized data for coaching analysis
- `rivalizer_matchmaking_view` - Pre-filtered matchmaking candidates

### Performance Metrics
The agents analyze comprehensive performance data:
- **Shot Efficiency**: Goal conversion and accuracy
- **Pass Efficiency**: Passing accuracy and possession control
- **Defensive Efficiency**: Tackling success and positioning
- **Overall Performance**: Weighted composite score (0-10 scale)
- **Consistency Score**: Performance variance measurement

## API Endpoints

### Public Endpoints (No Authentication)
- `GET /` - System information and status
- `GET /health` - Comprehensive health check with metrics
- `GET /agents` - Available agents and capabilities
- `GET /system/stats` - Detailed system statistics
- `GET /docs` - Interactive API documentation

### Protected Endpoints (Require API Key)
- `POST /coach/analyze` - Request coaching analysis and advice
- `POST /rivalizer/matchmake` - Find competitive match opponents

### Authentication
- **API Key Format**: `Authorization: Bearer your_api_key`
- **Rate Limiting**: 100 requests per minute per IP
- **Security Headers**: XSS/CSRF protection enabled

## Training Plan System

### Coach Agent Training Plans
The Coach Agent creates dynamic 4-week training programs based on performance analysis:

**Stake Mechanism**:
- Players stake tokens on their commitment to the training plan
- Success: Receive stake back + 20% bonus
- Failure: Partial or full stake slash (sent to treasury)

**Weekly Checkpoints**:
```json
{
  "week_1": {
    "matches_required": 3,
    "performance_target": 7.2,
    "focus_areas": ["finishing", "defensive_positioning"],
    "bonus_objectives": ["Score 5+ goals", "Keep clean sheet"]
  }
}
```

**Focus Areas Based on Performance**:
- **Declining**: Fundamentals (finishing, defense, game management)
- **Improving**: Advanced tactics (skill moves, pressure management)
- **Stable**: Consistency (fitness, mental preparation)

## Matchmaking Intelligence

### Rivalizer Agent Matchmaking
The Rivalizer Agent uses a sophisticated scoring system for opponent selection:

**Match Quality Score** (0-10 scale):
- **Performance Score** (40%): Skill level compatibility
- **Recency Score** (30%): Recent activity bonus
- **Experience Score** (20%): Similar match count preference
- **Win Rate Score** (10%): Balanced competition level

**Competitiveness Classification**:
- `very_even` (< 0.5 performance difference)
- `competitive` (0.5-1.0 difference)
- `slight_advantage` (1.0-1.5 difference)
- `challenging` (> 1.5 difference)

**Anti-Repetition Logic**:
- 7-day cooldown period for recent opponents
- Preference for new matchups to maintain engagement

## Production Features

### Security Implementation
- **API Key Authentication**: Environment-variable based key management
- **Rate Limiting**: Configurable request limits with IP-based tracking
- **Security Headers**: Comprehensive protection against common attacks
- **Input Validation**: Pydantic-based request/response validation

### Monitoring & Observability
- **Performance Metrics**: Response time tracking and system resource monitoring
- **Health Checks**: Multi-component status verification
- **API Analytics**: Endpoint usage statistics and error tracking
- **Agent Logging**: Comprehensive interaction logging for debugging

### Scalability Features
- **Async Processing**: Full async/await implementation for high concurrency
- **Database Connection Pooling**: Efficient Supabase connection management
- **Memory Management**: LangGraph checkpointing with MemorySaver
- **Error Recovery**: Graceful error handling with detailed logging

## Environment Configuration

### Required Environment Variables
```bash
# OpenAI Integration
OPENAI_API_KEY=your_openai_api_key

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key

# API Authentication
API_KEY=your_primary_api_key
# Or multiple keys: API_KEY_1, API_KEY_2, etc.

# Optional Configuration
RATE_LIMIT=100
LOG_LEVEL=INFO
```

### Development vs Production
- **Development Mode**: Uses demo API keys when no production keys are set
- **Production Mode**: Requires all environment variables, strict validation
- **Environment Detection**: Automatic mode selection based on `REPLIT_ENVIRONMENT`

## Deployment Guide

### Quick Start
1. **Install Dependencies**:
   ```bash
   pip install langgraph langchain-openai supabase asyncpg fastapi uvicorn
   ```

2. **Configure Environment**:
   ```bash
   cp production_environment.env .env
   # Edit .env with your credentials
   ```

3. **Run Server**:
   ```bash
   python api_server_futmatrix.py
   ```

4. **Verify Health**:
   ```bash
   curl http://localhost:5000/health
   ```

### Production Deployment
- **Replit**: Ready for one-click deployment
- **Docker**: Containerization support available
- **Cloud Providers**: Compatible with AWS, GCP, Azure
- **Load Balancing**: Stateless design enables horizontal scaling

## Integration Examples

### Coaching Analysis Request
```python
import requests

response = requests.post(
    "http://localhost:5000/coach/analyze",
    headers={"Authorization": "Bearer your_api_key"},
    json={"user_id": "user123", "message": "Analyze my recent performance"}
)

result = response.json()
print(f"Coaching advice: {result['response']}")
print(f"Plan updated: {result['additional_data']['plan_updated']}")
```

### Matchmaking Request
```python
response = requests.post(
    "http://localhost:5000/rivalizer/matchmake", 
    headers={"Authorization": "Bearer your_api_key"},
    json={"user_id": "user123", "message": "Find me a competitive match"}
)

result = response.json()
print(f"Match suggestions: {result['response']}")
print(f"Opponents found: {len(result['additional_data']['suggested_opponents'])}")
```

## Future Enhancements

### Planned Features
- **Advanced Analytics**: Machine learning-based performance prediction
- **Tournament Mode**: Multi-round competition coordination
- **Social Features**: Friend challenges and group competitions
- **Mobile SDK**: Native mobile app integration
- **Voice Interaction**: Discord voice channel integration

### Architecture Evolution
- **Multi-Game Support**: Extend beyond EA Sports FC 25
- **Real-Time Processing**: WebSocket-based live match analysis  
- **Advanced AI**: Integration with specialized sports AI models
- **Blockchain Integration**: Direct smart contract interaction

## Contributing

### Development Setup
1. Clone repository and install dependencies
2. Set up development environment variables
3. Run tests: `pytest tests/`
4. Start development server: `python api_server_futmatrix.py`

### Code Standards
- **Type Hints**: Full type annotation required
- **Async/Await**: All I/O operations must be async
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Docstrings for all public methods

### Testing
- **Unit Tests**: Individual component testing
- **Integration Tests**: Database and API testing  
- **Load Tests**: Performance validation
- **Agent Tests**: LangGraph workflow validation

---

## Summary

The Futmatrix AI Agents Layer provides intelligent, data-driven coaching and matchmaking services for competitive EA Sports FC 25 players. Built with LangGraph and modern Python technologies, it delivers personalized experiences that enhance player performance and competitive engagement while maintaining production-grade reliability and security.

**Key Capabilities**:
- ✅ Intelligent performance analysis and coaching advice
- ✅ Sophisticated matchmaking with quality scoring
- ✅ Dynamic training plan generation and management
- ✅ Comprehensive database integration with Supabase
- ✅ Production-ready API with security and monitoring
- ✅ Scalable architecture supporting thousands of users

The system is ready for production deployment and designed to scale with the Futmatrix platform's growth.