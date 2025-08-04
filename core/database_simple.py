"""
Simple Database Management for AI Agents System
Provides basic conversation persistence without external database dependencies
"""
import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class SimpleDatabase:
    """Simple file-based database for conversation persistence."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "conversations").mkdir(exist_ok=True)
        (self.data_dir / "users").mkdir(exist_ok=True)
        (self.data_dir / "agents").mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("simple_database")
        self.lock = asyncio.Lock()
    
    async def save_conversation(self, agent_id: str, user_id: str, conversation: List[Dict[str, Any]]) -> None:
        """Save conversation history to file."""
        async with self.lock:
            try:
                conversation_file = self.data_dir / "conversations" / f"{agent_id}_{user_id}.json"
                
                data = {
                    "agent_id": agent_id,
                    "user_id": user_id,
                    "conversation": conversation,
                    "updated_at": datetime.utcnow().isoformat(),
                    "message_count": len(conversation)
                }
                
                with open(conversation_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                self.logger.debug(f"Saved conversation for {agent_id}_{user_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to save conversation: {e}")
    
    async def load_conversation(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Load conversation history from file."""
        try:
            conversation_file = self.data_dir / "conversations" / f"{agent_id}_{user_id}.json"
            
            if not conversation_file.exists():
                return []
            
            with open(conversation_file, 'r') as f:
                data = json.load(f)
                
            return data.get("conversation", [])
            
        except Exception as e:
            self.logger.error(f"Failed to load conversation: {e}")
            return []
    
    async def save_user_info(self, user_id: str, user_info: Dict[str, Any]) -> None:
        """Save user information."""
        async with self.lock:
            try:
                user_file = self.data_dir / "users" / f"{user_id}.json"
                
                user_data = {
                    "user_id": user_id,
                    "info": user_info,
                    "created_at": user_info.get("created_at", datetime.utcnow().isoformat()),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                with open(user_file, 'w') as f:
                    json.dump(user_data, f, indent=2)
                    
                self.logger.debug(f"Saved user info for {user_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to save user info: {e}")
    
    async def load_user_info(self, user_id: str) -> Dict[str, Any]:
        """Load user information."""
        try:
            user_file = self.data_dir / "users" / f"{user_id}.json"
            
            if not user_file.exists():
                return {}
            
            with open(user_file, 'r') as f:
                data = json.load(f)
                
            return data.get("info", {})
            
        except Exception as e:
            self.logger.error(f"Failed to load user info: {e}")
            return {}
    
    async def save_agent_stats(self, agent_id: str, stats: Dict[str, Any]) -> None:
        """Save agent statistics."""
        async with self.lock:
            try:
                stats_file = self.data_dir / "agents" / f"{agent_id}_stats.json"
                
                stats_data = {
                    "agent_id": agent_id,
                    "stats": stats,
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                with open(stats_file, 'w') as f:
                    json.dump(stats_data, f, indent=2)
                    
                self.logger.debug(f"Saved stats for agent {agent_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to save agent stats: {e}")
    
    async def load_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Load agent statistics."""
        try:
            stats_file = self.data_dir / "agents" / f"{agent_id}_stats.json"
            
            if not stats_file.exists():
                return {
                    "total_messages": 0,
                    "total_tokens": 0,
                    "unique_users": 0,
                    "created_at": datetime.utcnow().isoformat()
                }
            
            with open(stats_file, 'r') as f:
                data = json.load(f)
                
            return data.get("stats", {})
            
        except Exception as e:
            self.logger.error(f"Failed to load agent stats: {e}")
            return {}
    
    async def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of all conversations."""
        try:
            conversations_dir = self.data_dir / "conversations"
            conversation_files = list(conversations_dir.glob("*.json"))
            
            total_conversations = len(conversation_files)
            total_messages = 0
            agents = set()
            users = set()
            
            for conv_file in conversation_files:
                try:
                    with open(conv_file, 'r') as f:
                        data = json.load(f)
                    
                    total_messages += data.get("message_count", 0)
                    agents.add(data.get("agent_id"))
                    users.add(data.get("user_id"))
                    
                except Exception as e:
                    self.logger.warning(f"Error reading conversation file {conv_file}: {e}")
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "unique_agents": len(agents),
                "unique_users": len(users),
                "active_agents": list(agents),
                "summary_generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate conversation summary: {e}")
            return {}
    
    async def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """Clean up conversations older than specified days."""
        try:
            conversations_dir = self.data_dir / "conversations"
            conversation_files = list(conversations_dir.glob("*.json"))
            
            cutoff_time = datetime.utcnow().timestamp() - (days_old * 24 * 3600)
            cleaned_count = 0
            
            for conv_file in conversation_files:
                try:
                    if conv_file.stat().st_mtime < cutoff_time:
                        conv_file.unlink()
                        cleaned_count += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error cleaning up {conv_file}: {e}")
            
            self.logger.info(f"Cleaned up {cleaned_count} old conversation files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup conversations: {e}")
            return 0