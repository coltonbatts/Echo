# backend/main.py
"""FastAPI server that connects the frontend with LLMs and MCP tools.

Endpoints:
    * ``/api/tools`` -- list tools discovered from MCP servers
    * ``/api/echo``  -- route a user message through an LLM and optional tools

Key helpers:
    ``llm_router`` routes text to OpenAI,
    ``get_mcp_tools`` caches tool discovery,
    ``find_relevant_tool`` picks a tool based on simple keywords.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .mcp_client import (
    list_mcp_servers,
    discover_all_tools,
    execute_tool,
    MCPClientError
)
import time
import asyncio
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env at project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT')
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL')

openai.api_key = OPENAI_API_KEY

app = FastAPI()

# Allow frontend to talk to backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/tools")
async def list_tools():
    tools = await get_mcp_tools()
    # Flatten tool list for frontend: [{name, description, server_url}]
    flat_tools = []
    for server_url, tool_list in (tools or {}).items():
        for tool in tool_list:
            flat_tools.append({
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "server_url": server_url
            })
    return {"tools": flat_tools}

class EchoRequest(BaseModel):
    message: str

# OpenAI LLM router
def llm_router(message: str) -> str:
    if not OPENAI_API_KEY:
        return "[Echo] Error: OPENAI_API_KEY is not set."
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": message}],
            max_tokens=256,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Echo] OpenAI API error: {e}"

# --- MCP Tool Discovery Cache ---
MCP_TOOLS_CACHE = {}
MCP_TOOLS_LAST_REFRESH = 0
MCP_TOOLS_REFRESH_INTERVAL = 60  # seconds

async def get_mcp_tools(force_refresh: bool = False):
    global MCP_TOOLS_CACHE, MCP_TOOLS_LAST_REFRESH
    now = time.time()
    if force_refresh or (now - MCP_TOOLS_LAST_REFRESH > MCP_TOOLS_REFRESH_INTERVAL):
        try:
            MCP_TOOLS_CACHE = await discover_all_tools()
            MCP_TOOLS_LAST_REFRESH = now
        except Exception:
            pass  # If discovery fails, keep old cache
    return MCP_TOOLS_CACHE

# --- Tool Usage Heuristic ---
TOOL_KEYWORDS = ["calculate", "calculation", "math", "sum", "add", "subtract", "multiply", "divide", "search", "web", "lookup"]

def find_relevant_tool(user_message: str, mcp_tools: dict) -> tuple:
    msg_lower = user_message.lower()
    for server_url, tools in mcp_tools.items():
        for tool in tools:
            for keyword in TOOL_KEYWORDS:
                if keyword in msg_lower and keyword in tool["name"].lower():
                    return server_url, tool["name"], tool
                if keyword in msg_lower and keyword in tool.get("description", "").lower():
                    return server_url, tool["name"], tool
    return None, None, None

@app.post("/api/echo")
async def echo_endpoint(req: EchoRequest):
    start_time = time.time()
    tools_used = []
    mcp_tools = await get_mcp_tools()
    server_url, tool_name, tool_info = find_relevant_tool(req.message, mcp_tools)
    tool_result = None
    tool_error = None
    # Try tool if relevant
    if server_url and tool_name:
        # Simple parameter extraction: pass whole message as 'query' or 'expression' if tool expects it
        params = {}
        if "expression" in (tool_info.get("parameters", {}) or {}):
            params = {"expression": req.message}
        elif "query" in (tool_info.get("parameters", {}) or {}):
            params = {"query": req.message}
        else:
            params = {k: req.message for k in (tool_info.get("parameters", {}) or {}).keys()}
        try:
            tool_result = await execute_tool(server_url, tool_name, params)
            tools_used.append({
                "name": tool_name,
                "parameters": params,
                "result": tool_result.get("result", tool_result)
            })
        except MCPClientError as e:
            tool_error = str(e)
        except Exception as e:
            tool_error = f"Unexpected MCP error: {e}"
    # Compose LLM context with tool result if available
    llm_context = req.message
    if tool_result:
        llm_context += f"\n\n[Tool {tool_name} result: {tool_result.get('result', tool_result)}]"
    elif tool_error:
        llm_context += f"\n\n[Tool {tool_name} error: {tool_error}]"
    response = llm_router(llm_context)
    end_time = time.time()
    return {
        "response": response,
        "tools_used": tools_used,
        "model_used": OPENAI_MODEL,
        "processing_time": round(end_time - start_time, 2)
    }
