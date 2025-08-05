"""
Futmatrix AI Agents - LangGraph Implementation
Coach Agent & Rivalizer Agent for competitive gaming platform
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Annotated
from datetime import datetime, timedelta
import json

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
import asyncpg

from core.supabase_tools import SupabaseQueryTool, SupabaseInsertTool
from utils.exceptions import AgentError


class AgentState(BaseModel):
    """State for Futmatrix agents with conversation history and context."""
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
    user_id: str = ""
    agent_type: str = ""  # 'coach' or 'rivalizer'
    context: Dict[str, Any] = Field(default_factory=dict)
    tools_output: Dict[str, Any] = Field(default_factory=dict)
    action_taken: bool = False


class FutmatrixCoachAgent:
    """
    Coach Agent - LangGraph implementation for performance analysis and training plans
    
    Tools:
    - Supabase DB Query Tool (fetch last 5 matches)
    - Metrics Analyzer Tool (compute avg efficiency) 
    - Training Plan Tool (generate or update plan)
    
    Logic:
    - If no recent match: suggest playing
    - If below performance threshold: adjust plan
    - If consistent progress: increase challenge + issue reward
    """
    
    def __init__(self, openai_api_key: str, supabase_url: str, supabase_key: str):
        self.logger = logging.getLogger("coach_agent")
        self.llm = ChatOpenAI(
            model="gpt-4o",
            openai_api_key=openai_api_key,
            temperature=0.3  # More analytical for coaching
        )
        
        # Initialize Supabase tools
        self.db_query_tool = SupabaseQueryTool(supabase_url, supabase_key)
        self.db_insert_tool = SupabaseInsertTool(supabase_url, supabase_key)
        
        # Create LangGraph workflow
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def _create_workflow(self) -> StateGraph:
        """Create the Coach Agent LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_user", self._analyze_user_performance)
        workflow.add_node("generate_response", self._generate_coaching_response)
        workflow.add_node("update_training_plan", self._update_training_plan)
        workflow.add_node("log_interaction", self._log_interaction)
        
        # Add edges
        workflow.add_edge(START, "analyze_user")
        workflow.add_edge("analyze_user", "generate_response")
        workflow.add_edge("generate_response", "update_training_plan")
        workflow.add_edge("update_training_plan", "log_interaction")
        workflow.add_edge("log_interaction", END)
        
        return workflow
    
    async def _analyze_user_performance(self, state: AgentState) -> AgentState:
        """Analyze user's recent performance using Supabase data."""
        try:
            # Fetch user's recent matches (last 5)
            recent_matches = await self.db_query_tool.query(
                """
                SELECT m.*, pm.overall_performance, pm.shot_efficiency, pm.pass_efficiency
                FROM matches m
                LEFT JOIN processed_metrics pm ON m.id = pm.match_id
                WHERE m.user_id = %s
                ORDER BY m.timestamp DESC
                LIMIT 5
                """,
                [state.user_id]
            )
            
            # Fetch user stats summary
            user_stats = await self.db_query_tool.query(
                "SELECT * FROM user_stats_summary WHERE user_id = %s",
                [state.user_id]
            )
            
            # Check current training plan
            training_plan = await self.db_query_tool.query(
                """
                SELECT * FROM training_plans 
                WHERE user_id = %s AND status = 'in_progress'
                ORDER BY start_date DESC LIMIT 1
                """,
                [state.user_id]
            )
            
            # Store analysis in context
            state.context.update({
                "recent_matches": recent_matches,
                "user_stats": user_stats[0] if user_stats else None,
                "current_training_plan": training_plan[0] if training_plan else None,
                "performance_trend": self._calculate_performance_trend(recent_matches)
            })
            
            self.logger.info(f"Analyzed performance for user {state.user_id}: {len(recent_matches)} recent matches")
            
        except Exception as e:
            self.logger.error(f"Error analyzing user performance: {e}")
            state.context["analysis_error"] = str(e)
        
        return state
    
    async def _generate_coaching_response(self, state: AgentState) -> AgentState:
        """Generate personalized coaching response based on analysis."""
        try:
            # Build coaching prompt based on analysis
            system_prompt = self._build_coaching_system_prompt()
            user_context = self._format_user_context(state.context)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                Analyze this player's performance and provide coaching advice:
                
                {user_context}
                
                Provide specific, actionable coaching advice based on their recent performance data.
                """)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Add to conversation history
            state.messages.extend([
                HumanMessage(content="Request coaching analysis"),
                AIMessage(content=response.content)
            ])
            
            state.context["coaching_response"] = response.content
            self.logger.info(f"Generated coaching response for user {state.user_id}")
            
        except Exception as e:
            self.logger.error(f"Error generating coaching response: {e}")
            state.context["response_error"] = str(e)
        
        return state
    
    async def _update_training_plan(self, state: AgentState) -> AgentState:
        """Update or create training plan based on performance analysis."""
        try:
            context = state.context
            current_plan = context.get("current_training_plan")
            performance_trend = context.get("performance_trend", {})
            
            # Determine if plan update is needed
            if self._should_update_training_plan(context):
                # Generate new training plan
                new_plan = await self._generate_training_plan(state.user_id, performance_trend)
                
                if current_plan:
                    # Update existing plan
                    await self.db_insert_tool.update(
                        "training_plans",
                        {"id": current_plan["id"]},
                        {
                            "checkpoints": json.dumps(new_plan["checkpoints"]),
                            "status": "updated"
                        }
                    )
                else:
                    # Create new plan
                    await self.db_insert_tool.insert(
                        "training_plans",
                        {
                            "user_id": state.user_id,
                            "start_date": datetime.now().date(),
                            "end_date": (datetime.now() + timedelta(weeks=4)).date(),
                            "checkpoints": json.dumps(new_plan["checkpoints"]),
                            "stake_amount": new_plan["stake_amount"],
                            "status": "in_progress"
                        }
                    )
                
                state.context["plan_updated"] = True
                state.context["new_plan"] = new_plan
                state.action_taken = True
            
        except Exception as e:
            self.logger.error(f"Error updating training plan: {e}")
            state.context["plan_update_error"] = str(e)
        
        return state
    
    async def _log_interaction(self, state: AgentState) -> AgentState:
        """Log the coaching interaction to database."""
        try:
            await self.db_insert_tool.insert(
                "agent_interactions",
                {
                    "user_id": state.user_id,
                    "agent_type": "coach",
                    "interaction_type": "coaching_session",
                    "content": state.context.get("coaching_response", ""),
                    "payload": json.dumps({
                        "analysis": state.context.get("performance_trend", {}),
                        "plan_updated": state.context.get("plan_updated", False),
                        "action_taken": state.action_taken
                    })
                }
            )
            
            self.logger.info(f"Logged coaching interaction for user {state.user_id}")
            
        except Exception as e:
            self.logger.error(f"Error logging interaction: {e}")
        
        return state
    
    def _build_coaching_system_prompt(self) -> str:
        """Build system prompt for coaching agent."""
        return """You are the Futmatrix Coach Agent, an expert EA Sports FC 25 performance analyst and trainer.

