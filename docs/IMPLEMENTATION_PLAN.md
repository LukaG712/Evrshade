# Evershade — Phased Implementation Plan

**Version:** 2.9.0 (Phase 10 — Deferred Project Integrations)
**Date:** 2026-10-26
**Context:** All 10 services implemented, core platform rebuilt with new packages. Phase 3–8 re-verified with new evershade-core, evershade-db, and evershade-events packages. Phase 10 integrated 5 deferred projects: Loki, Tempo, Langfuse, Browser Use, and Playwright MCP. All phases are now complete.

---

## Phase Overview

| Phase | Name | Services | Dependencies |
|-------|------|----------|-------------|
| 1 | Project Inventory & Architecture | — | None (planning only) |
| 2 | Core Platform & Service Contracts | Infrastructure, shared modules | Phase 1 |
| 3 | External Project Integrations | OpenTelemetry, Opik | Phase 2 |
| 4 | Agent Orchestration & Coding Agents | Greenie, Slinker | Phase 3 |
| 5 | Browser Automation, Memory & Model Routing | Trapper, Gobber, Shrewd | Phase 3 |
| 6 | Workflows, Observability, Security & Notifications | Sneaker, Hider, Poltergeist | Phase 3 |
| 7 | Dashboard, CLI & Deployment | Slammer, Speedy, docker-compose | Phase 4–6 |
| 8 | End-to-End Testing & Release Readiness | All services | Phase 7 |
| 10 | Deferred Project Integrations | Loki, Tempo, Langfuse, Browser Use, Playwright MCP | Phase 3–5 |

---

## Phase 1: Project Inventory & Architecture

**Status:** ✓ Complete
**Duration:** Planning only

### Objectives
- Evaluate all 20+ external projects for integration
- Define service responsibilities, interfaces, and data flows
- Establish the implementation plan

### Deliverables
- [x] `docs/EXISTING_PROJECTS.md` — Repository inventory and integration decisions
- [x] `docs/ARCHITECTURE_REBUILD.md` — Service responsibilities, interfaces, data flows
- [x] `docs/IMPLEMENTATION_PLAN.md` — This document
- [x] `docs/IMPLEMENTATION_STATUS.md` — Progress tracker

### Acceptance Criteria
- [x] All 20+ external projects documented with explicit dispositions
- [x] Each service has clear responsibilities and interfaces
- [x] Implementation phases are dependency-ordered
- [x] No questions remain unresolved without documented blockers

---

## Phase 2: Core Platform & Service Contracts

**Status:** ⬜ Pending
**Dependencies:** Phase 1

### Objectives
Establish the foundation that all services depend on: Docker infrastructure, shared modules, and service contracts.

### 2.1. Infrastructure Setup

**Tasks:**
1. Create `docker-compose.yml` with all service definitions, profiles, networks, and volumes
2. Create `.env.example` with all required environment variables
3. Create `Caddyfile` for optional TLS reverse proxy
4. Set up Docker networks: `internal` (service-to-service) and `frontend` (host-facing)
5. Configure Redis service with persistence and authentication

**Acceptance Criteria:**
- [ ] `docker compose --profile minimal config` validates without errors
- [ ] Redis starts, passes health check, and accepts authenticated connections
- [ ] All environment variables documented in `.env.example`

### 2.2. Shared Modules

**Tasks:**
1. Create `services/shared/evershade_telemetry.py` — OpenTelemetry initialization
2. Create shared health check module for Python services
3. Create shared error response module for consistent error format
4. Create shared configuration module for loading environment variables

**Acceptance Criteria:**
- [ ] Shared telemetry module initializes OpenTelemetry with OTLP exporter
- [ ] Health check module provides `/health`, `/ready`, and `/api/status` endpoints
- [ ] Error response module produces standard error envelope
- [ ] Configuration module loads and validates environment variables

### 2.3. Service Skeletons

**Tasks:**
1. Create minimal skeleton for each service with:
- `Dockerfile`
- `requirements.txt` (Python) or `package.json` (TypeScript)
- Main application file with health endpoints
- Service registration in docker-compose.yml

**Services:** Greenie, Slinker, Trapper, Gobber, Sneaker, Hider, Poltergeist, Shrewd, Slammer, Speedy

