# Greenie

Evershade agent orchestration and mission control service.

## Features

- Agent lifecycle management (create, update, delete agents)
- Mission planning and execution
- Task delegation to Slinker (code execution)
- Chat sessions with agents
- Service registry and discovery
- SSE/WebSocket streaming for real-time updates

## API Endpoints

- `GET /health` — Health check
- `GET /metrics` — Prometheus metrics
- `GET /api/capabilities` — Service capabilities
- `POST /api/agents/` — Create agent
- `GET /api/agents/` — List agents
- `GET /api/agents/{id}` — Get agent
- `DELETE /api/agents/{id}` — Delete agent
- `POST /api/missions/` — Create mission
- `GET /api/missions/` — List missions
- `POST /api/tasks/` — Create task
- `GET /api/tasks/` — List tasks

## Environment Variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | API key for authentication |
| `PORT` | Port to listen on (default: 8080) |
| `GREENIE_DB_PATH` | SQLite database path |
| `SLINKER_URL` | Slinker service URL |
| `TRAPPER_URL` | Trapper service URL |
| `GOBBER_URL` | Gobber service URL |
| `SHREWD_URL` | Shrewd service URL |
