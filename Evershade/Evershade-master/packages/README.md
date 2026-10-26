# Evershade — Core Platform

This directory contains the shared platform foundation for all Evershade services.

## Packages

### evershade-core
Shared modules for all Python services:
- **config.py** — Pydantic-based configuration with validation
- **errors.py** — Standard error envelope, middleware, correlation IDs
- **health.py** — Health check endpoints (/health, /ready, /metrics)
- **auth.py** — JWT-based service-to-service authentication
- **registry.py** — Service discovery and health aggregation
- **telemetry.py** — OpenTelemetry instrumentation (in services/shared/)

Install: `pip install -e packages/evershade-core[dev]`

### evershade-events
Event contracts and pub/sub event bus:
- Typed event classes (AgentCreated, MissionStarted, etc.)
- EventBus with in-memory and Redis backends
- HTTP event publisher

Install: `pip install -e packages/evershade-events[dev]`

### evershade-db
Database utilities and conventions:
- SQLite WAL mode setup
- Async connection manager
- Transaction support

Install: `pip install -e packages/evershade-db[dev]`

## Running Tests

```bash
# All packages
cd packages/evershade-core && pytest tests/ -v
cd packages/evershade-events && pytest tests/ -v
cd packages/evershade-db && pytest tests/ -v

# Or from root
pytest packages/ -v
```

## Development

```bash
# Start all services in dev mode
./scripts/dev.sh

# Run linters
./scripts/lint.sh
```

## Directory Structure

```
packages/
  evershade-core/    # Shared platform modules
  evershade-events/  # Event contracts
  evershade-db/      # Database utilities
integrations/        # Upstream project adapters
infrastructure/
  docker/            # Docker Compose files
  monitoring/        # Prometheus, Grafana
  proxy/             # Caddy reverse proxy
scripts/             # Dev tooling
services/            # Individual services
apps/                # Frontend applications
tests/               # Integration and security tests
```
