"""Enhanced MCP Client with parallel execution, better discovery, and caching.

This enhanced version provides:
- Parallel tool discovery and execution
- Intelligent caching with TTL
- Health monitoring of MCP servers
- Batch tool execution
- Enhanced error handling and retry logic
- Server capability detection
"""

import os
import asyncio
import httpx
import time
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from jsonschema import validate, ValidationError
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
MCP_SERVER_URLS = os.getenv("MCP_SERVER_URLS", "http://localhost:8001,http://localhost:8002,http://localhost:8003,http://localhost:8004").split(",")
MCP_DISCOVERY_TIMEOUT = float(os.getenv("MCP_DISCOVERY_TIMEOUT", "5"))
MCP_EXECUTION_TIMEOUT = float(os.getenv("MCP_EXECUTION_TIMEOUT", "15"))
MCP_HEALTH_CHECK_INTERVAL = float(os.getenv("MCP_HEALTH_CHECK_INTERVAL", "30"))
MCP_CACHE_TTL = float(os.getenv("MCP_CACHE_TTL", "300"))  # 5 minutes
MCP_MAX_RETRIES = int(os.getenv("MCP_MAX_RETRIES", "3"))
MCP_PARALLEL_LIMIT = int(os.getenv("MCP_PARALLEL_LIMIT", "10"))

class MCPClientError(Exception):
    """Enhanced MCP client error with more context"""
    def __init__(self, message: str, server_url: str = None, tool_name: str = None, error_code: str = None):
        super().__init__(message)
        self.server_url = server_url
        self.tool_name = tool_name
        self.error_code = error_code
        self.timestamp = datetime.now()

@dataclass
class ServerHealth:
    """Server health status tracking"""
    url: str
    is_healthy: bool
    last_check: datetime
    response_time: float
    error_count: int
    last_error: Optional[str] = None
    capabilities: List[str] = None

