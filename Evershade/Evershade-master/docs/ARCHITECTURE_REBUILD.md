# Evershade — Architecture (Greenfield Rebuild)

**Version:** 2.0.0 (Greenfield)
**Date:** 2026-10-26
**Context:** All 10 service directories are empty. This document defines the target architecture for the rebuild, incorporating external project integration decisions from `EXISTING_PROJECTS.md`.

---

## 1. Platform Overview

Evershade is a self-hosted AI agent platform composed of 10 specialized microservices. Each service has a single responsibility, communicates via HTTP APIs, and can run independently while contributing to the cohesive platform.

### Design Principles

1. **Modular services** – Each service has a clear boundary and public interface.
2. **SQLite-first** – Use SQLite where it satisfies requirements; introduce other databases only when necessary.
3. **No heavy infrastructure** – Avoid Kubernetes, Kafka, Elasticsearch, or distributed databases unless concrete need is demonstrated.
4. **Self-hosted practical** – Must run on ordinary developer hardware without excessive resource consumption.
5. **Security by default** – Least privilege, network isolation, and container hardening are the default.
6. **Integrate, don't recreate** – Use existing open-source projects as the foundation where practical.

---

## 2. Service Catalog

### Core Services (Required)

| Service | Role | Port | Language | Persistence |
|---------|------|------|----------|-------------|
| **Greenie** | Central API, orchestration, chat, dashboard | 8080 | Python/FastAPI | SQLite |
| **Slinker** | Code execution engine, Junie CLI runner | 8000 | Python/FastAPI | SQLite |
| **Trapper** | Web scraping, crawling, browser automation | 3000 | TypeScript/Fastify | Redis (queues) |
| **Gobber** | Persistent storage, knowledge graph, semantic memory | 8085 | Python/FastAPI | SQLite |

### Supporting Services (Optional)

| Service | Role | Port | Language | Persistence |
|---------|------|------|----------|-------------|
| **Sneaker** | Metrics, logs, traces, observability | 8086 | Python/FastAPI | SQLite |
| **Hider** | Encrypted secrets and configuration management | 8087 | Python/FastAPI | SQLite (encrypted) |
| **Poltergeist** | Notifications and async delivery | 8088 | Python/FastAPI | SQLite |
| **Shrewd** | LLM provider abstraction and model routing | 8089 | Python/FastAPI | In-memory |

### Frontend & Tools

| Service | Role | Port/Stack |
|---------|------|------------|
| **Slammer** | React-based standalone dashboard | 5173, React/TypeScript/Tailwind |
| **Speedy** | Command-line interface (`evershade`) | Python/Click/Rich |

### External Integrations

| Integration | Role | Disposition | Service Mapping |
|-------------|------|-------------|-----------------|
| **OpenTelemetry Python** | Standard telemetry SDK | ADOPT | All Python services |
| **Opik** | LLM observability | ADOPT (OPTIONAL) | Sneaker, Shrewd |
| **Prometheus** | Metrics collection | ADOPT (EXISTING) | Monitoring stack |
| **Grafana** | Visualization | ADOPT (EXISTING) | Monitoring stack |
| **cAdvisor** | Container metrics | ADOPT (EXISTING) | Monitoring stack |
| **node-exporter** | Host metrics | ADOPT (EXISTING) | Monitoring stack |
| **Browser Use** | LLM browser automation | DEFER | Trapper (optional backend) |
| **Playwright MCP** | MCP browser automation | DEFER | Trapper (optional backend) |
| **Loki** | Log aggregation | DEFER | Sneaker (future) |
| **Tempo** | Trace backend | DEFER | Sneaker (future) |

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Access                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Browser    │  │   Windows    │  │   CLI (Speedy)       │  │
│  │  (Slammer)   │  │   PC         │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         │  HTTPS/HTTP     │  SSH/HTTPS           │  HTTP        │
│         ▼                 ▼                      ▼              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Greenie (8080) – Gateway                     │  │
│  │  ┌────────────┬────────────┬────────────┬──────────────┐ │  │
│  │  │  Web UI    │  Chat API  │  Workflow  │  Management  │ │  │
│  │  │  (static)  │  + SSE     │  Engine    │  + RBAC      │ │  │
│  │  └────────────┴────────────┴────────────┴──────────────┘ │  │
│  │                    │                  │                   │  │
│  │              SQLite DB          Feature Stores           │  │
│  └────────────────────┼────────────────┼────────────────────┘  │
│                       │                  │                     │
└───────────────────────┼──────────────────┼─────────────────────┘
                        │                  │
          ┌─────────────┼──────────────────┼─────────────┐
          │             │                  │             │
          ▼             ▼                  ▼             ▼
   ┌──────────────┐ ┌──────────┐   ┌──────────┐  ┌──────────┐
   │  Slinker     │ │ Trapper  │   │ Gobber   │  │ Shrewd   │
   │  (8000)      │ │ (3000)   │   │ (8085)   │  │ (8089)   │
   │              │ │          │   │          │  │          │
   │ Git worktree │ │ Playwright│  │ SQLite   │  │ Provider │
   │ Junie CLI    │ │ + Adapter│  │ KG +     │  │ routing  │
   │ SQLite       │ │ Redis Q   │  │ Obsidian │  │ + Opik   │
   └──────────────┘ └──────────┘   └──────────┘  └──────────┘
          │             │                  │             │
          ▼             ▼                  ▼             ▼
   ┌──────────────┐ ┌──────────┐   ┌──────────┐  ┌──────────┐
   │  Hider       │ │ Sneaker  │   │ Polter-  │  │  (External│
   │  (8087)      │ │ (8086)   │   │ geist    │  │   LLM     │
   │              │ │          │   │ (8088)   │  │  APIs)    │
   │ Encrypted    │ │ OTLP +   │   │ Slack,   │  │           │
   │ secrets      │ │ OpenTelemetry │ Discord, │  │  OpenAI,  │
   │ Config       │ │ Prometheus│   │ Email    │  │  Anthropic│
   └──────────────┘ └──────────┘   └──────────┘  │  Google   │
                                                  └──────────┘
