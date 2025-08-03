"""
MCP (Model Context Protocol) client implementation.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
import json
import aiohttp
from urllib.parse import urljoin

from utils.exceptions import MCPError
import os

class MCPClient:
    """MCP client for connecting to MCP servers and tools."""
    
    def __init__(self, server_urls: List[str]):
        self.server_urls = server_urls
        self.logger = logging.getLogger("mcp_client")
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.connected_servers: List[str] = []
        
    async def connect(self) -> None:
        """Connect to all configured MCP servers."""
        try:
            if not self.server_urls:
                self.logger.info("No MCP servers configured - running in test mode")
                return
                
            for server_url in self.server_urls:
                await self._connect_to_server(server_url)
            
            if self.connected_servers:
                self.logger.info(f"Connected to {len(self.connected_servers)} MCP servers")
            else:
                self.logger.info("No MCP servers available - running in test mode")
            
        except Exception as e:
            self.logger.warning(f"MCP connection failed, running without external tools: {e}")
            # Don't raise error - allow system to continue without MCP
    
    async def _connect_to_server(self, server_url: str) -> None:
        """Connect to a single MCP server."""
        try:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('MCP_API_KEY', 'default_key')}"
                }
            )
            
            # Test connection with health check
            health_url = urljoin(server_url, "/health")
            async with session.get(health_url) as response:
                if response.status == 200:
                    self.sessions[server_url] = session
                    self.connected_servers.append(server_url)
                    self.logger.debug(f"Connected to MCP server: {server_url}")
                else:
                    await session.close()
                    self.logger.warning(f"MCP server {server_url} health check failed")
                    
        except Exception as e:
            self.logger.warning(f"Failed to connect to MCP server {server_url}: {e}")
            if 'session' in locals() and session:
                await session.close()
    
    async def list_tools(self, server_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available tools from MCP servers."""
        try:
            all_tools = []
            
            servers_to_query = [server_url] if server_url else self.connected_servers
            
            for server in servers_to_query:
                if server not in self.sessions:
                    continue
                    
                try:
                    tools_url = urljoin(server, "/tools")
                    session = self.sessions[server]
                    
                    async with session.get(tools_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            tools = data.get("tools", [])
                            for tool in tools:
                                tool["server_url"] = server
                            all_tools.extend(tools)
                        else:
                            self.logger.warning(f"Failed to list tools from {server}")
                            
                except Exception as e:
                    self.logger.warning(f"Error listing tools from {server}: {e}")
            
            return all_tools
            
        except Exception as e:
            self.logger.error(f"Error listing MCP tools: {e}")
            raise MCPError(f"Failed to list MCP tools: {e}")
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        server_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call a specific MCP tool."""
        try:
            # Find server with the tool if not specified
            if not server_url:
                tools = await self.list_tools()
                tool_servers = [t["server_url"] for t in tools if t.get("name") == tool_name]
                if not tool_servers:
                    raise MCPError(f"Tool '{tool_name}' not found on any connected server")
                server_url = tool_servers[0]
            
            if server_url not in self.sessions:
                raise MCPError(f"Not connected to server: {server_url}")
            
            # Call the tool
            tool_url = urljoin(server_url, f"/tools/{tool_name}/call")
            session = self.sessions[server_url]
            
            payload = {
                "arguments": arguments,
                "tool_name": tool_name
            }
            
            async with session.post(tool_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.debug(f"Successfully called tool {tool_name}")
                    return result
                else:
                    error_text = await response.text()
                    raise MCPError(f"Tool call failed: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error calling MCP tool {tool_name}: {e}")
            raise MCPError(f"Failed to call MCP tool {tool_name}: {e}")
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using MCP language model tools."""
        try:
            # Look for language model tools
            tools = await self.list_tools()
            llm_tools = [t for t in tools if "language" in t.get("name", "").lower() or "llm" in t.get("name", "").lower()]
            
            if not llm_tools:
                self.logger.debug("No language model tools available via MCP")
                return ""  # Return empty string to trigger fallback
            
            # Use the first available LLM tool
            llm_tool = llm_tools[0]
            
            result = await self.call_tool(
                llm_tool["name"],
                {"prompt": prompt, "max_tokens": 500},
                llm_tool["server_url"]
            )
            
            return result.get("response", "No response generated")
            
        except Exception as e:
            self.logger.debug(f"MCP response generation not available: {e}")
            return ""  # Return empty string to trigger fallback
    
    async def query_rag(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query RAG system through MCP tools."""
        try:
            # Look for RAG tools
            tools = await self.list_tools()
            rag_tools = [t for t in tools if "rag" in t.get("name", "").lower() or "search" in t.get("name", "").lower()]
            
            if not rag_tools:
                self.logger.warning("No RAG tools available via MCP")
                return []
            
            # Use the first available RAG tool
            rag_tool = rag_tools[0]
            
            result = await self.call_tool(
                rag_tool["name"],
                {"query": query, "top_k": top_k},
                rag_tool["server_url"]
            )
            
            return result.get("results", [])
            
        except Exception as e:
            self.logger.warning(f"Error querying RAG via MCP: {e}")
            return []  # Don't raise error, fallback to database RAG
    
    async def disconnect(self) -> None:
        """Disconnect from all MCP servers."""
        try:
            for server_url, session in self.sessions.items():
                await session.close()
            
            self.sessions.clear()
            self.connected_servers.clear()
            
            self.logger.info("Disconnected from all MCP servers")
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from MCP servers: {e}")
