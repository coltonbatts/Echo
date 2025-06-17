# Echo

A modular, local-first creative-tech assistant. Lightweight, cinematic, and personal. Built for creative technologists who want a hackable LLM companion that runs locally but can connect to cloud LLMs and MCP servers.

---

## Project Overview
Echo is a local-first chat assistant with a modern, minimalist frontend and a FastAPI backend. It is designed for rapid prototyping of LLM-based tools and creative workflows. The backend is ready for real LLM API integration and MCP (Modular Command Protocol) server communication.

- **Frontend:** Static HTML/CSS (Tailwind), chat UI, open in browser
- **Backend:** FastAPI, `/api/echo` endpoint, pluggable LLM router, ready for OpenAI/Claude/Ollama
- **Config:** `echo.config.json` for API keys and server endpoints
- **Docker:** Fully containerized for dev and prod

---

## Architecture

```
[ User (browser) ]
        |
        v
[ Frontend (index.html) ]
        |
        v
[ Backend (FastAPI: /api/echo) ]
        |
        v
[ LLM Router / MCP Client ]
```

- **Frontend** is static and not served by the backend. Open it directly from the `frontend/` folder.
- **Backend** exposes API endpoints (mainly `/api/echo`) and loads config from `echo.config.json`.
- **LLM Router** is ready to connect to OpenAI, Claude, Ollama, etc. (currently stubbed)
- **MCP Client** is stubbed for future modular tool invocation.

---

## Features
- Modern, dark-mode chat UI (Claude-style)
- Local-first, privacy-focused architecture
- Modular backend ready for LLM and MCP integration
- Dockerized for easy setup and development
- Live code reload in Docker via volume mount

---

## Folder Structure
```
echo/
├── backend/
│   ├── main.py            # FastAPI server with /api/echo endpoint
│   ├── llm_router.py      # LLM router (uses system prompt)
│   └── mcp_client.py      # (stub for now)
├── prompts/
│   └── base_prompt.yaml
├── frontend/
│   └── index.html         # Tailwind-based UI (static)
├── echo.config.json       # API keys, MCP endpoints
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Configuration

Edit `echo.config.json` to set your API keys and endpoints:
```json
{
  "openai_api_key": "sk-PLACEHOLDER",
  "claude_api_key": "claude-PLACEHOLDER",
  "ollama_endpoint": "http://localhost:11434",
  "mcp_server_url": "http://localhost:8001"
}
```
- This file is required for backend operation. Do **not** commit real keys to version control.

---

## Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/coltonbatts/Echo.git
cd Echo
```

### 2. Set up configuration
- Copy `echo.config.example.json` to `echo.config.json` and add your API keys or endpoints as needed.
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
   - Open `frontend/index.html` directly in your browser.

### 4. Docker (Recommended for full isolation)
1. **Build and run**
   ```bash
   docker compose up --build
   ```
   - Backend: [http://localhost:8000](http://localhost:8000)
   - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
2. **Frontend:** Open `frontend/index.html` (not served by backend)
3. **Live reload:** Code changes are reflected automatically in the container if you use volume mounts (default in `docker-compose.yml`).
   - To force reload, restart the container: `docker compose restart`

1. **Build and run**
   ```bash
   docker compose up --build
   ```
   - Backend: [http://localhost:8000](http://localhost:8000)
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

---

## Roadmap
- Real LLM routing (OpenAI, Claude, Ollama, etc)
- Live MCP tool discovery and invocation
- Desktop app via Tauri
- Persistent chat history

---

> Echo is a personal creative-tech companion. Not for corporate use.
