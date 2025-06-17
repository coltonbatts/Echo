# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .mcp_client import discover_tools
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

@app.post("/api/echo")
async def echo_endpoint(req: EchoRequest):
    response = llm_router(req.message)
    return {"response": response}