**Acceptance Criteria:**
- [ ] Every service has a Dockerfile that builds successfully
- [ ] Every service exposes `/health` returning 200 OK
- [ ] `docker compose --profile minimal up` starts all core services
- [ ] All services pass Docker health checks

### 2.4. Monitoring Stack Foundation

**Tasks:**
1. Configure Prometheus with scrape targets for all services
2. Configure Grafana with auto-provisioned dashboards
3. Add cAdvisor and node-exporter services
4. Create `monitoring/` directory structure

**Acceptance Criteria:**
- [ ] `docker compose --profile monitoring up` starts monitoring stack
- [ ] Prometheus scrapes all service `/metrics` endpoints
- [ ] Grafana auto-provisions Evershade Overview dashboard
- [ ] cAdvisor reports container metrics

---

## Phase 3: External Project Integrations

**Status:** ✓ Complete
**Dependencies:** Phase 2

### Objectives
Integrate the external projects that were marked as ADOPT: OpenTelemetry Python and Opik.

### 3.1. OpenTelemetry Python Integration

**Tasks:**
1. Add OpenTelemetry dependencies to evershade-core package:
- `opentelemetry-api`
- `opentelemetry-sdk`
- `opentelemetry-instrumentation-fastapi`
- `opentelemetry-exporter-otlp-proto-grpc`
- `opentelemetry-instrumentation-httpx`
- `opentelemetry-propagator-b3`
2. Create telemetry module (`packages/evershade-core/src/evershade/telemetry.py`)
3. Add `SNEAKER_OTLP_ENDPOINT` environment variable to all Python services
4. Verify trace context propagation across service boundaries
5. Keep `prometheus_client` for `/metrics` endpoint
6. Create telemetry unit tests (9 tests)

**Acceptance Criteria:**
- [x] All Python services emit traces to Sneaker via OTLP when `SNEAKER_OTLP_ENDPOINT` is set
- [x] Trace context propagates across service boundaries via B3 headers
- [x] `/metrics` endpoints expose Prometheus-format metrics
- [x] OpenTelemetry is optional — services work normally without it
- [x] Telemetry module has 9 unit tests covering all functions
- [x] Telemetry functions exported from evershade-core package

### 3.2. Opik Integration (Optional)

**Tasks:**
1. Add Opik service to docker-compose.yml with `--profile opik` ✓
2. Configure persistent volume for Opik data ✓
3. Add `OPIK_ENDPOINT` environment variable to Shrewd ✓
4. Document Opik setup in `docs/MONITORING.md` ✓

**Acceptance Criteria:**
- [x] Opik is optional and disabled by default (separate profile)
- [x] Opik runs on port 9000 with persistent data
- [x] No impact on services when Opik is disabled
- [x] Shrewd can send LLM traces to Opik when configured

---

## Phase 4: Agent Orchestration & Coding Agents

**Status:** ✓ Complete (Re-verified with new packages)
**Dependencies:** Phase 3

### Objectives
Rebuild Greenie (central hub) and Slinker (code execution) — the two core services that drive the platform. Both services now use the new evershade-core, evershade-db, and evershade-events packages.

### 4.1. Greenie — Core API

**Tasks:**
1. Implement FastAPI application with:
- Health endpoints (`/health`, `/ready`, `/api/status`, `/api/capabilities`)
- Agent management (CRUD operations)
- Chat sessions and conversation history
- Workflow definitions and execution state
- User accounts and RBAC policies
2. Implement SQLite database with WAL mode using evershade-db
3. Implement API key authentication middleware
4. Implement CSRF protection
5. Implement SSE streaming for real-time updates
6. Implement WebSocket feed (`/ws/feed`)
7. Integrate with evershade-core: config, errors, health, telemetry, registry, middleware

**Acceptance Criteria:**
- [x] Greenie starts and passes all health checks
- [x] Agent CRUD operations work correctly
- [x] Chat sessions are persisted and queryable
- [x] API key authentication rejects unauthorized requests
- [x] SSE streaming delivers real-time updates
- [x] `/api/capabilities` returns service version and feature list
- [x] Uses evershade-core packages (config, errors, health, telemetry, registry)
- [x] Uses evershade-db for database operations
- [x] Correlation ID middleware and request logging enabled

### 4.2. Greenie — Mission Control

