# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Echo is a modular AI infrastructure platform that orchestrates different LLMs and MCP (Model Context Protocol) tools through a unified interface. The platform consists of a FastAPI backend, React frontend with terminal-style UI, and Docker-based deployment.

## Development Commands

### Backend Development
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install MCP server dependencies
pip install -r mcp_servers/requirements.txt

# Run backend in development mode
uvicorn backend.main:app --reload

# Start all MCP servers
python scripts/start_mcp_servers.py

# Check MCP server health
python scripts/start_mcp_servers.py --check-health

# Stop MCP servers
python scripts/start_mcp_servers.py --stop

# Run tests
pytest
pytest tests/test_enhanced_mcp.py  # Enhanced MCP tests
```

### Frontend Development
```bash
# React app development
cd echo-blackgreen
npm install
npm start  # Runs on localhost:3000

# Standard React commands
npm test
npm run build
```

### Docker Development (Recommended)
```bash
# Start all services
docker compose up -d --build

# Restart services after changes
docker compose restart

# View logs
docker compose logs -f
```

### Testing
```bash
# Run Python tests
pytest

# Run React tests
cd echo-blackgreen && npm test
```

## Architecture

### Core Components
- **Backend (`backend/`)**: FastAPI server with LLM routing and MCP client integration
- **Frontend (`echo-blackgreen/`)**: React terminal-style chat interface with Tailwind CSS
- **MCP Integration**: Dynamic tool discovery and execution via HTTP endpoints
- **Docker**: Multi-container setup with Nginx proxy

### Key Files
- `backend/main.py`: Main FastAPI application with `/api/echo` and `/api/tools` endpoints
- `backend/mcp_client.py`: MCP server communication and tool management
- `echo-blackgreen/src/ChatBox.jsx`: Terminal-style React chat component
- `echo-blackgreen/src/setupProxy.js`: Proxies `/api/*` requests to backend during development
- `prompts/base_prompt.yaml`: System prompt configuration for LLM interactions

### Data Flow
1. React app sends chat messages to `/api/echo` via proxy
2. Backend analyzes message for tool relevance using keyword matching
3. If relevant, executes MCP tool and includes result in LLM context
4. Response includes LLM output, tools used, and processing metadata

## Environment Configuration

Create `.env` file in project root with:
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
MCP_SERVER_URLS=http://localhost:8001
MCP_DISCOVERY_TIMEOUT=3
MCP_EXECUTION_TIMEOUT=10
```

## Enhanced MCP Tool Integration

### Available MCP Servers
1. **Calculator Server** (`sample_mcp_server.py`) - Port 8001
   - Basic mathematical calculations
2. **File Operations Server** (`mcp_servers/file_server.py`) - Port 8002  
   - File reading, writing, directory listing, search
3. **Web Search Server** (`mcp_servers/web_server.py`) - Port 8003
   - Web search, URL fetching, link extraction
4. **System Utilities Server** (`mcp_servers/system_server.py`) - Port 8004
   - System info, process management, performance metrics

### Intelligent Tool Selection
- **Entity Extraction**: Automatically extracts file paths, URLs, math expressions, etc.
- **Intent Detection**: Identifies user intent (file_read, web_search, calculation, etc.)
- **Semantic Similarity**: Calculates relevance between user message and tool capabilities
- **Usage Learning**: Improves selection based on usage patterns and context

### Tool Discovery & Execution
- **Parallel Discovery**: All servers queried simultaneously with health monitoring
- **Caching**: Tools cached for 5 minutes (configurable via `MCP_CACHE_TTL`)
- **Retry Logic**: Automatic retry with exponential backoff for failed operations
- **Batch Execution**: Multiple tools can be executed in parallel

### Configuration
- Set `USE_INTELLIGENT_SELECTION=true` for smart tool selection
- Set `USE_INTELLIGENT_SELECTION=false` for legacy keyword matching
- Configure timeouts, retry limits, and parallel execution limits via environment variables

## Frontend Architecture

### React Components
- `BlackGreenMockup.jsx`: Main layout with terminal aesthetic
- `ChatBox.jsx`: Core chat functionality with typewriter effects
- `ModelsList.jsx`, `ToolsPanel.jsx`: UI panels for displaying capabilities

### Styling
- Uses Tailwind CSS via `tailwind.config.js`
- Terminal theme: green text on black background
- Monospace fonts throughout
- CSS-in-JS for component-specific animations

## Testing Strategy

### Backend Tests (`tests/`)
- `test_api_echo.py`: Tests echo endpoint with tool execution and error scenarios
- `test_api_tools.py`: Tests tool discovery endpoints
- Uses pytest with FastAPI TestClient and monkeypatch for mocking

### Frontend Tests
- Standard Create React App testing setup
- Jest and React Testing Library

## Development Workflow

1. Start Docker services: `docker compose up -d --build`
2. Run React dev server: `cd echo-blackgreen && npm start`
3. Backend available at `localhost:8000`, frontend at `localhost:3000`
4. React app proxies API calls to backend automatically
5. Changes auto-reload in both frontend and backend containers

## Port Configuration
- Backend: `8000` (FastAPI)
- Frontend (Nginx): `80`
- React Dev: `3000`
- MCP Servers: `8001+` (configurable)

## Common Development Patterns

### Adding New LLM Providers
Extend `llm_router()` function in `backend/main.py` with provider-specific logic.

### Adding New MCP Endpoints
MCP servers should implement the standard endpoints. Update `MCP_SERVER_URLS` environment variable.

### Modifying Chat Interface
Main chat logic lives in `ChatBox.jsx`. Terminal styling uses CSS animations for typewriter and cursor effects.