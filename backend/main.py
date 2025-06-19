# backend/main.py
"""Enhanced FastAPI server that connects the frontend with LLMs and MCP tools.

Endpoints:
    * ``/api/tools`` -- list tools discovered from MCP servers
    * ``/api/echo``  -- route a user message through an LLM and optional tools
    * ``/api/tools/stats`` -- get MCP server and tool statistics
    * ``/api/tools/recommendations`` -- get tool recommendations

Key features:
    * Intelligent tool selection beyond keyword matching
    * Parallel tool execution and discovery
    * Server health monitoring
    * Enhanced error handling and retry logic
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import both old and new MCP clients for backward compatibility
from .mcp_client import MCPClientError
from .enhanced_mcp_client import get_mcp_client, EnhancedMCPClient
from .intelligent_tool_selector import get_intelligent_selector, ToolMatch

import time
import asyncio
import openai
import logging
from backend.config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = get_config()

openai.api_key = config.openai.api_key
OPENAI_MODEL = config.openai.model
CLAUDE_API_KEY = config.claude_api_key
OLLAMA_ENDPOINT = config.ollama_endpoint
USE_INTELLIGENT_SELECTION = config.use_intelligent_selection

# Initialize enhanced MCP client and intelligent selector
mcp_client = get_mcp_client()
intelligent_selector = get_intelligent_selector()

app = FastAPI(title="Echo Enhanced API", version="1.1.0")

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
    """List all available tools from MCP servers"""
    try:
        tools_by_server = await mcp_client.discover_all_tools()
        
        # Flatten tool list for frontend with enhanced metadata
        flat_tools = []
        for server_url, tools in tools_by_server.items():
            for tool in tools:
                flat_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "server_url": tool.server_url,
                    "category": tool.category,
                    "tags": tool.tags or [],
                    "usage_count": tool.usage_count,
                    "avg_response_time": tool.avg_response_time,
                    "last_used": tool.last_used.isoformat() if tool.last_used else None
                })
        
        return {
            "tools": flat_tools,
            "total_count": len(flat_tools),
            "servers": list(tools_by_server.keys())
        }
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@app.get("/api/tools/stats")
async def get_tools_stats():
    """Get comprehensive MCP server and tool statistics"""
    try:
        stats = mcp_client.get_server_statistics()
        selection_stats = intelligent_selector.get_selection_statistics()
        
        return {
            "server_stats": stats,
            "selection_stats": selection_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/tools/recommendations")
async def get_tool_recommendations(limit: int = 5):
    """Get tool recommendations based on usage patterns"""
    try:
        recommendations = intelligent_selector.get_tool_recommendations(limit)
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

class EchoRequest(BaseModel):
    message: str
    context: Optional[List[str]] = None
    use_intelligent_selection: Optional[bool] = None

class ToolSelectionRequest(BaseModel):
    message: str
    context: Optional[List[str]] = None
    max_tools: int = 3

# OpenAI LLM router
def llm_router(message: str) -> str:
    if not OPENAI_API_KEY:
        return "[Echo] Error: OPENAI_API_KEY is not set."
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": message}],
            max_tokens=512,  # Increased for better responses
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Echo] OpenAI API error: {e}"

# --- Backward Compatibility Functions ---
async def get_mcp_tools(force_refresh: bool = False):
    """Backward compatible tool discovery"""
    tools_by_server = await mcp_client.discover_all_tools(force_refresh)
    
    # Convert to old format for backward compatibility
    result = {}
    for server_url, tools in tools_by_server.items():
        result[server_url] = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in tools
        ]
    
    return result

def find_relevant_tool(user_message: str, mcp_tools: dict) -> tuple:
    """Legacy keyword-based tool selection (fallback)"""
    TOOL_KEYWORDS = ["calculate", "calculation", "math", "sum", "add", "subtract", "multiply", "divide", "search", "web", "lookup"]
    
    msg_lower = user_message.lower()
    for server_url, tools in mcp_tools.items():
        for tool in tools:
            for keyword in TOOL_KEYWORDS:
                if keyword in msg_lower and keyword in tool["name"].lower():
                    return server_url, tool["name"], tool
                if keyword in msg_lower and keyword in tool.get("description", "").lower():
                    return server_url, tool["name"], tool
    return None, None, None

def extract_parameters_from_message(message: str, tool_match: ToolMatch) -> dict:
    """Extract parameters from user message based on tool requirements and entities"""
    params = {}
    entities = tool_match.entities or {}
    tool = tool_match.tool
    
    if not tool.parameters:
        return params
    
    # Map entities to parameters
    entity_param_mapping = {
        'file_path': ['file_path', 'path', 'filename', 'directory_path'],
        'url': ['url', 'web_url', 'link'],
        'search_query': ['query', 'search_term', 'text'],
        'math_expression': ['expression', 'formula', 'equation'],
        'process_name': ['process_name', 'service_name', 'name'],
        'number': ['amount', 'value', 'number']
    }
    
    # Map entities to parameters
    for entity_type, entity_values in entities.items():
        if entity_type in entity_param_mapping:
            for param_name in entity_param_mapping[entity_type]:
                if param_name in tool.parameters:
                    # Use the first entity value
                    params[param_name] = entity_values[0] if entity_values else message
                    break
    
    # Fill in missing required parameters with the message
    for param_name in tool.parameters.keys():
        if param_name not in params:
            if param_name in ['query', 'text', 'message', 'input']:
                params[param_name] = message
            elif param_name in ['expression', 'formula'] and any(op in message for op in ['+', '-', '*', '/', '=']):
                # Extract mathematical expression
                import re
                math_expr = re.search(r'[\d\s+\-*/.()]+', message)
                params[param_name] = math_expr.group(0).strip() if math_expr else message
            else:
                params[param_name] = message  # Default fallback
    
    return params

@app.post("/api/tools/select")
async def select_tools_endpoint(req: ToolSelectionRequest):
    """Select the best tools for a user message using intelligent selection"""
    try:
        tool_matches = await intelligent_selector.select_tools(
            req.message, 
            req.context, 
            req.max_tools
        )
        
        return {
            "message": req.message,
            "selected_tools": [
                {
                    "tool_name": match.tool.name,
                    "server_url": match.tool.server_url,
                    "confidence": match.confidence,
                    "reasons": match.reasons,
                    "intent": match.intent,
                    "category": match.tool.category,
                    "description": match.tool.description
                }
                for match in tool_matches
            ],
            "total_matches": len(tool_matches)
        }
    except Exception as e:
        logger.error(f"Tool selection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tool selection failed: {str(e)}")

@app.post("/api/echo")
async def echo_endpoint(req: EchoRequest):
    """Enhanced echo endpoint with intelligent tool selection and parallel execution"""
    start_time = time.time()
    tools_used = []
    tool_errors = []
    
    # Determine whether to use intelligent selection
    use_intelligent = req.use_intelligent_selection if req.use_intelligent_selection is not None else USE_INTELLIGENT_SELECTION
    
    try:
        if use_intelligent:
            # Use intelligent tool selection
            tool_matches = await intelligent_selector.select_tools(req.message, req.context, max_tools=2)
            
            if tool_matches:
                # Execute tools in parallel (limit to top 2 for performance)
                tool_requests = []
                for match in tool_matches[:2]:
                    params = extract_parameters_from_message(req.message, match)
                    tool_requests.append((match.tool.server_url, match.tool.name, params))
                
                if tool_requests:
                    execution_results = await mcp_client.execute_multiple_tools(tool_requests)
                    
                    for i, result in enumerate(execution_results):
                        match = tool_matches[i]
                        
                        if result.success:
                            tools_used.append({
                                "name": result.tool_name,
                                "server_url": result.server_url,
                                "parameters": result.parameters,
                                "result": result.result.get("result", result.result) if isinstance(result.result, dict) else result.result,
                                "execution_time": result.execution_time,
                                "confidence": match.confidence,
                                "intent": match.intent,
                                "selection_reasons": match.reasons
                            })
                            
                            # Record successful usage
                            intelligent_selector.record_tool_usage(result.server_url, result.tool_name)
                        else:
                            tool_errors.append({
                                "name": result.tool_name,
                                "server_url": result.server_url,
                                "error": result.error,
                                "confidence": match.confidence
                            })
        else:
            # Fall back to legacy keyword-based selection
            mcp_tools = await get_mcp_tools()
            server_url, tool_name, tool_info = find_relevant_tool(req.message, mcp_tools)
            
            if server_url and tool_name:
                # Simple parameter extraction
                params = {}
                if "expression" in (tool_info.get("parameters", {}) or {}):
                    params = {"expression": req.message}
                elif "query" in (tool_info.get("parameters", {}) or {}):
                    params = {"query": req.message}
                else:
                    params = {k: req.message for k in (tool_info.get("parameters", {}) or {}).keys()}
                
                try:
                    # Use the enhanced client for execution
                    result = await mcp_client.execute_tool_with_retry(server_url, tool_name, params)
                    
                    if result.success:
                        tools_used.append({
                            "name": tool_name,
                            "server_url": server_url,
                            "parameters": params,
                            "result": result.result.get("result", result.result) if isinstance(result.result, dict) else result.result,
                            "execution_time": result.execution_time,
                            "selection_method": "keyword_matching"
                        })
                    else:
                        tool_errors.append({
                            "name": tool_name,
                            "server_url": server_url,
                            "error": result.error,
                            "selection_method": "keyword_matching"
                        })
                        
                except Exception as e:
                    tool_errors.append({
                        "name": tool_name,
                        "server_url": server_url,
                        "error": f"Execution failed: {str(e)}",
                        "selection_method": "keyword_matching"
                    })
        
        # Compose LLM context with tool results
        llm_context = req.message
        
        if tools_used:
            tool_context = "\n\n[Tool Results:\n"
            for tool in tools_used:
                tool_context += f"- {tool['name']}: {tool['result']}\n"
            tool_context += "]"
            llm_context += tool_context
        
        if tool_errors:
            error_context = "\n\n[Tool Errors:\n"
            for error in tool_errors:
                error_context += f"- {error['name']}: {error['error']}\n"
            error_context += "]"
            llm_context += error_context
        
        # Get LLM response
        response = llm_router(llm_context)
        
        end_time = time.time()
        
        return {
            "response": response,
            "tools_used": tools_used,
            "tool_errors": tool_errors,
            "model_used": OPENAI_MODEL,
            "processing_time": round(end_time - start_time, 2),
            "selection_method": "intelligent" if use_intelligent else "keyword",
            "total_tools_attempted": len(tools_used) + len(tool_errors)
        }
        
    except Exception as e:
        logger.error(f"Echo endpoint error: {e}")
        end_time = time.time()
        
        return {
            "response": f"[Echo] Error processing request: {str(e)}",
            "tools_used": tools_used,
            "tool_errors": tool_errors,
            "model_used": OPENAI_MODEL,
            "processing_time": round(end_time - start_time, 2),
            "error": str(e)
        }
