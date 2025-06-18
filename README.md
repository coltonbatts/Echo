# Echo

**A modular AI infrastructure platform for creative technologists.**

Echo breaks free from monolithic AI platforms by treating intelligence as composable modules. Mix and match LLM providers, integrate MCP-compliant tools, and orchestrate sophisticated AI workflows—all through a unified, vendor-agnostic interface.

Built Docker-first for maximum portability. No vendor lock-in. Maximum flexibility.

---

## 🎯 Vision: Modular AI Composition

Traditional AI platforms lock you into their ecosystem. Echo does the opposite—it's designed as an orchestration layer that composes heterogeneous AI capabilities:

- **🧠 LLM Providers**: OpenAI, Anthropic Claude, local Ollama models, or emerging providers
- **🔧 MCP Tools**: Web search, file operations, databases, APIs—any MCP-compliant server
- **🤖 Agent Workflows**: Chain reasoning, tool usage, and decision logic into autonomous processes
- **🔄 Dynamic Discovery**: Tools and capabilities are discovered at runtime, not hardcoded

All orchestrated through a single, clean interface that adapts to your workflow.

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  External APIs  │
│   (Nginx)       │────│   (FastAPI)     │────│  & MCP Servers  │
│                 │    │                 │    │                 │
│ • Modern UI     │    │ • LLM Router    │    │ • OpenAI/Claude │
│ • Tool Display  │    │ • MCP Client    │    │ • Ollama        │
│ • Live Updates  │    │ • Tool Executor │    │ • Custom Tools  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

- **Frontend**: Modern, dark-mode chat interface served by Nginx with live tool discovery
- **Backend**: FastAPI server with pluggable LLM routing and async MCP integration
- **LLM Router**: Intelligent model selection based on task requirements (OpenAI, Claude, Ollama)
- **MCP Client**: Dynamic tool discovery, schema validation, and execution
- **Tool Orchestration**: Automatic tool detection and intelligent parameter mapping

---

## ✨ Features

### Current Capabilities
- 🎨 **Modern Chat Interface**: Claude-style dark UI with real-time tool visibility
- 🔌 **Modular LLM Support**: Easy switching between OpenAI, Claude, and local models
- 🛠️ **MCP Tool Integration**: Automatic discovery and execution of MCP-compliant tools
- 🐳 **Docker-First**: Fully containerized for development and production
- 🔄 **Live Reload**: Code changes reflected instantly in development
- 📊 **Tool Transparency**: See which tools are used and their results
- ⚡ **Async Everything**: Non-blocking tool discovery and execution

### Smart Tool Detection
Echo automatically detects when to use tools based on message content:
- **Math operations** → Calculator tools
- **Web queries** → Search tools
- **File operations** → File system tools
- **API calls** → Custom MCP servers

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key (optional: Claude API key, Ollama setup)

### 1. Clone and Configure
```bash
git clone https://github.com/coltonbatts/Echo.git
cd Echo
cp .env.example .env
# Edit .env with your API keys
```

### 2. Launch with Docker (Recommended)
```bash
docker compose up --build
```

- **🌐 Frontend**: [http://localhost](http://localhost)
- **📚 API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **🔧 Tools API**: [http://localhost:8000/api/tools](http://localhost:8000/api/tools)

### 3. Local Development (Advanced)
```bash
# Terminal 1: Backend
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload

# Terminal 2: Open frontend/index.html or serve it
python -m http.server 3000 --directory frontend
```

---
git clone https://github.com/coltonbatts/Echo.git
cd Echo
```

### 2. Set up configuration
- Copy `.env.example` to `.env` and add your API keys or endpoints as needed.
- **Never commit real keys to version control!**

### 3. Local Development
1. **Install dependencies**
   ```bash
   pip install fastapi uvicorn openai pyyaml
   ```
2. **Start the backend**
   ```bash
   uvicorn backend.main:app --reload
   ```
3. **Open the frontend**
   - Open `http://localhost:8000` in your browser.

### 4. Docker (Recommended for full isolation)
1. **Build and run everything**
    ```bash
    docker compose up --build
    ```
    - **Frontend:** [http://localhost](http://localhost) ← served by Nginx container, proxies API calls to backend
    - **Backend:** [http://localhost:8000](http://localhost:8000) (API only; not for direct user access)
    - **API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
2. **Live reload:** Code changes are reflected automatically in the containers if you use volume mounts (default in `docker-compose.yml`).
    - To force reload, restart the containers: `docker compose restart`
   - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
2. **Frontend:** Open `frontend/index.html` (not served by backend)
3. **Live reload:** Code changes are reflected automatically in the container.

---

## API Endpoints
- `POST /api/echo` – Main chat endpoint (expects JSON, returns LLM response)
- `GET /docs` – FastAPI interactive API docs
- `GET /` – Not implemented (returns 404 by design)

---

## Development Notes
- **Frontend:** Pure HTML/CSS, no build step, open directly.
- **Backend:** Modular FastAPI app, ready for LLM and MCP integration.
- **Docker:** Lightweight, production-ready config. Mounts code for live reload.
- **Extending:** Add new LLMs/tools by editing `llm_router.py` and `mcp_client.py`.

### Running Tests
Echo includes a small pytest suite under `tests/`.

```bash
pip install -r backend/requirements.txt
pip install pytest respx
pytest
```

---

## Roadmap
- Real LLM routing (OpenAI, Claude, Ollama, etc)
- Live MCP tool discovery and invocation
- Desktop app via Tauri
- Persistent chat history

---

> Echo is a personal creative-tech companion. Not for corporate use.
