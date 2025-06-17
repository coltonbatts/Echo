# backend/mcp_client.py
"""
Stub MCP client for discovering tools and executing tool calls.
"""

def discover_tools(mcp_url: str = "http://localhost:8001"):
    # TODO: Implement real MCP discovery
    # For now, return a mocked list of tools
    return [
        {"name": "Calculator", "description": "Performs calculations."},
        {"name": "WebSearch", "description": "Searches the web."}
    ]

def tool_call(tool_name: str, params: dict):
    # TODO: Implement tool call via MCP
    return {"result": f"Called {tool_name} with {params} (mock)"}
