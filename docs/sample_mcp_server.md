# Sample MCP Server

This repository does not include a full MCP implementation, but you can run a minimal server locally for testing Echo's tool integration.

## Quick Start

1. **Install dependencies**
   ```bash
   pip install fastapi uvicorn
   ```
2. **Run the example server**
   ```bash
   python sample_mcp_server.py
   ```
   The server listens on `http://localhost:8001`.

## Tool Schema and Endpoints

The sample server exposes a single `calculator` tool with the following schema:

```json
{
  "type": "object",
  "properties": {
    "expression": { "type": "string" }
  },
  "required": ["expression"]
}
```

Available endpoints:

- `GET /tools` – list available tools.
- `GET /tools/{tool}/schema` – return JSON schema for parameters.
- `POST /tools/{tool}/execute` – execute the tool and return `{ "result": ... }`.

Set `MCP_SERVER_URLS=http://localhost:8001` in your `.env` so the Echo backend can discover this tool.
