# Echo

![version](https://img.shields.io/badge/version-0.1-green)

**A modular AI infrastructure platform for creative technologists.**

## ⚙️ Centralized Configuration System (v1.1)

Echo now uses a robust, centralized configuration system based on **Pydantic v2** and **YAML** files, supporting layered overrides via environment variables and `.env` files.

### How It Works
- **YAML files** in `config/` provide base, development, and production configs.
- **Environment variables** and a local `.env` file can override any setting (see `.env.example`).
- All config is validated and loaded via Pydantic models for type safety and reliability.

### Onboarding Steps
1. **Copy `.env.example` to `.env`** and fill in required secrets and API keys.
2. **Review and customize YAML configs** in `config/` as needed for your environment.
3. **Install dependencies:**
   ```sh
   pip install -r backend/requirements.txt
   pip install pydantic-settings
   ```
4. **Run tests:**
   ```sh
   PYTHONPATH=. pytest tests/test_configuration.py
   ```

### Configuration Structure
- **config/base.yaml**: Default settings for all environments.
- **config/development.yaml**: Development overrides (debug, local MCP servers, etc).
- **config/production.yaml**: Production overrides (rate limits, feature flags, etc).
- **.env**: Local secrets and environment-specific overrides (never commit this file).

**Precedence:**
1. Environment variables / `.env`
2. YAML (environment-specific)
3. YAML (base)

### Example
See `.env.example` and YAML files in `config/` for all available settings and documentation.

---

**Version 0.1 – June 18, 2025**
- 🟢 First working checkpoint: Docker Compose, backend (FastAPI), frontend (Nginx), React dev server, and chat proxy integration
- ✅ All smoke tests passing (backend health, frontend loads, React chat API, OpenAI relay)
- See below for setup and usage steps.

---

## v0.1 Changelog
- Initial working integration of backend (FastAPI), frontend (Nginx), and React dev chat app.
- ChatBox in React proxies `/api/echo` to backend via `src/setupProxy.js`.
- All containers and dev tools run via Docker Compose and `npm start`.
- All smoke tests pass: backend health, frontend loads, chat API connects, OpenAI relay works.

---

## 🆕 Enhanced MCP Architecture (June 2025)

Echo now supports a robust, intelligent, and scalable Modular Command Protocol (MCP) ecosystem:

### New MCP Servers
- **File Operations Server** (`mcp_servers/file_server.py`): File reading/writing, directory ops, file search, binary support, sandboxed
- **Web Search Server** (`mcp_servers/web_server.py`): DuckDuckGo search, webpage/content/link extraction, rate limiting, caching
- **System Utilities Server** (`mcp_servers/system_server.py`): System info, performance, process management, safe command execution

### Enhanced MCP Client
- Parallel tool execution, health monitoring, TTL caching, retry logic, usage analytics

### Intelligent Tool Selection
- Entity extraction, intent detection, semantic analysis, learning from usage, confidence scoring

### New API Endpoints
- `/api/tools/stats`: MCP server and tool statistics
- `/api/tools/recommendations`: Usage-based recommendations
- `/api/tools/select`: Intelligent tool selection testing
- Enhanced `/api/echo`: Parallel tool execution, smart parameter extraction

### Management & Testing
- `scripts/start_mcp_servers.py`: Start/stop/monitor all MCP servers
- Full test suite: `tests/test_enhanced_mcp.py`
- Updated `.env.example` and documentation

**Key Improvements:**
- Moves beyond keyword matching to semantic tool selection
- Parallel execution and intelligent caching for performance
- Health monitoring, retry logic, and error handling for reliability
- Easy extensibility for new tool categories
- Detailed statistics and usage tracking for observability

**Usage:**
```bash
# Start all MCP servers (in a virtualenv)
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python scripts/start_mcp_servers.py

# Test intelligent tool selection
curl -X POST "http://localhost:8000/api/tools/select" \
  -H "Content-Type: application/json" \
  -d '{"message": "Search for Python tutorials", "max_tools": 3}'

# Enhanced echo with intelligent selection
curl -X POST "http://localhost:8000/api/echo" \
  -H "Content-Type: application/json" \
  -d '{"message": "Read the file config.txt", "use_intelligent_selection": true}'
```

See the CLAUDE.md for full documentation.

---

## 🚀 v0.1 Setup & Usage
1. **Clone the repo and copy `.env.example` to `.env`**
   - Add your `OPENAI_API_KEY` and any other required secrets.
2. **Start all services:**
   ```bash
   docker compose up -d --build
   ```
   - Backend: [http://localhost:8000](http://localhost:8000) (API)
   - Frontend: [http://localhost/](http://localhost/) (Nginx)
3. **Run the React dev app:**
   ```bash
   cd echo-blackgreen
   npm install
   npm start
   ```
   - React dev: [http://localhost:3000](http://localhost:3000)
   - ChatBox will now connect to backend via proxy for `/api/echo` requests.
4. **Smoke tests:**
   - Backend health: `curl http://localhost:8000/` (should return 404 or health JSON)
   - Frontend: Open [http://localhost/](http://localhost/) in browser
   - React dev: Open [http://localhost:3000](http://localhost:3000) and test chat
   - Chat API: Enter message in chat; should get OpenAI-powered response

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

### Environment Variables
The `.env` file controls API keys and MCP tool settings. Important variables:

- `OPENAI_API_KEY` – OpenAI authentication (optional)
- `MCP_SERVER_URLS` – comma-separated list of MCP server endpoints
- `MCP_DISCOVERY_TIMEOUT` – tool discovery timeout (seconds)
- `MCP_EXECUTION_TIMEOUT` – tool execution timeout (seconds)

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

### Sample MCP Server for Local Testing
See [docs/sample_mcp_server.md](docs/sample_mcp_server.md) for a minimal example server you can run locally.

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
