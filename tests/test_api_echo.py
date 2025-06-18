import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from fastapi.testclient import TestClient
from backend import main

def test_echo_with_tool_execution(monkeypatch):
    async def mock_get_mcp_tools(force_refresh=False):
        return {
            "http://mockserver": [
                {"name": "calculator", "parameters": {"expression": {"type": "string"}}}
            ]
        }

    def mock_find_relevant_tool(message, tools):
        return "http://mockserver", "calculator", {"parameters": {"expression": {"type": "string"}}}

    async def mock_execute_tool(server, tool, params):
        return {"result": "42"}

    def mock_llm_router(message):
        return f"LLM:{message}"

    main.MCP_TOOLS_CACHE = {}
    main.MCP_TOOLS_LAST_REFRESH = 0
    monkeypatch.setattr(main, "get_mcp_tools", mock_get_mcp_tools)
    monkeypatch.setattr(main, "find_relevant_tool", mock_find_relevant_tool)
    monkeypatch.setattr(main, "execute_tool", mock_execute_tool)
    monkeypatch.setattr(main, "llm_router", mock_llm_router)

    client = TestClient(main.app)
    resp = client.post("/api/echo", json={"message": "calculate 2+2"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["tools_used"][0]["name"] == "calculator"
    assert data["tools_used"][0]["result"] == "42"
    assert data["response"].startswith("LLM:")

def test_echo_tool_error(monkeypatch):
    async def mock_get_mcp_tools(force_refresh=False):
        return {"http://mockserver": [{"name": "calculator", "parameters": {"expression": {"type": "string"}}}]}

    def mock_find_relevant_tool(message, tools):
        return "http://mockserver", "calculator", {"parameters": {"expression": {"type": "string"}}}

    async def mock_execute_tool(server, tool, params):
        raise main.MCPClientError("bad params")

    captured = {}
    def mock_llm_router(message):
        captured["msg"] = message
        return "LLM error"

    main.MCP_TOOLS_CACHE = {}
    main.MCP_TOOLS_LAST_REFRESH = 0
    monkeypatch.setattr(main, "get_mcp_tools", mock_get_mcp_tools)
    monkeypatch.setattr(main, "find_relevant_tool", mock_find_relevant_tool)
    monkeypatch.setattr(main, "execute_tool", mock_execute_tool)
    monkeypatch.setattr(main, "llm_router", mock_llm_router)

    client = TestClient(main.app)
    resp = client.post("/api/echo", json={"message": "calculate 2+2"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["tools_used"] == []
    assert "bad params" in captured["msg"]
