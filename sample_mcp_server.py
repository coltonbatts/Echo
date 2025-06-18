from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Sample MCP Server")

# List of available tools
@app.get("/tools")
async def list_tools():
    return [{
        "name": "calculator",
        "description": "Evaluate simple math expressions",
        "parameters": {"expression": "string"}
    }]

# JSON schema for tool parameters
@app.get("/tools/{tool_name}/schema")
async def tool_schema(tool_name: str):
    if tool_name != "calculator":
        return {"error": "unknown tool"}
    return {
        "type": "object",
        "properties": {
            "expression": {"type": "string"}
        },
        "required": ["expression"]
    }

class Expr(BaseModel):
    expression: str

# Execute tool
@app.post("/tools/{tool_name}/execute")
async def execute(tool_name: str, payload: Expr):
    if tool_name != "calculator":
        return {"error": "unknown tool"}
    try:
        result = eval(payload.expression, {"__builtins__": {}})
    except Exception as e:
        return {"error": str(e)}
    return {"result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
