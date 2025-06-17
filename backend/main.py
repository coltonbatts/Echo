# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .mcp_client import discover_tools

app = FastAPI()

# Allow frontend to talk to backend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EchoRequest(BaseModel):
    message: str

# Placeholder LLM router
def llm_router(message: str) -> str:
    # TODO: Route to local/API LLMs (OpenAI, Claude, Ollama, etc)
    return f"[Echo] You said: {message} (mock response)"

@app.post("/api/echo")
async def echo_endpoint(req: EchoRequest):
    response = llm_router(req.message)
    return {"response": response}