Your role is to:
1. Analyze player performance data from recent matches
2. Identify strengths and weaknesses in gameplay
3. Provide specific, actionable coaching advice
4. Create or adjust training plans to improve performance
5. Track progress and provide motivational feedback

Focus on:
- Shot efficiency and finishing
- Passing accuracy and possession
- Defensive positioning and tackling
- Game management and decision making
- Match psychology and mental preparation

Always provide specific, data-driven insights and actionable recommendations.
Be encouraging but honest about areas needing improvement."""
    
    def _format_user_context(self, context: Dict[str, Any]) -> str:
        """Format user context for coaching analysis."""
        recent_matches = context.get("recent_matches", [])
        user_stats = context.get("user_stats", {})
        performance_trend = context.get("performance_trend", {})
        
        context_str = f"""
        Player Statistics:
        - Matches Played: {user_stats.get('matches_played', 0)}
        - Win Rate: {user_stats.get('win_rate', 0):.2%}
        - Average Performance: {user_stats.get('avg_overall_performance', 0):.2f}
        - Performance Trend: {performance_trend.get('trend', 'stable')}
        
        Recent Match Performance:
        """
        
        for i, match in enumerate(recent_matches[:3]):
            context_str += f"""
        Match {i+1} ({match.get('match_type', 'unknown')}):
        - Score: {match.get('score_user', 0)} - {match.get('score_opponent', 0)}
        - Shot Accuracy: {match.get('shot_accuracy', 0):.1%}
        - Pass Accuracy: {match.get('pass_accuracy', 0):.1%}
        - Performance: {match.get('overall_performance', 0):.2f}
        """
        
        return context_str
    
    def _calculate_performance_trend(self, matches: List[Dict]) -> Dict[str, Any]:
        """Calculate performance trend from recent matches."""
        if not matches:
            return {"trend": "no_data", "direction": "stable"}
        
        performances = [m.get('overall_performance', 0) for m in matches if m.get('overall_performance')]
        
        if len(performances) < 2:
            return {"trend": "insufficient_data", "direction": "stable"}
        
        # Simple trend calculation
        recent_avg = sum(performances[:2]) / 2 if len(performances) >= 2 else performances[0]
        older_avg = sum(performances[2:]) / len(performances[2:]) if len(performances) > 2 else recent_avg
        
        trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        
        return {
            "trend": trend_direction,
            "recent_performance": recent_avg,
            "performance_change": recent_avg - older_avg,
            "consistency": self._calculate_consistency(performances)
        }
    
    def _calculate_consistency(self, performances: List[float]) -> float:
        """Calculate performance consistency (lower is more consistent)."""
        if len(performances) < 2:
            return 0.0
        
        avg = sum(performances) / len(performances)
        variance = sum((p - avg) ** 2 for p in performances) / len(performances)
        return variance ** 0.5
    
    def _should_update_training_plan(self, context: Dict[str, Any]) -> bool:
        """Determine if training plan should be updated."""
        performance_trend = context.get("performance_trend", {})
        current_plan = context.get("current_training_plan")
        
        # Update if declining performance or no current plan
        if performance_trend.get("trend") == "declining":
            return True
        
        if not current_plan:
            return True
        
        # Update if plan is old (more than 2 weeks)
        if current_plan:
            start_date = datetime.fromisoformat(str(current_plan["start_date"]))
            if (datetime.now() - start_date).days > 14:
                return True
        
        return False
    
    async def _generate_training_plan(self, user_id: str, performance_trend: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new training plan based on performance analysis."""
        # Simple training plan generation logic
        base_stake = 50  # Base token stake
        
        if performance_trend.get("trend") == "declining":
            stake_multiplier = 1.5
            focus_areas = ["finishing", "defensive_positioning", "game_management"]
        elif performance_trend.get("trend") == "improving":
            stake_multiplier = 0.8
            focus_areas = ["advanced_tactics", "skill_moves", "pressure_management"]
        else:
            stake_multiplier = 1.0
            focus_areas = ["consistency", "fitness", "mental_preparation"]
        
        checkpoints = []
        for week in range(1, 5):
            checkpoints.append({
                f"week_{week}": {
                    "matches_required": 3,
                    "performance_target": 7.0 + (week * 0.2),
                    "focus_areas": focus_areas,
                    "bonus_objectives": self._generate_bonus_objectives(focus_areas)
                }
            })
        
        return {
            "checkpoints": checkpoints,
            "stake_amount": int(base_stake * stake_multiplier),
            "focus_areas": focus_areas,
            "duration_weeks": 4
        }
    
    def _generate_bonus_objectives(self, focus_areas: List[str]) -> List[str]:
        """Generate bonus objectives based on focus areas."""
        bonus_map = {
            "finishing": ["Score 5+ goals in a match", "Achieve 70%+ shot accuracy"],
            "defensive_positioning": ["Keep clean sheet", "Win 80%+ tackles"],
            "game_management": ["Win from behind", "No cards received"],
            "advanced_tactics": ["10+ successful skill moves", "Complete 90%+ passes"],
            "consistency": ["Win 3 matches in a row", "Maintain 8.0+ rating average"]
        }
        
        objectives = []
        for area in focus_areas:
            if area in bonus_map:
                objectives.extend(bonus_map[area])
        
        return objectives[:3]  # Limit to 3 bonus objectives
    
    async def process_coaching_request(self, user_id: str, message: str = "") -> Dict[str, Any]:
        """Process a coaching request for a user."""
        try:
            config = {"configurable": {"thread_id": f"coach_{user_id}"}}
            
            initial_state = AgentState(
                user_id=user_id,
                agent_type="coach",
                messages=[HumanMessage(content=message or "Request coaching analysis")]
            )
            
            # Run the workflow
            result = await self.app.ainvoke(initial_state, config=config)
            
            return {
                "success": True,
                "agent_type": "coach",
                "user_id": user_id,
                "response": result.get("context", {}).get("coaching_response", ""),
                "action_taken": result.get("action_taken", False),
                "plan_updated": result.get("context", {}).get("plan_updated", False),
                "performance_analysis": result.get("context", {}).get("performance_trend", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing coaching request: {e}")
            return {
                "success": False,
                "agent_type": "coach",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class FutmatrixRivalizerAgent:
    """
    Rivalizer Agent - LangGraph implementation for matchmaking and competition management
    
    Tools:
    - Supabase DB Tool (match history)
    - Matchmaking Tool (access to rivalizer_matchmaking_view)
    - Discord + Platform Integration Tool (sends match invite)
    - Smart Contract Trigger Tool (stake, payout)
    
    Logic:
    - Filters eligible opponents
    - Picks 3 optimal based on skill delta + recency
    - Records user acceptance and schedules match
    """
    
    def __init__(self, openai_api_key: str, supabase_url: str, supabase_key: str):
        self.logger = logging.getLogger("rivalizer_agent")
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            openai_api_key=openai_api_key,
            temperature=0.5  # Balanced for matchmaking decisions
        )
        
        # Initialize Supabase tools
        self.db_query_tool = SupabaseQueryTool(supabase_url, supabase_key)
        self.db_insert_tool = SupabaseInsertTool(supabase_url, supabase_key)
        
        # Create LangGraph workflow
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def _create_workflow(self) -> StateGraph:
        """Create the Rivalizer Agent LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("find_opponents", self._find_eligible_opponents)
        workflow.add_node("rank_matches", self._rank_potential_matches)
        workflow.add_node("generate_suggestions", self._generate_match_suggestions)
        workflow.add_node("log_interaction", self._log_interaction)
        
        # Add edges
        workflow.add_edge(START, "find_opponents")
        workflow.add_edge("find_opponents", "rank_matches")
        workflow.add_edge("rank_matches", "generate_suggestions")
        workflow.add_edge("generate_suggestions", "log_interaction")
        workflow.add_edge("log_interaction", END)
        
        return workflow
    
    async def _find_eligible_opponents(self, state: AgentState) -> AgentState:
        """Find eligible opponents for matchmaking."""
        try:
            # Get user's current stats
            user_stats = await self.db_query_tool.query(
                "SELECT * FROM user_stats_summary WHERE user_id = %s",
                [state.user_id]
            )
            
            if not user_stats:
                state.context["error"] = "User stats not found"
                return state
            
            user_performance = user_stats[0]["avg_overall_performance"]
            user_matches = user_stats[0]["matches_played"]
            
            # Find potential opponents within performance range
            performance_range = 1.5  # +/- 1.5 performance points
            min_matches = max(5, user_matches * 0.5)  # At least 5 matches or 50% of user's matches
            
            opponents = await self.db_query_tool.query(
                """
                SELECT u.id, u.username, uss.*
                FROM users u
                JOIN user_stats_summary uss ON u.id = uss.user_id
                WHERE u.id != %s
                AND uss.matches_played >= %s
                AND uss.avg_overall_performance BETWEEN %s AND %s
                AND u.status = 'active'
                ORDER BY ABS(uss.avg_overall_performance - %s), uss.last_match_at DESC
                LIMIT 10
                """,
                [
                    state.user_id,
                    min_matches,
                    user_performance - performance_range,
                    user_performance + performance_range,
                    user_performance
                ]
            )
            
            # Check recent match history to avoid repeat opponents
            recent_opponents = await self.db_query_tool.query(
                """
                SELECT DISTINCT opponent_id FROM (
                    SELECT 
                        CASE 
                            WHEN user_id = %s THEN 'opponent_user_id' 
                            ELSE user_id 
                        END as opponent_id
                    FROM matches 
                    WHERE match_type = 'rivalizer' 
                    AND timestamp > NOW() - INTERVAL '7 days'
                    AND (user_id = %s OR 'opponent_user_id' = %s)
                ) recent
                """,
                [state.user_id, state.user_id, state.user_id]
            )
            
            recent_opponent_ids = [r["opponent_id"] for r in recent_opponents]
            
            # Filter out recent opponents
            filtered_opponents = [
                opp for opp in opponents
                if opp["id"] not in recent_opponent_ids
            ]
            
            state.context.update({
                "user_stats": user_stats[0],
                "eligible_opponents": filtered_opponents[:6],  # Top 6 candidates
                "user_performance": user_performance
            })
            
            self.logger.info(f"Found {len(filtered_opponents)} eligible opponents for user {state.user_id}")
            
        except Exception as e:
            self.logger.error(f"Error finding opponents: {e}")
            state.context["error"] = str(e)
        
        return state
    
    async def _rank_potential_matches(self, state: AgentState) -> AgentState:
        """Rank potential matches based on various factors."""
        try:
            opponents = state.context.get("eligible_opponents", [])
            user_performance = state.context.get("user_performance", 0)
            
            ranked_matches = []
            
            for opponent in opponents:
                # Calculate match quality score
                performance_diff = abs(opponent["avg_overall_performance"] - user_performance)
                performance_score = max(0, 10 - performance_diff * 2)  # Closer = better
                
                # Recency bonus (more recent activity = better)
                last_match = datetime.fromisoformat(str(opponent["last_match_at"]))
                days_since_match = (datetime.now() - last_match).days
                recency_score = max(0, 10 - days_since_match * 0.5)
                
                # Experience matching (similar match counts preferred)
                match_count_diff = abs(opponent["matches_played"] - state.context["user_stats"]["matches_played"])
                experience_score = max(0, 10 - match_count_diff * 0.1)
                
                # Win rate consideration (avoid too easy/hard opponents)
                win_rate_diff = abs(opponent["win_rate"] - state.context["user_stats"]["win_rate"])
                win_rate_score = max(0, 10 - win_rate_diff * 10)
                
                total_score = (
                    performance_score * 0.4 +
                    recency_score * 0.3 +
                    experience_score * 0.2 +
                    win_rate_score * 0.1
                )
                
                ranked_matches.append({
                    **opponent,
                    "match_quality_score": total_score,
                    "performance_diff": performance_diff,
                    "estimated_competitiveness": self._estimate_competitiveness(user_performance, opponent["avg_overall_performance"])
                })
            
            # Sort by match quality score
            ranked_matches.sort(key=lambda x: x["match_quality_score"], reverse=True)
            
            state.context["ranked_matches"] = ranked_matches[:3]  # Top 3 suggestions
            
        except Exception as e:
            self.logger.error(f"Error ranking matches: {e}")
            state.context["ranking_error"] = str(e)
        
        return state
    
    async def _generate_match_suggestions(self, state: AgentState) -> AgentState:
        """Generate match suggestions with AI-powered descriptions."""
        try:
            ranked_matches = state.context.get("ranked_matches", [])
            
            if not ranked_matches:
                state.context["response"] = "No suitable opponents found at this time. Try again later or play some matches to improve your matchmaking pool."
                return state
            
            # Build suggestion prompt
            system_prompt = """You are the Futmatrix Rivalizer Agent, expert at creating exciting match suggestions for competitive EA Sports FC 25 players.

Create engaging, personalized match suggestions that highlight:
1. Why each opponent is a good match
2. What makes the match competitive and interesting
3. Strategic insights about the matchup
4. Motivational elements to encourage participation

Be concise but exciting. Focus on the competitive aspect and potential for a great match."""
            
            suggestions_context = self._format_match_suggestions_context(ranked_matches, state.context["user_stats"])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                Generate 3 exciting match suggestions for this player:
                
                {suggestions_context}
                
                Create compelling descriptions for each suggested opponent that will motivate the player to accept a match.
                """)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Add to conversation history
            state.messages.extend([
                HumanMessage(content="Find me a Rivalizer match"),
                AIMessage(content=response.content)
            ])
            
            state.context["response"] = response.content
            state.context["suggestions_generated"] = True
            state.action_taken = True
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}")
            state.context["response"] = f"Error generating match suggestions: {str(e)}"
        
        return state
    
    async def _log_interaction(self, state: AgentState) -> AgentState:
        """Log the rivalizer interaction to database."""
        try:
            await self.db_insert_tool.insert(
                "agent_interactions",
                {
                    "user_id": state.user_id,
                    "agent_type": "rivalizer",
                    "interaction_type": "match_suggestion",
                    "content": state.context.get("response", ""),
                    "payload": json.dumps({
                        "suggested_opponents": [
                            {
                                "user_id": match["id"],
                                "username": match["username"],
                                "match_quality_score": match["match_quality_score"],
                                "competitiveness": match["estimated_competitiveness"]
                            }
                            for match in state.context.get("ranked_matches", [])
                        ],
                        "suggestions_generated": state.context.get("suggestions_generated", False)
                    })
                }
            )
            
            self.logger.info(f"Logged rivalizer interaction for user {state.user_id}")
            
        except Exception as e:
            self.logger.error(f"Error logging interaction: {e}")
        
        return state
    
    def _estimate_competitiveness(self, user_performance: float, opponent_performance: float) -> str:
        """Estimate match competitiveness based on performance difference."""
        diff = abs(user_performance - opponent_performance)
        
        if diff < 0.5:
            return "very_even"
        elif diff < 1.0:
            return "competitive"
        elif diff < 1.5:
            return "slight_advantage"
        else:
            return "challenging"
    
    def _format_match_suggestions_context(self, matches: List[Dict], user_stats: Dict) -> str:
        """Format match suggestions context for AI generation."""
        context = f"""
        Player Profile:
        - Performance Level: {user_stats['avg_overall_performance']:.2f}
        - Win Rate: {user_stats['win_rate']:.2%}
        - Matches Played: {user_stats['matches_played']}
        
        Suggested Opponents:
        """
        
        for i, match in enumerate(matches, 1):
            context += f"""
        {i}. {match['username']}
           - Performance: {match['avg_overall_performance']:.2f}
           - Win Rate: {match['win_rate']:.2%}
           - Matches: {match['matches_played']}
           - Match Quality: {match['match_quality_score']:.1f}/10
           - Competitiveness: {match['estimated_competitiveness']}
        """
        
        return context
    
    async def process_matchmaking_request(self, user_id: str, message: str = "") -> Dict[str, Any]:
        """Process a matchmaking request for a user."""
        try:
            config = {"configurable": {"thread_id": f"rivalizer_{user_id}"}}
            
            initial_state = AgentState(
                user_id=user_id,
                agent_type="rivalizer",
                messages=[HumanMessage(content=message or "Find me a Rivalizer match")]
            )
            
            # Run the workflow
            result = await self.app.ainvoke(initial_state, config=config)
            
            return {
                "success": True,
                "agent_type": "rivalizer",
                "user_id": user_id,
                "response": result.get("context", {}).get("response", ""),
                "suggestions_generated": result.get("context", {}).get("suggestions_generated", False),
                "suggested_opponents": result.get("context", {}).get("ranked_matches", []),
                "action_taken": result.get("action_taken", False),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing matchmaking request: {e}")
            return {
                "success": False,
                "agent_type": "rivalizer",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class FutmatrixAgentManager:
    """Manager for both Futmatrix agents with unified interface."""
    
    def __init__(self, openai_api_key: str, supabase_url: str, supabase_key: str):
        self.logger = logging.getLogger("futmatrix_agent_manager")
        
        # Initialize both agents
        self.coach_agent = FutmatrixCoachAgent(openai_api_key, supabase_url, supabase_key)
        self.rivalizer_agent = FutmatrixRivalizerAgent(openai_api_key, supabase_url, supabase_key)
        
        self.logger.info("Futmatrix Agent Manager initialized with Coach and Rivalizer agents")
    
    async def process_request(self, agent_type: str, user_id: str, message: str = "") -> Dict[str, Any]:
        """Process request for specified agent type."""
        if agent_type.lower() == "coach":
            return await self.coach_agent.process_coaching_request(user_id, message)
        elif agent_type.lower() == "rivalizer":
            return await self.rivalizer_agent.process_matchmaking_request(user_id, message)
        else:
            return {
                "success": False,
                "error": f"Unknown agent type: {agent_type}. Available: coach, rivalizer",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about available agents."""
        return {
            "agents": [
                {
                    "agent_type": "coach",
                    "description": "Performance analysis and training plan management",
                    "capabilities": [
                        "Analyze recent match performance",
                        "Generate personalized coaching advice",
                        "Create and update training plans",
                        "Track progress and provide feedback"
                    ]
                },
                {
                    "agent_type": "rivalizer", 
                    "description": "Matchmaking and competitive gaming coordination",
                    "capabilities": [
                        "Find suitable opponents based on skill level",
                        "Generate match suggestions with strategic insights",
                        "Coordinate match scheduling",
                        "Track competitive match outcomes"
                    ]
                }
            ],
            "platform": "Futmatrix - EA Sports FC 25 Competitive Gaming",
            "powered_by": "LangGraph + OpenAI GPT-4o"
        }