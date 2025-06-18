# backend/mcp_client.py
"""
Async-only MCP client for discovering tools and executing tool calls.
All stub/mock (non-async) code has been removed.
"""

import os
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from jsonschema import validate, ValidationError

MCP_SERVER_URLS = os.getenv("MCP_SERVER_URLS", "http://localhost:8001").split(",")
MCP_DISCOVERY_TIMEOUT = float(os.getenv("MCP_DISCOVERY_TIMEOUT", "3"))
MCP_EXECUTION_TIMEOUT = float(os.getenv("MCP_EXECUTION_TIMEOUT", "10"))

class MCPClientError(Exception):
    pass

def list_mcp_servers() -> List[str]:
    return [url.strip() for url in MCP_SERVER_URLS if url.strip()]

async def discover_tools(mcp_url: str) -> List[Dict[str, Any]]:
    """Discover available tools from a given MCP server."""
    try:
        async with httpx.AsyncClient(timeout=MCP_DISCOVERY_TIMEOUT) as client:
            resp = await client.get(f"{mcp_url.rstrip('/')}/tools")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise MCPClientError(f"Failed to discover tools from {mcp_url}: {e}")

async def get_tool_schema(mcp_url: str, tool_name: str) -> Dict[str, Any]:
    """Get parameter schema for a specific tool."""
    try:
        async with httpx.AsyncClient(timeout=MCP_DISCOVERY_TIMEOUT) as client:
            resp = await client.get(f"{mcp_url.rstrip('/')}/tools/{tool_name}/schema")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise MCPClientError(f"Failed to get schema for {tool_name} from {mcp_url}: {e}")

async def execute_tool(mcp_url: str, tool_name: str, parameters: dict) -> Dict[str, Any]:
    """Execute a tool on a given MCP server, with parameter validation."""
    try:
        schema = await get_tool_schema(mcp_url, tool_name)
        validate(instance=parameters, schema=schema)
    except ValidationError as ve:
        raise MCPClientError(f"Parameter validation failed: {ve.message}")
    except Exception as e:
        raise MCPClientError(f"Failed to fetch schema for validation: {e}")
    try:
        async with httpx.AsyncClient(timeout=MCP_EXECUTION_TIMEOUT) as client:
            resp = await client.post(f"{mcp_url.rstrip('/')}/tools/{tool_name}/execute", json=parameters)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise MCPClientError(f"Tool execution failed: {e}")

# Utility: Discover all tools from all servers (returns {server_url: [tools]})
async def discover_all_tools() -> Dict[str, List[Dict[str, Any]]]:
    servers = list_mcp_servers()
    results = {}
    for url in servers:
        try:
            tools = await discover_tools(url)
            results[url] = tools
        except Exception:
            results[url] = []
    return results