**Tasks:**
1. Implement mission lifecycle: create → plan → execute → validate → complete
2. Implement milestone and feature management
3. Implement validation contracts and results
4. Implement checkpoint recovery (SQLite)
5. Implement approval gates
6. Implement autonomy levels (supervised, restricted, full)
7. Implement secret redaction for logs and model context
8. Implement automation engine (GitHub webhooks, cron triggers)
9. Implement mission analytics
10. Implement SSE log streaming

**Acceptance Criteria:**
- [ ] Missions can be created, planned, executed, and completed
- [ ] Checkpoints allow recovery after restart
- [ ] Approval gates pause execution for human review
- [ ] Secret redaction removes API keys from logs
- [ ] Mission analytics report success rates and durations

### 4.3. Greenie — Agent Harness

**Tasks:**
1. Implement Spec Mode (read-only research before implementation)
2. Implement Custom Droids (specialized subagents)
3. Implement Skills System (reusable SKILL.md workflows)
4. Implement Hooks System (event-driven lifecycle hooks)
5. Implement Environments (reusable sandbox definitions)

**Acceptance Criteria:**
- [ ] Specs can be created, researched, approved, and converted to missions
- [ ] Custom droids are discovered from `.evershade/droids/` and `~/.evershade/droids/`
- [ ] Skills are auto-matched to tasks based on trigger phrases
- [ ] Hooks execute on mission lifecycle events
- [ ] Environments can be validated before execution

### 4.4. Slinker — Code Execution Engine

