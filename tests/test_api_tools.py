import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from fastapi.testclient import TestClient
from backend import main

def test_tools_endpoint_structure(monkeypatch):
    async def mock_discover_all_tools():
        return {
            "http://mockserver": [
                {"name": "calculator", "description": "Adds numbers", "parameters": {"expression": {"type": "string"}}}
            ]
        }

    # Clear cache and patch discovery
    main.MCP_TOOLS_CACHE = {}
    main.MCP_TOOLS_LAST_REFRESH = 0
    monkeypatch.setattr(main, "discover_all_tools", mock_discover_all_tools)

    client = TestClient(main.app)
    resp = client.get("/api/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {
        "tools": [
            {
                "name": "calculator",
                "description": "Adds numbers",
                "server_url": "http://mockserver"
            }
        ]
    }