@dataclass
class ToolInfo:
    """Enhanced tool information with metadata"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server_url: str
    schema: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    tags: List[str] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    avg_response_time: float = 0.0

@dataclass
class ExecutionResult:
    """Tool execution result with metadata"""
    tool_name: str
    server_url: str
    parameters: Dict[str, Any]
    result: Any
    success: bool
    execution_time: float
    timestamp: datetime
    error: Optional[str] = None

class EnhancedMCPClient:
    """Enhanced MCP client with advanced features"""
    
    def __init__(self):
        self.servers = [url.strip() for url in MCP_SERVER_URLS if url.strip()]
        self.server_health: Dict[str, ServerHealth] = {}
        self.tool_cache: Dict[str, ToolInfo] = {}
        self.schema_cache: Dict[str, Dict[str, Any]] = {}
        self.execution_cache: Dict[str, ExecutionResult] = {}
        self.last_discovery = 0
        self.semaphore = asyncio.Semaphore(MCP_PARALLEL_LIMIT)
        
        # Initialize server health tracking
        for server in self.servers:
            self.server_health[server] = ServerHealth(
                url=server,
                is_healthy=True,
                last_check=datetime.now(),
                response_time=0.0,
                error_count=0
            )
    
    def get_cache_key(self, operation: str, *args) -> str:
        """Generate cache key for operations"""
        key_data = f"{operation}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def check_server_health(self, server_url: str) -> ServerHealth:
        """Check health of a single MCP server"""
        start_time = time.time()
        health = self.server_health[server_url]
        
        try:
            async with httpx.AsyncClient(timeout=MCP_DISCOVERY_TIMEOUT) as client:
                response = await client.get(f"{server_url.rstrip('/')}/tools")
                response.raise_for_status()
                
                response_time = time.time() - start_time
                health.is_healthy = True
                health.response_time = response_time
                health.last_check = datetime.now()
                health.error_count = max(0, health.error_count - 1)  # Decay error count
                
                # Try to detect server capabilities
                tools = response.json()
                if isinstance(tools, list):
                    health.capabilities = [tool.get('name', '') for tool in tools]
                
        except Exception as e:
            health.is_healthy = False
            health.last_error = str(e)
            health.error_count += 1
            health.last_check = datetime.now()
            health.response_time = time.time() - start_time
            
            logger.warning(f"Server {server_url} health check failed: {e}")
        
        return health
    
    async def check_all_servers_health(self) -> Dict[str, ServerHealth]:
        """Check health of all servers in parallel"""
        tasks = [self.check_server_health(server) for server in self.servers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, ServerHealth):
                self.server_health[self.servers[i]] = result
        
        return self.server_health
    
    async def discover_tools_from_server(self, server_url: str) -> List[ToolInfo]:
        """Discover tools from a single server with enhanced metadata"""
        async with self.semaphore:
            try:
                async with httpx.AsyncClient(timeout=MCP_DISCOVERY_TIMEOUT) as client:
                    response = await client.get(f"{server_url.rstrip('/')}/tools")
                    response.raise_for_status()
                    tools_data = response.json()
                
                tools = []
                for tool_data in tools_data:
                    # Extract tool information
                    tool_info = ToolInfo(
                        name=tool_data.get('name', ''),
                        description=tool_data.get('description', ''),
                        parameters=tool_data.get('parameters', {}),
                        server_url=server_url,
                        category=self._categorize_tool(tool_data.get('name', ''), tool_data.get('description', '')),
                        tags=self._extract_tags(tool_data.get('name', ''), tool_data.get('description', ''))
                    )
                    
                    tools.append(tool_info)
                    
                    # Cache the tool
                    cache_key = f"{server_url}:{tool_info.name}"
                    self.tool_cache[cache_key] = tool_info
                
                return tools
                
            except Exception as e:
                logger.error(f"Failed to discover tools from {server_url}: {e}")
                raise MCPClientError(f"Tool discovery failed: {e}", server_url=server_url)
    
    def _categorize_tool(self, name: str, description: str) -> str:
        """Categorize tools based on name and description"""
        name_lower = name.lower()
        desc_lower = description.lower()
        
        if any(keyword in name_lower or keyword in desc_lower 
               for keyword in ['file', 'read', 'write', 'directory', 'folder']):
            return 'file_operations'
        elif any(keyword in name_lower or keyword in desc_lower 
                for keyword in ['web', 'search', 'url', 'http', 'internet']):
            return 'web_operations'
        elif any(keyword in name_lower or keyword in desc_lower 
                for keyword in ['system', 'process', 'cpu', 'memory', 'disk']):
            return 'system_operations'
        elif any(keyword in name_lower or keyword in desc_lower 
                for keyword in ['calculate', 'math', 'compute', 'number']):
            return 'computation'
        else:
            return 'general'
    
    def _extract_tags(self, name: str, description: str) -> List[str]:
        """Extract tags from tool name and description"""
        tags = []
        text = f"{name} {description}".lower()
        
        # Common tag patterns
        tag_patterns = {
            'async': ['async', 'asynchronous'],
            'cached': ['cache', 'cached'],
            'secure': ['secure', 'safe', 'security'],
            'batch': ['batch', 'bulk', 'multiple'],
            'realtime': ['real-time', 'live', 'instant'],
            'ai': ['ai', 'ml', 'intelligence', 'smart'],
            'data': ['data', 'database', 'storage'],
            'network': ['network', 'internet', 'connection']
        }
        
        for tag, keywords in tag_patterns.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    async def discover_all_tools(self, force_refresh: bool = False) -> Dict[str, List[ToolInfo]]:
        """Discover all tools from all servers in parallel"""
        current_time = time.time()
        
        # Check if we need to refresh
        if not force_refresh and current_time - self.last_discovery < MCP_CACHE_TTL:
            # Return cached results
            cached_tools = {}
            for cache_key, tool in self.tool_cache.items():
                server_url = tool.server_url
                if server_url not in cached_tools:
                    cached_tools[server_url] = []
                cached_tools[server_url].append(tool)
            return cached_tools
        
        # Check server health first
        await self.check_all_servers_health()
        
        # Only discover from healthy servers
        healthy_servers = [
            server for server, health in self.server_health.items() 
            if health.is_healthy
        ]
        
        if not healthy_servers:
            logger.warning("No healthy servers available for tool discovery")
            return {}
        
        # Discover tools in parallel
        tasks = [self.discover_tools_from_server(server) for server in healthy_servers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        discovered_tools = {}
        for i, result in enumerate(results):
            server_url = healthy_servers[i]
            if isinstance(result, list):
                discovered_tools[server_url] = result
            else:
                logger.error(f"Tool discovery failed for {server_url}: {result}")
                discovered_tools[server_url] = []
        
        self.last_discovery = current_time
        return discovered_tools
    
    async def get_tool_schema_cached(self, server_url: str, tool_name: str) -> Dict[str, Any]:
        """Get tool schema with caching"""
        cache_key = f"{server_url}:{tool_name}:schema"
        
        if cache_key in self.schema_cache:
            return self.schema_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=MCP_DISCOVERY_TIMEOUT) as client:
                response = await client.get(f"{server_url.rstrip('/')}/tools/{tool_name}/schema")
                response.raise_for_status()
                schema = response.json()
                
                # Cache the schema
                self.schema_cache[cache_key] = schema
                return schema
                
        except Exception as e:
            raise MCPClientError(f"Failed to get schema for {tool_name}: {e}", 
                               server_url=server_url, tool_name=tool_name)
    
    async def execute_tool_with_retry(self, server_url: str, tool_name: str, 
                                    parameters: dict, max_retries: int = None) -> ExecutionResult:
        """Execute tool with retry logic and caching"""
        if max_retries is None:
            max_retries = MCP_MAX_RETRIES
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Validate parameters
                schema = await self.get_tool_schema_cached(server_url, tool_name)
                validate(instance=parameters, schema=schema)
                
                # Execute tool
                async with httpx.AsyncClient(timeout=MCP_EXECUTION_TIMEOUT) as client:
                    response = await client.post(
                        f"{server_url.rstrip('/')}/tools/{tool_name}/execute",
                        json=parameters
                    )
                    response.raise_for_status()
                    result = response.json()
                
                execution_time = time.time() - start_time
                
                # Update tool usage statistics
                cache_key = f"{server_url}:{tool_name}"
                if cache_key in self.tool_cache:
                    tool_info = self.tool_cache[cache_key]
                    tool_info.usage_count += 1
                    tool_info.last_used = datetime.now()
                    tool_info.avg_response_time = (
                        (tool_info.avg_response_time * (tool_info.usage_count - 1) + execution_time) /
                        tool_info.usage_count
                    )
                
                return ExecutionResult(
                    tool_name=tool_name,
                    server_url=server_url,
                    parameters=parameters,
                    result=result,
                    success=True,
                    execution_time=execution_time,
                    timestamp=datetime.now()
                )
                
            except ValidationError as ve:
                error_msg = f"Parameter validation failed: {ve.message}"
                return ExecutionResult(
                    tool_name=tool_name,
                    server_url=server_url,
                    parameters=parameters,
                    result=None,
                    success=False,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    error=error_msg
                )
                
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Tool execution attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Tool execution failed after {max_retries + 1} attempts: {e}")
        
        return ExecutionResult(
            tool_name=tool_name,
            server_url=server_url,
            parameters=parameters,
            result=None,
            success=False,
            execution_time=time.time() - start_time,
            timestamp=datetime.now(),
            error=f"Failed after {max_retries + 1} attempts: {last_error}"
        )
    
    async def execute_multiple_tools(self, tool_requests: List[Tuple[str, str, dict]]) -> List[ExecutionResult]:
        """Execute multiple tools in parallel"""
        async with self.semaphore:
            tasks = [
                self.execute_tool_with_retry(server_url, tool_name, parameters)
                for server_url, tool_name, parameters in tool_requests
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            execution_results = []
            for i, result in enumerate(results):
                if isinstance(result, ExecutionResult):
                    execution_results.append(result)
                else:
                    server_url, tool_name, parameters = tool_requests[i]
                    execution_results.append(ExecutionResult(
                        tool_name=tool_name,
                        server_url=server_url,
                        parameters=parameters,
                        result=None,
                        success=False,
                        execution_time=0,
                        timestamp=datetime.now(),
                        error=f"Execution failed: {result}"
                    ))
            
            return execution_results
    
    def get_tools_by_category(self, category: str) -> List[ToolInfo]:
        """Get all tools of a specific category"""
        return [tool for tool in self.tool_cache.values() if tool.category == category]
    
    def get_tools_by_tags(self, tags: List[str]) -> List[ToolInfo]:
        """Get tools that match any of the given tags"""
        matching_tools = []
        for tool in self.tool_cache.values():
            if tool.tags and any(tag in tool.tags for tag in tags):
                matching_tools.append(tool)
        return matching_tools
    
    def get_server_statistics(self) -> Dict[str, Any]:
        """Get comprehensive server statistics"""
        stats = {
            "servers": {},
            "tools": {
                "total_count": len(self.tool_cache),
                "by_category": {},
                "by_server": {},
                "most_used": [],
                "fastest_response": []
            }
        }
        
        # Server statistics
        for server_url, health in self.server_health.items():
            stats["servers"][server_url] = {
                "healthy": health.is_healthy,
                "response_time": health.response_time,
                "error_count": health.error_count,
                "last_check": health.last_check.isoformat(),
                "capabilities": health.capabilities or []
            }
        
        # Tool statistics
        category_counts = {}
        server_counts = {}
        
        for tool in self.tool_cache.values():
            # Count by category
            category_counts[tool.category] = category_counts.get(tool.category, 0) + 1
            
            # Count by server
            server_counts[tool.server_url] = server_counts.get(tool.server_url, 0) + 1
        
        stats["tools"]["by_category"] = category_counts
        stats["tools"]["by_server"] = server_counts
        
        # Most used tools
        used_tools = [tool for tool in self.tool_cache.values() if tool.usage_count > 0]
        used_tools.sort(key=lambda x: x.usage_count, reverse=True)
        stats["tools"]["most_used"] = [
            {"name": tool.name, "server": tool.server_url, "usage_count": tool.usage_count}
            for tool in used_tools[:10]
        ]
        
        # Fastest tools
        fast_tools = [tool for tool in self.tool_cache.values() if tool.avg_response_time > 0]
        fast_tools.sort(key=lambda x: x.avg_response_time)
        stats["tools"]["fastest_response"] = [
            {"name": tool.name, "server": tool.server_url, "avg_response_time": tool.avg_response_time}
            for tool in fast_tools[:10]
        ]
        
        return stats

# Global client instance
_client_instance = None

def get_mcp_client() -> EnhancedMCPClient:
    """Get the global MCP client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = EnhancedMCPClient()
    return _client_instance

# Backward compatibility functions
async def discover_all_tools() -> Dict[str, List[Dict[str, Any]]]:
    """Backward compatible tool discovery"""
    client = get_mcp_client()
    tools_by_server = await client.discover_all_tools()
    
    # Convert ToolInfo objects to dictionaries
    result = {}
    for server_url, tools in tools_by_server.items():
        result[server_url] = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category,
                "tags": tool.tags
            }
            for tool in tools
        ]
    
    return result

async def execute_tool(server_url: str, tool_name: str, parameters: dict) -> Dict[str, Any]:
    """Backward compatible tool execution"""
    client = get_mcp_client()
    result = await client.execute_tool_with_retry(server_url, tool_name, parameters)
    
    if result.success:
        return result.result
    else:
        raise MCPClientError(result.error, server_url=server_url, tool_name=tool_name)

def list_mcp_servers() -> List[str]:
    """List configured MCP servers"""
    return [url.strip() for url in MCP_SERVER_URLS if url.strip()]