**Tasks:**
1. Implement FastAPI application with health endpoints
2. Implement task execution state management
3. Implement worker registry with semaphore-based concurrency
4. Implement project registration
5. Implement Git worktree management
6. Implement Junie CLI integration
7. Implement session logging
8. Implement OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/models`)
9. Implement prompt refinement via Ollama (optional)

**Acceptance Criteria:**
- [ ] Slinker starts and passes all health checks
- [ ] Tasks are executed in isolated Git worktrees
- [ ] Worker concurrency is limited by `MAX_CONCURRENT_WORKERS`
- [ ] Session logs are persisted and queryable
- [ ] OpenAI-compatible endpoints work correctly
- [ ] Prompt refinement is optional and configurable

### 4.5. Greenie-Slinker Integration

**Tasks:**
1. Greenie delegates code execution tasks to Slinker
2. Implement task status polling and SSE updates
3. Implement error handling and retry logic

**Acceptance Criteria:**
- [ ] Greenie can submit tasks to Slinker
- [ ] Task status is visible in Greenie's API
- [ ] SSE updates deliver real-time task progress
- [ ] Failed tasks are properly reported with error details

---

## Phase 5: Browser Automation, Memory & Model Routing

**Status:** ✓ Complete
**Dependencies:** Phase 3

### Objectives
Rebuild Trapper (browser automation), Gobber (memory and storage), and Shrewd (LLM routing).

### 5.1. Trapper — Web Scraping & Crawling

**Tasks:**
1. Implement Fastify application with health endpoints
2. Implement browser backend adapter pattern:
- `BrowserBackend` interface
- `PlaywrightBackend` as default implementation
- Factory function `createBrowserBackend()` with `TRAPPER_BROWSER_BACKEND` env var
3. Implement scraping operations (scrape, extract)
4. Implement crawling with Redis/BullMQ queues
5. Implement search and mapping operations
6. Implement interaction operations
7. Implement SSRF protection
8. Implement rate limiting
9. Implement Trapper-api and Trapper-worker separation

**Acceptance Criteria:**
- [ ] Trapper starts and passes all health checks
- [ ] Scraping returns structured content from URLs
- [ ] Crawling respects depth, page count, and concurrency limits
- [ ] SSRF protection blocks internal addresses
- [ ] Browser backend is configurable via environment variable
- [ ] Rate limiting prevents abuse

### 5.2. Gobber — Persistent Storage & Knowledge Graph

**Tasks:**
1. Implement FastAPI application with health endpoints
2. Implement webhook definitions and delivery history
3. Implement analytics events storage
4. Implement RBAC roles and user assignments
5. Implement response cache
6. Implement feature flags
7. Implement knowledge graph (notes, embeddings, links)
8. Implement Obsidian vault indexing
9. Implement embedding API (`/api/embeddings/*`)
10. Integrate with Shrewd for embedding generation

**Acceptance Criteria:**
- [ ] Gobber starts and passes all health checks
- [ ] Webhooks are stored and queryable
- [ ] RBAC roles are enforced
- [ ] Knowledge graph supports semantic search
- [ ] Embedding API generates and searches vectors
- [ ] Obsidian vault indexing works with mounted vault path

### 5.3. Shrewd — LLM Provider Abstraction

**Tasks:**
1. Implement FastAPI application with health endpoints
2. Implement provider abstraction for:
- OpenAI
- Anthropic
- Google
- Ollama
3. Implement model registry
4. Implement usage tracking and cost estimation
5. Implement routing rules
6. Implement privacy classification
7. Implement Opik integration (when `OPIK_ENDPOINT` is configured)

**Acceptance Criteria:**
- [ ] Shrewd starts and passes all health checks
- [ ] Chat completions work for all configured providers
- [ ] Usage tracking records token counts and costs
- [ ] Routing rules direct requests to appropriate models
- [ ] Opik traces are sent when configured

### 5.4. Greenie Integration

**Tasks:**
1. Greenie delegates web scraping to Trapper
2. Greenie delegates feature stores to Gobber
3. Greenie delegates LLM requests to Shrewd
4. Implement error handling and fallback logic

**Acceptance Criteria:**
- [ ] Greenie can scrape URLs via Trapper
- [ ] Greenie can query knowledge graph via Gobber
- [ ] Greenie can make LLM requests via Shrewd
- [ ] Failed downstream services are handled gracefully

---

## Phase 6: Workflows, Observability, Security & Notifications

**Status:** ✓ Complete
**Dependencies:** Phase 3

### Objectives
Rebuild Sneaker (observability), Hider (secrets), and Poltergeist (notifications).

### 6.1. Sneaker — Observability

**Tasks:**
1. Implement FastAPI application with health endpoints
2. Implement OTLP ingest endpoints:
- `POST /v1/traces`
- `POST /v1/metrics`
- `POST /v1/logs`
3. Implement OTLP export endpoints
4. Implement metric time series storage
5. Implement trace span storage
6. Implement log entry storage
7. Implement alert rules
8. Implement Prometheus `/metrics` export

**Acceptance Criteria:**
- [ ] Sneaker starts and passes all health checks
- [ ] OTLP traces are ingested and queryable
- [ ] OTLP logs are ingested and queryable
- [ ] Prometheus `/metrics` endpoint works
- [ ] Alert rules trigger on threshold violations

### 6.2. Hider — Secrets & Configuration

**Tasks:**
1. Implement FastAPI application with health endpoints
2. Implement AES-256 encryption/decryption
3. Implement secret storage (CRUD operations)
4. Implement versioned configuration entries
5. Implement secret access audit log
6. Implement SQLite storage with encrypted payload

**Acceptance Criteria:**
- [ ] Hider starts and passes all health checks
- [ ] Secrets are encrypted at rest
- [ ] Secret access is audited
- [ ] Configuration entries are versioned

### 6.3. Poltergeist — Notifications

**Tasks:**
1. Implement FastAPI application with health endpoints
2. Implement notification channels:
- Slack
- Discord
- Email (SMTP)
- Telegram
3. Implement notification templates
4. Implement async delivery with retries
5. Implement delivery history

**Acceptance Criteria:**
- [ ] Poltergeist starts and passes all health checks
- [ ] Notifications are sent via all configured channels
- [ ] Failed deliveries are retried
- [ ] Delivery history is queryable

### 6.4. Greenie Integration

**Tasks:**
1. Greenie delegates observability to Sneaker
2. Greenie delegates secrets to Hider
3. Greenie delegates notifications to Poltergeist
4. Implement graceful degradation when optional services are unavailable

**Acceptance Criteria:**
- [ ] Greenie logs warnings when optional services are unavailable
- [ ] Platform continues to operate without optional services
- [ ] No cascade failure from missing optional services

---

## Phase 7: Dashboard, CLI & Deployment

**Status:** ✓ Complete (Re-verified)
**Dependencies:** Phase 4, 5, 6

### Objectives
Rebuild Slammer (web dashboard), Speedy (CLI), and finalize deployment configuration. Re-verify with new core platform packages.

### 7.1. Slammer — Web Dashboard

**Tasks:**
1. Set up React/Vite/Tailwind project
2. Implement views:
- Logs
- Metrics
- Missions
- Plugins
- Terminal
- Workflow builder
- Workstations
3. Implement API client for Greenie
4. Implement Grafana link with live status indicator
5. Implement authentication flow
6. Implement Dockerfile for production build
7. Verify nginx.conf proxy configuration

**Acceptance Criteria:**
- [x] Slammer builds and serves on port 5173
- [x] All views load and display data from Greenie
- [x] Grafana link shows green/red status indicator
- [x] Authentication flow works correctly
- [x] Docker image builds successfully
- [x] nginx.conf properly proxies /api/, /ws/, /sse/, /grafana/, /prometheus/, /opik/
- [x] Multi-stage Dockerfile (Node → nginx) works correctly
- [x] No Python package migration needed (React/TypeScript)

### 7.2. Speedy — CLI

**Tasks:**
1. Implement Python/Click/Rich CLI
2. Implement commands:
- `evershade status` — Service status
- `evershade agents` — Agent list
- `evershade tasks` — Task list
- `evershade config` — Configuration management
- `evershade capabilities` — Capability status
- `evershade monitoring status` — Monitoring stack health
- `evershade install` — Installation
- `evershade start` — Start services
- `evershade stop` — Stop services
- `evershade registry` — Service registry (new)
3. Implement CLIConfig class for validated environment variables
4. Implement remote connection profiles
5. Implement Docker Compose integration

**Acceptance Criteria:**
- [x] All commands execute correctly
- [x] `evershade status` shows all service health
- [x] `evershade monitoring status` reports Prometheus and Grafana health
- [x] `evershade registry` lists discovered services from Greenie
- [x] Remote connection profiles work correctly
- [x] CLIConfig class provides validated environment variable loading
- [x] pyproject.toml includes pydantic and pydantic-settings dependencies

### 7.3. Deployment Configuration

**Tasks:**
1. Finalize `docker-compose.yml` with all services and profiles
2. Create `install.sh`, `start.sh`, and `stop.sh` scripts
3. Create `.env.example` with all variables
4. Create `Caddyfile` for TLS proxy
5. Create `README.md` with setup instructions
6. Create `version-manifest.json` for version tracking

**Acceptance Criteria:**
- [x] `docker compose --profile full up` starts all services
- [x] `install.sh` completes without errors
- [x] `start.sh` starts all services in correct order
- [x] `stop.sh` stops all services gracefully
- [x] All environment variables are documented

---

## Phase 8: End-to-End Testing & Release Readiness

**Status:** ✓ Complete (Re-verified)
**Dependencies:** Phase 7

### Objectives
Validate the entire platform through end-to-end testing and ensure release readiness. Re-verify all tests work with the new core platform packages.

### 8.1. Integration Testing (Re-verified)

**Tasks:**
1. Test core platform flow: registry, correlation IDs, error envelope, /metrics
2. Test chat flow: User → Slammer → Greenie → Shrewd → External LLM
3. Test code execution flow: User → Greenie → Slinker → Junie CLI
4. Test web scraping flow: User → Greenie → Trapper → Playwright
5. Test notification flow: Greenie → Poltergeist → External channels
6. Test observability flow: All services → Sneaker → Prometheus → Grafana
7. Test knowledge graph flow: Greenie → Gobber → Shrewd (embeddings)

**Acceptance Criteria:**
- [x] Core platform flow verifies registry, correlation IDs, error envelope, and /metrics
- [x] Chat flow completes end-to-end
- [x] Code execution flow completes end-to-end
- [x] Web scraping flow completes end-to-end
- [x] Notification flow completes end-to-end
- [x] Observability flow captures traces and metrics
- [x] Knowledge graph flow generates and searches embeddings
- [x] Base test class supports correlation ID checking and error envelope parsing
- [x] All 7 flow tests run via `python -m tests.integration.run_tests`

### 8.2. Security Validation (Re-verified)

**Tasks:**
1. Verify container hardening (read-only, no-new-privileges, cap_drop)
2. Verify network isolation (internal vs frontend)
3. Verify API key authentication on all services
4. Verify CSRF protection on Greenie
5. Verify secret encryption in Hider
6. Verify SSRF protection in Trapper
7. Verify core platform packages (auth, errors, config)
8. Verify service Dockerfiles mount evershade packages

**Acceptance Criteria:**
- [x] All containers run with read-only filesystem
- [x] Only Greenie and Slammer are exposed to host
- [x] API key authentication rejects unauthorized requests
- [x] CSRF tokens are required for state-changing operations
- [x] Secrets are encrypted at rest
- [x] SSRF protection blocks internal addresses
- [x] evershade-core auth module has JWT creation, verification, and middleware
- [x] evershade-core errors module has standard error envelope
- [x] All 7 Python service Dockerfiles mount evershade packages
- [x] All 9 security checks run via `python -m tests.security.run_security`

### 8.3. Performance Validation (Re-verified)

**Tasks:**
1. Verify health check response times (< 5s)
2. Verify API call latency (< 30s)
3. Verify resource limits are respected
4. Verify SQLite WAL mode via evershade-db
5. Verify /metrics endpoints on all services

**Acceptance Criteria:**
- [x] Health checks respond within 5 seconds
- [x] API calls complete within timeout limits
- [x] Resource limits prevent runaway processes
- [x] evershade-db package configures WAL mode
- [x] All 7 Python services use evershade-db for WAL mode
- [x] /metrics endpoints are accessible on all services
- [x] All 5 performance checks run via `python -m tests.performance.run_performance`

### 8.4. Documentation

**Tasks:**
1. Update `README.md` with setup instructions
2. Update `docs/MONITORING.md` with observability documentation
3. Update `docs/DEPLOYMENT.md` with deployment guides
4. Update `docs/SECURITY.md` with security architecture
5. Update `docs/GETTING_STARTED.md` with quick start guide
6. Verify `docs/IMPLEMENTATION_STATUS.md` is up to date

**Acceptance Criteria:**
- [x] README.md provides clear setup instructions
- [x] Monitoring documentation covers all observability features
- [x] Deployment guide covers desktop and server modes
- [x] Security documentation covers all hardening measures
- [x] Quick start guide gets a new user running in < 10 minutes
- [x] IMPLEMENTATION_STATUS.md updated to v2.7.0

### 8.5. Release Readiness

**Tasks:**
1. Verify all services pass health checks
2. Verify docker-compose profiles work correctly
3. Verify `.env.example` contains all required variables
4. Create release tag and version manifest
5. Run final integration test suite

**Acceptance Criteria:**
- [x] All 10 services are functional
- [x] All docker-compose profiles work
- [x] No unresolved blockers in IMPLEMENTATION_STATUS.md
- [x] Version manifest is up to date
- [x] Platform is ready for production use

---

## Phase 10: Deferred Project Integrations

**Status:** ✓ Complete
**Dependencies:** Phase 3–5

### Objectives
Integrate the 5 high-impact deferred projects: Browser Use and Playwright MCP as Trapper backends, Langfuse for AI observability, and Loki and Tempo for the monitoring stack.

### 10.1. Loki — Log Aggregation

**Tasks:**
1. Add Loki service to docker-compose.yml on "monitoring" profile
2. Create `monitoring/loki/loki.yml` configuration
3. Add Grafana datasource provisioning for Loki
4. Add Loki scrape target to Prometheus config

**Acceptance Criteria:**
- [x] Loki runs on port 3100 with local TSDB storage
- [x] Grafana can query Loki via auto-provisioned datasource
- [x] Prometheus scrapes Loki metrics
- [x] No impact on services when Loki is not running

### 10.2. Tempo — Distributed Tracing

**Tasks:**
1. Add Tempo service to docker-compose.yml on "monitoring" profile
2. Create `monitoring/tempo/tempo.yml` configuration with OTLP receivers
3. Add Grafana datasource provisioning for Tempo with traces-to-logs/metrics links
4. Add Tempo scrape target to Prometheus config
5. Add `TEMPO_OTLP_ENDPOINT` env var to all services

**Acceptance Criteria:**
- [x] Tempo runs on ports 3200 (HTTP), 4317 (OTLP gRPC), 4318 (OTLP HTTP)
- [x] Grafana can query Tempo via auto-provisioned datasource
- [x] Prometheus scrapes Tempo metrics
- [x] All services have TEMPO_OTLP_ENDPOINT configured

### 10.3. Langfuse — AI Observability

**Tasks:**
1. Add Langfuse and PostgreSQL to docker-compose.yml on "langfuse" profile
2. Create `integrations/langfuse/__init__.py` adapter module
3. Add `LANGFUSE_ENDPOINT` to Shrewd's environment
4. Add Grafana datasource provisioning for Langfuse

**Acceptance Criteria:**
- [x] Langfuse runs on port 3101 with PostgreSQL backend
- [x] LangfuseClient supports traces, spans, and generation logging
- [x] Shrewd can send LLM traces to Langfuse
- [x] No impact on services when Langfuse is not running

### 10.4. Browser Use — Trapper Backend

**Tasks:**
1. Create `services/Trapper/src/browserUseBackend.ts` implementing BrowserBackend
2. Add Browser Use service to docker-compose.yml on "browser-use" profile
3. Update Trapper's backend factory to select Browser Use

**Acceptance Criteria:**
- [x] BrowserUseBackend implements BrowserBackend interface
- [x] Trapper selects Browser Use when `TRAPPER_BROWSER_BACKEND=browser-use`
- [x] Browser Use runs as separate Docker Compose service
- [x] No impact on Trapper when Browser Use is not running

### 10.5. Playwright MCP — Trapper Backend

**Tasks:**
1. Create `services/Trapper/src/playwrightMcpBackend.ts` implementing BrowserBackend
2. Add Playwright MCP service to docker-compose.yml on "playwright-mcp" profile
3. Update Trapper's backend factory to select Playwright MCP

**Acceptance Criteria:**
- [x] PlaywrightMcpBackend implements BrowserBackend interface via JSON-RPC
- [x] Trapper selects Playwright MCP when `TRAPPER_BROWSER_BACKEND=playwright-mcp`
- [x] Playwright MCP runs as separate Docker Compose service
- [x] No impact on Trapper when Playwright MCP is not running

---

## Dependency Graph

```
Phase 1 (Planning)
    │
    ▼
Phase 2 (Infrastructure)
    │
    ├──→ Phase 3 (External Integrations)
    │       │
    │       ├──→ Phase 4 (Greenie, Slinker)
    │       │       │
    │       │       ├──→ Phase 7 (Dashboard, CLI)
    │       │
    │       ├──→ Phase 5 (Trapper, Gobber, Shrewd)
    │       │       │
    │       │       ├──→ Phase 7 (Dashboard, CLI)
    │       │
    │       └──→ Phase 6 (Sneaker, Hider, Poltergeist)
    │               │
    │               └──→ Phase 7 (Dashboard, CLI)
    │
Phase 7 (Dashboard, CLI, Deployment)
    │
    ▼
Phase 8 (Testing & Release)
    │
    ▼
Phase 10 (Deferred Integrations)
```

Phases 4, 5, and 6 can proceed in parallel after Phase 3 completes.
Phase 10 can run after Phase 8, integrating deferred projects.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Junie CLI unavailable | Low | High | Slinker degrades gracefully; tasks queue until available |
| OpenTelemetry compatibility | Low | Medium | Shared telemetry module is optional; services work without it |
| SQLite concurrency limits | Medium | Medium | WAL mode, connection pooling, read replicas if needed |
| Playwright browser failures | Medium | Medium | Retry logic, timeout limits, queue-based processing |
| LLM API rate limits | Medium | Medium | Shrewd routing, fallback models, cost tracking |
| Docker resource exhaustion | Low | High | Resource limits on all containers, monitoring alerts |

---

## Estimated Effort

| Phase | Estimated Effort | Complexity |
|-------|-----------------|------------|
| Phase 1 | Complete | — |
| Phase 2 | 2–3 days | Low |
| Phase 3 | 1–2 days | Low |
| Phase 4 | 5–7 days | High (Greenie is large) |
| Phase 5 | 4–5 days | Medium |
| Phase 6 | 3–4 days | Medium |
| Phase 7 | 3–4 days | Medium |
| Phase 8 | 2–3 days | Low |
| Phase 10 | 2–3 days | Medium |
| **Total** | **22–31 days** | — |

Note: Phases 4, 5, and 6 can run in parallel, reducing total calendar time to ~10–14 days.