```

---

## 4. Service Responsibilities

### 4.1. Greenie — Central Hub & Dashboard

**Responsibility:** Orchestration, agent management, chat sessions, workflow execution, user interface.

**Owns:**
- Agent definitions and configuration
- Chat sessions and conversation history
- Workflow definitions and execution state
- User accounts and RBAC policies
- Approval workflows
- Mission control (missions, milestones, features, validation)
- Agent harness (specs, droids, skills, hooks, environments)
- Analytics events (delegates storage to Gobber)
- Feature flags (delegates storage to Gobber)
- Webhook definitions (delegates storage to Gobber)

**Dependencies:**
- Slinker (code execution tasks)
- Trapper (web scraping tasks)
- Gobber (persistent feature stores, knowledge graph)
- Shrewd (LLM requests)
- Poltergeist (notifications) — optional
- Sneaker (observability) — optional
- Hider (secrets) — optional

**Public Interface:**
- REST API: `/api/*`
- WebSocket: `/ws/feed`
- SSE: Various streaming endpoints
- Static files: Web dashboard

**Rebuild Notes:** Greenie is the largest service (~157 Python files in the previous version). The rebuild should start with the core API, health endpoints, and agent management, then add missions, agent harness, and marketplace.

---

### 4.2. Slinker — Code Execution Engine

**Responsibility:** Execute AI agent tasks in isolated Git worktrees using the Junie CLI.

**Owns:**
- Task execution state
- Worker registry
- Project registrations
- Session logs
- Worktree management

**Dependencies:**
- Junie CLI (external binary)
- Ollama (optional, for prompt refinement)

**Public Interface:**
- REST API: `/api/v1/*`
- OpenAI-compatible: `/v1/chat/completions`, `/v1/models`
- Health: `/health`, `/ready`

**Rebuild Notes:** Slinker is a focused service (~20 Python files). Rebuild with worktree isolation, worker management, and Junie CLI integration.

---

### 4.3. Trapper — Web Scraping & Crawling

**Responsibility:** Scrape, crawl, search, and interact with websites using Playwright.

**Owns:**
- Scraping jobs and results
- Crawl queues (Redis/BullMQ)
- Browser instances
- Browser backend adapter pattern

**Dependencies:**
- Redis (job queues)
- Playwright/Chromium (browser automation)

**Public Interface:**
- REST API: `/api/*` (scrape, crawl, map, search, extract, interact, agent)
- Health: `/health`

**Rebuild Notes:** Trapper is TypeScript/Fastify (~39 files). The rebuild must include the browser backend adapter pattern from day one, with Playwright as the default backend. This enables future integration of Browser Use or Playwright MCP as optional backends.

**Browser Backend Adapter:**
```
BrowserBackend (interface)
  ├── PlaywrightBackend (default)
  └── [Future: BrowserUseBackend, PlaywrightMcpBackend]
```

Selected via `TRAPPER_BROWSER_BACKEND` environment variable.

---

### 4.4. Gobber — Persistent Storage & Knowledge Graph

**Responsibility:** Centralized persistent storage for ecosystem feature stores and semantic memory.

**Owns:**
- Webhook definitions and delivery history
- Analytics events
- RBAC roles and user assignments
- Response cache
- Feature flags
- Knowledge graph (notes, embeddings, links)
- Obsidian vault index

**Dependencies:**
- Shrewd (optional, for embedding generation)

**Public Interface:**
- REST API: `/api/*` (webhooks, analytics, flags, cache, roles, vault)
- Embedding API: `/api/embeddings/*` (generate, search, batch, stats)
- Health: `/health`

**Rebuild Notes:** Gobber is a focused service (~11 Python files). Rebuild with SQLite, embedding pipeline via Shrewd, and Obsidian vault indexing.

---

### 4.5. Sneaker — Observability

**Responsibility:** Collect and query metrics, distributed traces, and structured logs.

**Owns:**
- Metric time series
- Trace spans (OTLP)
- Log entries (OTLP)
- Alert rules
- OTLP export endpoints

**Dependencies:** None (leaf service)

**Public Interface:**
- REST API: `/api/*` (metrics, traces, logs, alerts)
- OTLP endpoints: `POST /v1/traces`, `POST /v1/metrics`, `POST /v1/logs`
- OTLP export: `GET /api/otlp/export/traces`, `/metrics`, `/logs`
- OTLP stats: `GET /api/otlp/stats`
- Health: `/health`

**Rebuild Notes:** Sneaker is the observability hub (~8 Python files). Must support both OTLP ingest and Prometheus `/metrics` export. OpenTelemetry SDK integration is required for all Python services to send traces to Sneaker.

---

### 4.6. Hider — Secrets & Configuration

**Responsibility:** Encrypted storage and retrieval of secrets and centralized configuration.

**Owns:**
- Encrypted secrets (AES-256)
- Versioned configuration entries
- Secret access audit log

**Dependencies:** None (leaf service)

**Public Interface:**
- REST API: `/api/*` (secrets, configs)
- Health: `/health`

**Rebuild Notes:** Hider is a focused service (~7 Python files). Rebuild with AES-256 encryption, SQLite storage, and audit logging.

---

### 4.7. Poltergeist — Notifications

**Responsibility:** Send notifications through multiple channels with templating and async delivery.

**Owns:**
- Notification templates
- Delivery history
- Channel configurations

**Dependencies:**
- External services (Slack, Discord, email SMTP, Telegram API)

**Public Interface:**
- REST API: `/api/*` (notifications, templates)
- Health: `/health`

**Rebuild Notes:** Poltergeist is a focused service (~7 Python files). Rebuild with Slack, Discord, email, and Telegram channels. Async delivery with retries.

---

### 4.8. Shrewd — LLM Abstraction

**Responsibility:** Unified interface for multiple LLM providers with model routing.

**Owns:**
- Model registry
- Provider configurations
- Usage tracking and cost estimation
- Routing rules
- Privacy classification

**Dependencies:**
- External LLM APIs (OpenAI, Anthropic, Google, Ollama)
- Opik (optional, for LLM tracing)

**Public Interface:**
- REST API: `/api/*` (chat, models, providers)
- Health: `/health`

**Rebuild Notes:** Shrewd is a focused service (~7 Python files). Rebuild with provider abstraction for OpenAI, Anthropic, Google, and Ollama. Add Opik integration when `OPIK_ENDPOINT` is configured.

---

### 4.9. Slammer — Web Dashboard

**Responsibility:** React-based standalone dashboard for platform management.

**Owns:**
- Frontend application code
- UI state management

**Dependencies:**
- Greenie (all API calls proxied through Greenie)

**Public Interface:**
- Static web application served on port 5173

**Rebuild Notes:** Slammer is a React/Vite/Tailwind app (~14 files). Rebuild with logs, metrics, missions, plugins, terminal, workflow builder, and workstations views. Include Grafana link when monitoring is enabled.

---

### 4.10. Speedy — CLI

**Responsibility:** Command-line interface for platform management.

**Owns:**
- CLI commands and configuration
- Remote connection profiles

**Dependencies:**
- Greenie API (primary)
- Docker Compose (for install/start/stop)

**Public Interface:**
- `evershade` command with subcommands

**Rebuild Notes:** Speedy is a small Python/Click/Rich app (~2 files). Rebuild with service status, agents, tasks, configuration, capabilities, and monitoring status commands.

---

## 5. Communication Standards

### Synchronous Communication

All service-to-service communication uses HTTP/JSON REST APIs.

**Standard headers:**
- `Authorization: Bearer <service-api-key>` – Service authentication
- `X-Request-ID: <uuid>` – Unique request identifier
- `X-Correlation-ID: <uuid>` – Correlates requests across services
- `X-Service-Name: <service>` – Source service identification
- `Content-Type: application/json` – Request format
- `Accept: application/json` – Response format

**Standard response envelope:**
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "requestId": "uuid",
  "timestamp": "2026-10-26T10:00:00Z"
}
```

**Standard error response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Trapper service is not reachable",
    "details": "Connection timeout after 5s"
  },
  "requestId": "uuid",
  "timestamp": "2026-10-26T10:00:00Z"
}
```

**Error codes:**
| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `SERVICE_UNAVAILABLE` | 503 | Downstream service unavailable |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Timeouts and Retries

| Operation | Timeout | Retries | Backoff |
|-----------|---------|---------|---------|
| Health check | 5s | 0 | – |
| Synchronous API call | 30s | 1 | 1s fixed |
| Long-running task (Slinker) | 1800s | 0 | – |
| Web scraping (Trapper) | 60s | 1 | 2s fixed |
| LLM request (Shrewd) | 120s | 1 | 5s fixed |

### Asynchronous Communication

Used only where genuinely required:
- **Trapper crawl jobs:** Redis/BullMQ for background crawl processing
- **Poltergeist notifications:** Async delivery queue for notification channels
- **Slinker workers:** Concurrent worker pool with semaphore

---

## 6. Data Ownership

| Data Type | Owner | Consumers | Storage |
|-----------|-------|-----------|---------|
| Agent definitions | Greenie | Slinker, Shrewd | Greenie SQLite |
| Chat sessions | Greenie | – | Greenie SQLite |
| Workflow definitions | Greenie | All services | Greenie SQLite |
| Task execution state | Slinker | Greenie | Slinker SQLite |
| Web scraping results | Trapper | Greenie, Gobber | Return value (ephemeral) |
| Feature stores (webhooks, RBAC, etc.) | Gobber | Greenie | Gobber SQLite |
| Knowledge graph | Gobber | Greenie, Slinker | Gobber SQLite |
| Metrics and traces | Sneaker | Greenie (dashboard) | Sneaker SQLite |
| Secrets | Hider | All services (on demand) | Hider SQLite (encrypted) |
| Notification history | Poltergeist | Greenie (dashboard) | Poltergeist SQLite |
| Model registry | Shrewd | Greenie, Slinker | Shrewd (in-memory) |

**Rules:**
1. Services access other services' data only through public APIs.
2. No direct database access across service boundaries.
3. Schema changes are the responsibility of the owning service.
4. No duplicated sources of truth.

---

## 7. Telemetry Architecture

### OpenTelemetry Integration

All Python services adopt OpenTelemetry SDK for distributed tracing:

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Greenie  │    │ Slinker  │    │ Shrewd   │
│  OTel    │    │  OTel    │    │  OTel    │
└────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │
     └───────────────┼───────────────┘
                     │ OTLP/gRPC
                     ▼
              ┌──────────────┐
              │   Sneaker    │
              │  OTLP Ingest │
              └──────┬───────┘
                     │
              ┌──────┴───────┐
              │ Prometheus   │
              │ /metrics     │
              └──────────────┘
```

**Shared telemetry module:** `services/shared/evershade_telemetry.py`

**Configuration:** `SNEAKER_OTLP_ENDPOINT` environment variable on all Python services.

### Opik Integration (Optional)

When Opik is enabled via `--profile opik`:

```
Shrewd → Opik (port 9000)
         ├── LLM call traces
         ├── Token usage
         └── Prompt optimization
```

**Configuration:** `OPIK_ENDPOINT` environment variable on Shrewd.

---

## 8. Deployment Topology

### Default (Desktop) Mode

```
┌──────────────────────────────────────────────┐
│                 Host Machine                 │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │         Docker Network (internal)      │  │
│  │                                        │  │
│  │  Greenie ←── Slinker                   │  │
│  │    │        Trapper                     │  │
│  │    ├── Gobber                          │  │
│  │    ├── Sneaker                         │  │
│  │    ├── Hider                           │  │
│  │    ├── Poltergeist                     │  │
│  │    └── Shrewd                          │  │
│  │                                        │  │
│  │  Redis (internal)                      │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  Host: localhost:8080 → Greenie only         │
│  All other services: internal only           │
└──────────────────────────────────────────────┘
```

### Server Mode

```
┌──────────────────────────────────────────────┐
│              Ubuntu Server / VM              │
│                                              │
│  ┌────────────┐    ┌──────────────────────┐  │
│  │  Caddy     │    │  Docker Network      │  │
│  │  (TLS)     │───→│  (internal)          │  │
│  │  :443      │    │                      │  │
│  └────────────┘    │  Greenie ←─ Slinker  │  │
│                    │       └─ Trapper      │  │
│                    │       └─ Gobber       │  │
│                    │       └─ (others)     │  │
│                    └──────────────────────┘  │
│                                              │
│  Host: :443 → Caddy → Greenie               │
│  All other services: internal only           │
└──────────────────────────────────────────────┘
         ▲
         │ HTTPS
         │
   ┌─────────┐
   │ Windows │
   │  PC     │
   └─────────┘
```

### Docker Compose Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `minimal` | Greenie, Slinker, Trapper, Gobber, Redis | Core functionality only |
| `standard` | All services except Slammer | Full backend |
| `full` | Everything including Slammer | Complete platform |
| `monitoring` | Prometheus, Grafana, cAdvisor, node-exporter | Observability |
| `opik` | Opik | LLM observability |
| `ollama` | Ollama | Local LLM inference |
| `proxy` | Caddy | TLS reverse proxy |
| `dev` | All ports exposed | Development mode |

---

## 9. Service Health Contract

Every service exposes:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Liveness check – returns 200 if process is running |
| `/ready` | GET | Readiness check – returns 200 if fully initialized |
| `/api/status` | GET | Detailed status – version, capabilities, dependency health |
| `/api/capabilities` | GET | Feature list and integration status |

**Health response:**
```json
{
  "status": "ok",
  "service": "Greenie",
  "version": "2.0.0"
}
```

---

## 10. Optional Services Policy

Services are classified as required or optional:

- **Required:** Greenie, Slinker, Trapper, Gobber
- **Optional:** Sneaker, Hider, Poltergeist, Shrewd, Slammer

When an optional service is unavailable:
1. The platform continues to operate.
2. Greenie logs a warning and marks the service as unavailable.
3. Features depending on the unavailable service degrade gracefully.
4. No cascade failure — a missing optional service never brings down the platform.

---

## 11. Security Architecture

### Container Hardening

All containers apply:
- `read_only: true` — Read-only root filesystem
- `no-new-privileges: true` — Prevent privilege escalation
- `cap_drop: ALL` — Drop all Linux capabilities
- Resource limits (CPU and memory)
- Health checks with restart policies

### Network Isolation

- Internal Docker network for service-to-service communication
- Only Greenie (port 8080) and Slammer (port 5173) exposed to host
- All other services accessible only via internal network
- Optional Caddy proxy for TLS termination

### Secrets Management

- Hider service provides encrypted secret storage (AES-256)
- API keys for inter-service authentication
- Redis password protection
- Environment variables for configuration, never hardcoded

---

## 12. Naming Convention

All services follow the Luigi's Mansion ghost naming theme:

| Service | Plain-Language Role |
|---------|-------------------|
| Greenie | Central hub and dashboard |
| Slinker | Code execution engine |
| Trapper | Web scraping and crawling |
| Gobber | Persistent storage and knowledge graph |
| Sneaker | Observability and monitoring |
| Hider | Secrets and configuration management |
| Poltergeist | Notification delivery |
| Shrewd | LLM provider abstraction |
| Slammer | Web dashboard |
| Speedy | Command-line interface |

---

## 13. Data Flows

### Chat Flow
```
User → Slammer → Greenie → Shrewd → External LLM API
                          ↕ Gobber (knowledge graph lookup)
                          → Sneaker (tracing)
```

### Code Execution Flow
```
User → Slammer → Greenie → Slinker → Junie CLI → Git Worktree
                          ↕ Sneaker (tracing)
```

### Web Scraping Flow
```
User → Slammer → Greenie → Trapper → Playwright → Target Website
                                    ↕ Redis (queue)
```

### Notification Flow
```
Greenie → Poltergeist → Slack/Discord/Email/Telegram
```

### Observability Flow
```
All Services → OpenTelemetry → Sneaker (OTLP)
All Services → /metrics → Prometheus → Grafana
Shrewd → Opik (optional, LLM traces)
```
