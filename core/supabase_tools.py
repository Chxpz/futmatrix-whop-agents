"""
Supabase Tools for Futmatrix AI Agents
Database query and insert tools for LangGraph agents
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime

import asyncpg
from supabase import create_client, Client
from postgrest import APIError

from utils.exceptions import DatabaseError


class SupabaseQueryTool:
    """Tool for querying Supabase database from LangGraph agents."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.logger = logging.getLogger("supabase_query_tool")
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Initialize Supabase client."""
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            self.logger.info("Connected to Supabase successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to Supabase: {e}")
            raise DatabaseError(f"Supabase connection failed: {e}")
    
    async def query(self, sql: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query with optional parameters.
        
        Args:
            sql: SQL query string
            params: Optional list of parameters for parameterized queries
            
        Returns:
            List of result dictionaries
        """
        try:
            if not self.client:
                self._connect()
            
            if not self.client:
                raise DatabaseError("Supabase client not initialized")
            
            # For complex queries, we'll use the raw SQL execution
            # Note: This is a simplified implementation
            # In production, you'd want to use Supabase's query builder or raw SQL execution
            
            if "user_stats_summary" in sql and params:
                # Handle user stats queries
                response = self.client.table("user_stats_summary").select("*").eq("user_id", params[0]).execute()
                return response.data
            
            elif "matches" in sql and params:
                # Handle matches queries
                if "LIMIT 5" in sql:
                    response = (self.client.table("matches")
                              .select("*, processed_metrics(*)")
                              .eq("user_id", params[0])
                              .order("timestamp", desc=True)
                              .limit(5)
                              .execute())
                    return response.data
                else:
                    response = self.client.table("matches").select("*").eq("user_id", params[0]).execute()
                    return response.data
            
            elif "training_plans" in sql and params:
                # Handle training plans queries
                response = (self.client.table("training_plans")
                          .select("*")
                          .eq("user_id", params[0])
                          .eq("status", "in_progress")
                          .order("start_date", desc=True)
                          .limit(1)
                          .execute())
                return response.data
            
            elif "rivalizer_matchmaking_view" in sql or ("users" in sql and "user_stats_summary" in sql):
                # Handle matchmaking queries - this is more complex
                return await self._handle_matchmaking_query(params or [])
            
            else:
                # Fallback for other queries
                self.logger.warning(f"Unhandled query pattern: {sql[:50]}...")
                return []
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Query failed: {e}")
    
    async def _handle_matchmaking_query(self, params: List) -> List[Dict[str, Any]]:
        """Handle complex matchmaking queries."""
        try:
            user_id = params[0] if params else None
            if not user_id:
                return []
            
            # Get user stats first
            user_response = self.client.table("user_stats_summary").select("*").eq("user_id", user_id).execute()
            if not user_response.data:
                return []
            
            user_stats = user_response.data[0]
            user_performance = user_stats["avg_overall_performance"]
            
            # Find potential opponents
            performance_range = 1.5
            min_performance = user_performance - performance_range
            max_performance = user_performance + performance_range
            
            # Query for opponents with similar performance
            opponents_response = (self.client.table("user_stats_summary")
                                .select("*, users(id, username, status)")
                                .neq("user_id", user_id)
                                .gte("avg_overall_performance", min_performance)
                                .lte("avg_overall_performance", max_performance)
                                .gte("matches_played", 5)
                                .eq("users.status", "active")
                                .limit(10)
                                .execute())
            
            # Format results to match expected structure
            formatted_results = []
            for opponent in opponents_response.data:
                if opponent.get("users"):  # Check if user data exists
                    formatted_results.append({
                        "id": opponent["users"]["id"],
                        "username": opponent["users"]["username"],
                        "avg_overall_performance": opponent["avg_overall_performance"],
                        "win_rate": opponent["win_rate"],
                        "matches_played": opponent["matches_played"],
                        "last_match_at": opponent["last_match_at"]
                    })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Matchmaking query failed: {e}")
            return []
    
    async def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user statistics summary."""
        try:
            response = self.client.table("user_stats_summary").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self.logger.error(f"Failed to get user stats: {e}")
            return None
    
    async def get_recent_matches(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get user's recent matches with metrics."""
        try:
            response = (self.client.table("matches")
                       .select("*, processed_metrics(*)")
                       .eq("user_id", user_id)
                       .order("timestamp", desc=True)
                       .limit(limit)
                       .execute())
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to get recent matches: {e}")
            return []
    
    async def get_training_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current training plan."""
        try:
            response = (self.client.table("training_plans")
                       .select("*")
                       .eq("user_id", user_id)
                       .eq("status", "in_progress")
                       .order("start_date", desc=True)
                       .limit(1)
                       .execute())
            return response.data[0] if response.data else None
        except Exception as e:
            self.logger.error(f"Failed to get training plan: {e}")
            return None


class SupabaseInsertTool:
    """Tool for inserting/updating data in Supabase from LangGraph agents."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.logger = logging.getLogger("supabase_insert_tool")
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self):
        """Initialize Supabase client."""
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            self.logger.info("Connected to Supabase for insertions")
        except Exception as e:
            self.logger.error(f"Failed to connect to Supabase: {e}")
            raise DatabaseError(f"Supabase connection failed: {e}")
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert data into specified table.
        
        Args:
            table: Table name
            data: Dictionary of data to insert
            
        Returns:
            Inserted record data
        """
        try:
            if not self.client:
                self._connect()
            
            if not self.client:
                raise DatabaseError("Supabase client not initialized")
            
            # Add timestamp if not present
            if "timestamp" not in data and table == "agent_interactions":
                data["timestamp"] = datetime.utcnow().isoformat()
            
            response = self.client.table(table).insert(data).execute()
            
            if response.data:
                self.logger.info(f"Successfully inserted into {table}")
                return response.data[0]
            else:
                raise DatabaseError(f"Insert returned no data for table {table}")
            
        except Exception as e:
            self.logger.error(f"Insert failed for table {table}: {e}")
            raise DatabaseError(f"Insert failed: {e}")
    
    async def update(self, table: str, match_criteria: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data in specified table.
        
        Args:
            table: Table name
            match_criteria: Criteria to match records for update
            data: Dictionary of data to update
            
        Returns:
            Updated record data
        """
        try:
            if not self.client:
                self._connect()
            
            if not self.client:
                raise DatabaseError("Supabase client not initialized")
            
            # Build update query
            query = self.client.table(table)
            
            # Apply match criteria
            for key, value in match_criteria.items():
                query = query.eq(key, value)
            
            response = query.update(data).execute()
            
            if response.data:
                self.logger.info(f"Successfully updated {table}")
                return response.data[0]
            else:
                raise DatabaseError(f"Update returned no data for table {table}")
            
        except Exception as e:
            self.logger.error(f"Update failed for table {table}: {e}")
            raise DatabaseError(f"Update failed: {e}")
    
    async def log_agent_interaction(self, user_id: str, agent_type: str, interaction_type: str, 
                                   content: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        """Log an agent interaction."""
        data = {
            "user_id": user_id,
            "agent_type": agent_type,
            "interaction_type": interaction_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if payload:
            data["payload"] = json.dumps(payload)
        
        return await self.insert("agent_interactions", data)
    
    async def create_training_plan(self, user_id: str, checkpoints: List[Dict], 
                                  stake_amount: int, duration_weeks: int = 4) -> Dict[str, Any]:
        """Create a new training plan."""
        start_date = datetime.now().date()
        end_date = datetime.now().date().replace(day=start_date.day + (duration_weeks * 7))
        
        data = {
            "user_id": user_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "checkpoints": json.dumps(checkpoints),
            "stake_amount": stake_amount,
            "status": "in_progress",
            "reward_issued": False,
            "penalty_applied": False
        }
        
        return await self.insert("training_plans", data)
    
    async def update_training_plan(self, plan_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing training plan."""
        return await self.update("training_plans", {"id": plan_id}, updates)


class SupabaseViewTool:
    """Tool for accessing Supabase views optimized for agent operations."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.logger = logging.getLogger("supabase_view_tool")
        self.client = create_client(supabase_url, supabase_key)
    
    async def get_coach_user_view(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get data from coach_user_view for coaching analysis."""
        try:
            response = self.client.table("coach_user_view").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self.logger.error(f"Failed to get coach user view: {e}")
            return None
    
    async def get_rivalizer_matchmaking_view(self, user_id: str) -> List[Dict[str, Any]]:
        """Get potential opponents from rivalizer_matchmaking_view."""
        try:
            response = self.client.table("rivalizer_matchmaking_view").select("*").neq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to get matchmaking view: {e}")
            return []
    
    async def get_weekly_rankings(self, rank_type: str = "week_on_fire") -> List[Dict[str, Any]]:
        """Get current weekly rankings."""
        try:
            response = (self.client.table("weekly_rankings")
                       .select("*")
                       .eq("rank_type", rank_type)
                       .order("week_start", desc=True)
                       .limit(1)
                       .execute())
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to get weekly rankings: {e}")
            return []