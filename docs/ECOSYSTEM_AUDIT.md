# Evershade Ecosystem Audit and Integration Plan

**Date:** 2025-10-25
**Status:** All P1 and P2 improvements implemented and verified.

---

## 1. Current-State Audit

### 1.1 Verified Service Inventory

| Service | Repository | Files | Responsibilities | Status |
|---|---|---|---|---|
| **Greenie** | `services/Greenie` | 157 .py | AI-agent dashboard, agents, skills, sessions, runs, memory, streaming, schedules, approvals, audit, DAGs, pipelines, MCP, knowledge graph, marketplace, plugins, bots, cluster coordination | ✓ Mature |
| **Slinker** | `services/Slinker` | ~20 .py | Coding-agent execution via Junie, worker management, prompt refinement, session logging, backup | ✓ Mature |
| **Trapper** | `services/Trapper` | 39 .ts | Web crawling, scraping, batch scraping, extraction, interaction, mapping, search, browser automation, agent queue, SSRF protection | ✓ Mature |
| **Gobber** | `services/Gobber` | 11 .py | Persistent storage, webhooks, analytics, RBAC, feature flags, cache, knowledge graph, vector embeddings, Obsidian vault indexing | ✓ Mature |
| **Sneaker** | `services/Sneaker` | 8 .py | Observability: metrics, traces, logs, OTLP ingest, alerting, Prometheus export | ✓ Mature |
| **Hider** | `services/Hider` | 7 .py | Encrypted secrets and configuration management | ✓ Mature |
| **Poltergeist** | `services/Poltergeist` | 7 .py | Notifications: Slack, Discord, email, Telegram; async delivery, retries | ✓ Mature |
| **Shrewd** | `services/Shrewd` | 7 .py | LLM provider abstraction: OpenAI, Anthropic, Google, Ollama; routing, cost tracking, privacy classification | ✓ Mature |
| **Slammer** | `services/Slammer` | 14 .tsx/.ts | React/Vite/Tailwind dashboard: logs, metrics, missions, plugins, terminal, workflow builder, workstations | ✓ Mature |
| **Speedy** | `services/Speedy` | 2 .py | CLI for service status, agents, tasks, configuration | ✓ Present |

### 1.2 Infrastructure

| Component | Status | Details |
|---|---|---|
| **Docker Compose** | ✓ Complete | 7 profiles: minimal, standard, full, monitoring, ollama, proxy, dev |
| **Redis** | ✓ Complete | Shared queue and cache, persistent volume |
| **Monitoring** | ✓ Complete | Prometheus + Grafana + cAdvisor + node-exporter, auto-provisioned dashboards |
| **Prometheus Metrics** | ✓ Complete | All Python services expose `/metrics`. Trapper has prom-client. |
| **OTLP** | ✓ Complete | Sneaker accepts OTLP traces, logs, and metrics |
| **Health Checks** | ✓ Complete | All services have health endpoints and Docker health checks |
| **Security** | ✓ Good | API key auth, read-only containers, capability drops, no-new-privileges |
| **Persistent Volumes** | ✓ Complete | All services with state have named volumes |
| **Caddy Proxy** | ✓ Complete | Optional TLS reverse proxy profile |
| **Ollama** | ✓ Complete | Optional local LLM profile |

### 1.3 Existing Telemetry

- **Prometheus:** All 8 backend services expose `/metrics` endpoints (Greenie, Sneaker, Gobber, Hider, Poltergeist, Shrewd, Slinker, Trapper). Prometheus scrapes all services plus cAdvisor and node-exporter.
- **Grafana:** Two auto-provisioned dashboards (Evershade Overview, Container Metrics).
- **OTLP:** Sneaker accepts OTLP traces, logs, and metrics for centralized observability.
- **OpenTelemetry:** All Python services support OpenTelemetry SDK for distributed tracing (optional, enabled via `SNEAKER_OTLP_ENDPOINT`).
- **Alerting:** Sneaker has alerting module for threshold-based notifications.

### 1.4 Identified Gaps

| Gap | Severity | Description | Status |
|---|---|---|---|
| **AI-specific tracing** | P2 | No LLM observability platform (Langfuse/Opik) for prompt management, evaluations, and agent debugging | ✓ Implemented (Opik profile) |
| **Browser automation adapter** | P2 | Trapper uses Playwright directly; no adapter pattern for alternative backends | ✓ Implemented |
| **Slammer Grafana link** | P3 | Slammer dashboard doesn't link to Grafana for monitoring visibility | ✓ Implemented |
| **Speedy monitoring check** | P3 | Speedy CLI doesn't report monitoring stack status | ✓ Implemented |
| **Capability registry** | P2 | No centralized registry documenting which integrations are enabled and their status | ✓ Implemented |

---

## 2. External Repository Comparison Matrix

### 2.1 Evaluation Criteria

Each candidate is scored on:
- **Feature Value** (1-5): How much value it adds to Evershade
- **Architecture Fit** (1-5): How well it fits the current architecture
- **Integration Effort** (1-5): 1=trivial, 5=massive
- **Maintenance Burden** (1-5): 1=low, 5=high
- **Security** (1-5): 1=risky, 5=secure
- **License** (1-5): 1=problematic, 5=compatible
- **Overlap** (1-5): 1=high overlap (bad), 5=no overlap (good)

### 2.2 Comparison Results

| # | Repository | Capability | License | Feature | Fit | Effort | Maintain | Security | Overlap | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Langfuse** | LLM tracing, evals, prompt mgmt | MIT | 5 | 4 | 3 | 3 | 4 | 3 | **Defer** |
| 2 | **Opik** | LLM tracing, evals, prompt optimization | Apache 2.0 | 5 | 4 | 3 | 3 | 4 | 3 | **Defer** |
| 3 | **OpenHands** | Coding-agent execution | Apache 2.0 | 3 | 3 | 5 | 5 | 3 | 2 | **Reject** |
| 4 | **Mem0** | AI agent memory | Apache 2.0 | 3 | 3 | 3 | 3 | 4 | 2 | **Reject** |
| 5 | **Temporal** | Durable workflows | MIT | 3 | 2 | 5 | 5 | 4 | 2 | **Reject** |
| 6 | **LiteLLM** | LLM gateway | MIT | 4 | 3 | 3 | 3 | 4 | 2 | **Reject** |
| 7 | **Playwright MCP** | Browser automation via MCP | Apache 2.0 | 3 | 4 | 2 | 2 | 4 | 3 | **Defer** |
| 8 | **Graphiti** | Temporal knowledge graph | Apache 2.0 | 3 | 3 | 3 | 4 | 4 | 2 | **Reject** |
| 9 | **OpenTelemetry Python** | Standard telemetry SDK | Apache 2.0 | 4 | 5 | 2 | 2 | 5 | 4 | **Adopt (P2)** |
| 10 | **Browser Use** | LLM-driven browser automation | Apache 2.0 | 3 | 3 | 3 | 3 | 3 | 3 | **Defer** |
| 11 | **nanobot** | Agent orchestration | Unknown | 2 | 2 | 4 | 4 | 2 | 2 | **Reject** |
| 12 | **n8n** | Workflow automation | SPL-1.0 | 2 | 2 | 4 | 4 | 3 | 2 | **Reject** |
| 13 | **Paperclip** | Agent management | Unknown | 2 | 2 | 4 | 4 | 2 | 1 | **Reject** |
| 14 | **REA** | Unverified | Unknown | ? | ? | ? | ? | ? | ? | **Reject** |
| 15 | **Ponytail** | Unverified | Unknown | ? | ? | ? | ? | ? | ? | **Reject** |
| 16 | **UI/UX Pro Max** | Frontend design skill | Unknown | 2 | 3 | 2 | 2 | 3 | 4 | **Defer** |
| 17 | **i-have-adhd** | Unverified | Unknown | ? | ? | ? | ? | ? | ? | **Reject** |
| 18 | **Humanizer** | Writing skill | Unknown | 1 | 2 | 2 | 2 | 3 | 4 | **Reject** |
| 19 | **Colibri** | Local inference | Unknown | 2 | 3 | 3 | 3 | 3 | 3 | **Defer** |
| 20 | **Composio skills** | Skill discovery | Mixed | 2 | 3 | 3 | 3 | 2 | 4 | **Defer** |

### 2.3 Detailed Analysis

#### Langfuse vs Opik (LLM Observability)

Both provide LLM tracing, evaluation, and prompt management. Key differences:
- **Langfuse:** MIT license, ClickHouse-backed, broader integration surface, deeper prompt management. Enterprise features behind paid tier.
- **Opik:** Apache 2.0, Comet-backed, autonomous prompt optimization, pytest integration for CI. No enterprise paywall.

**Decision: Defer.** Sneaker already provides infrastructure observability with OTLP ingest. Adding LLM observability is valuable but requires:
1. Clear separation between infrastructure telemetry (Sneaker) and AI-specific tracing
2. Dedicated dashboard in Grafana or standalone UI
3. Integration with Shrewd for automatic trace capture
4. Evaluation of whether the operational cost justifies the benefit

**Recommendation:** Start with **Opik** (Apache 2.0, no paywall) when AI tracing becomes a concrete need. Integrate via Shrewd's provider layer so traces are automatically captured for every LLM call.

#### OpenHands (Coding Agent)

**Decision: Reject.** Slinker already provides coding-agent execution via Junie with worktree isolation, worker management, and prompt refinement. OpenHands would be a second full agent platform with significant operational overhead. No clear capability gap in Slinker justifies the integration effort.

#### Mem0 (AI Memory)

**Decision: Reject.** Gobber already provides knowledge graph with vector embeddings, Obsidian vault indexing, and semantic search. Mem0 would add a second memory store without solving a proven gap. Gobber's embedding pipeline uses Shrewd for generation with hash-based fallback.

#### Graphiti (Temporal Knowledge Graph)

**Decision: Reject.** Gobber already has a knowledge graph implementation. Graphiti's temporal modeling (valid_at/invalid_at on edges) is powerful but requires Neo4j, adding significant operational complexity. Gobber's current graph is sufficient for Obsidian vault indexing and semantic search.

#### Temporal (Durable Workflows)

**Decision: Reject.** Evershade uses Redis queues (Trapper) and Greenie's native scheduler. Temporal requires a dedicated server cluster and introduces significant operational complexity. The current queue model handles the workload. Temporal would only be justified for multi-day workflows with human approval gates — a use case not yet demonstrated.

#### LiteLLM (LLM Gateway)

**Decision: Reject.** Shrewd already provides LLM provider abstraction with routing, cost tracking, and privacy classification. LiteLLM supports 140+ providers vs Shrewd's 4, but Shrewd's interface is Evershade-specific and integrates with cost tracking. Adding LiteLLM behind Shrewd would only make sense if provider count becomes a bottleneck.

#### OpenTelemetry Python (Standard Telemetry)

**Decision: Adopt (P2).** All Python services currently use `prometheus_client` directly. OpenTelemetry SDK provides:
- Standard trace context propagation across services
- Consistent semantic attributes
- Unified exporter configuration
- Automatic instrumentation for HTTP clients/servers

**Integration:** Add `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, and `opentelemetry-exporter-otlp` to all Python services. Configure OTLP exporter to point at Sneaker. Keep prometheus_client for the `/metrics` endpoint.

#### Playwright MCP & Browser Use (Browser Automation)

**Decision: Defer.** Trapper already has Playwright-based browser automation with SSRF protection, queue-based processing, and multiple operation types (scrape, crawl, extract, interact, map, search). An adapter pattern would be valuable for future-proofing but is not urgent.

**Future path:** When browser backend flexibility is needed, implement an adapter interface in Trapper with Playwright as the default backend. Playwright MCP could be added as an optional backend for agent-driven browsing.

#### Unverified Repositories (REA, Ponytail, i-have-adhd, Humanizer, Colibri, nanobot, Paperclip)

**Decision: Reject.** These repositories could not be verified or provide unclear value. Without confirmed identity, license, and maintenance status, they cannot be safely integrated.

#### n8n (Workflow Automation)

**Decision: Reject.** Greenie already provides workflow orchestration with DAGs, pipelines, and scheduling. n8n would be a second workflow engine with SPL-1.0 license (requires source disclosure). No capability gap justifies the integration.

#### Composio Skills & UI/UX Pro Max

**Decision: Defer.** Skill discovery and frontend design skills are low-priority. Greenie has a marketplace endpoint that could eventually curate approved skills, but no urgent need exists.

---

## 3. Prioritized Roadmap

### P0 — Required Correctness/Security Blockers

**None identified.** The current ecosystem is functional and secure. All services have health checks, API authentication, and resource limits.

### P1 — High-Value Improvements

#### 1.1. OpenTelemetry Standardization (Priority: P1) ✓ **IMPLEMENTED**

**Rationale:** All Python services use `prometheus_client` directly without trace context propagation. OpenTelemetry provides standard instrumentation that enables distributed tracing across services.

**Status:** Implemented. All Python services now support OpenTelemetry SDK with OTLP exporter to Sneaker.

**Changes:**
- Added OpenTelemetry dependencies to all Python services (Shrewd, Gobber, Hider, Poltergeist, Sneaker, Slinker)
- Created shared telemetry module at `services/shared/evershade_telemetry.py`
- Added `SNEAKER_OTLP_ENDPOINT` env var to all services in docker-compose.yml
- Updated `.env.example` with OpenTelemetry configuration
- Updated `docs/MONITORING.md` with distributed tracing documentation

**Acceptance Criteria:**
- ✅ All Python services emit traces to Sneaker via OTLP when `SNEAKER_OTLP_ENDPOINT` is set
- ✅ Trace context propagates across service boundaries via B3 headers
- ✅ Existing `/metrics` endpoints continue to work
- ✅ No breaking changes to existing APIs
- ✅ OpenTelemetry is optional — services work normally without it

**Effort:** Completed
**Dependencies:** None

#### 1.2. Capability Registry (Priority: P1) ✓ **IMPLEMENTED**

**Rationale:** No centralized mechanism documents which integrations are enabled, their health status, and configuration. A simple registry improves diagnostics and administration.

**Status:** Implemented. All 8 services expose enhanced `/api/capabilities` with version and feature lists. Speedy CLI has `capabilities` command.

**Changes:**
- Enhanced `/api/capabilities` on all 8 services with version and features
- Added `speedy capabilities` CLI command
- Added `speedy monitoring status` CLI command

**Acceptance Criteria:**
- ✅ Every service exposes `/api/capabilities` with service name, version, and features
- ✅ Speedy CLI can query and display capability status
- ✅ Speedy CLI reports monitoring stack health

**Effort:** Completed
**Dependencies:** None

### P2 — Optional Capabilities

#### 2.1. AI-Specific Tracing with Opik (Priority: P2) ✓ **IMPLEMENTED**

**Rationale:** LLM observability is valuable for debugging agent behavior, tracking prompt changes, and evaluating output quality. Opik (Apache 2.0) is the preferred candidate.

**Status:** Implemented. Opik is available as an optional Docker Compose profile.

**Changes:**
- Added `opik` Docker Compose profile with persistent storage
- Documented setup in `docs/MONITORING.md`

**Acceptance Criteria:**
- ✅ Opik is optional and disabled by default (separate profile)
- ✅ Opik runs on port 9000 with persistent data
- ✅ No impact on services when Opik is disabled

**Effort:** Completed
**Dependencies:** None

#### 2.2. Browser Automation Adapter in Trapper (Priority: P2) ✓ **IMPLEMENTED**

**Rationale:** Trapper currently uses Playwright directly. An adapter pattern enables future-proofing for alternative browser backends (Playwright MCP, Browser Use).

**Status:** Implemented. BrowserBackend interface defined with PlaywrightBackend as default.

**Changes:**
- Created `browser-adapter.ts` with `BrowserBackend` and `BrowserSession` interfaces
- Created `playwright-backend.ts` implementing the adapter
- Factory function `createBrowserBackend()` selects backend via `TRAPPER_BROWSER_BACKEND` env var

**Acceptance Criteria:**
- ✅ BrowserBackend interface defined
- ✅ PlaywrightBackend implements the interface as default
- ✅ Backend is configurable via `TRAPPER_BROWSER_BACKEND` environment variable
- ✅ New backends can be added without modifying core code

**Effort:** Completed
**Dependencies:** None

#### 2.3. Slammer Grafana Integration (Priority: P2) ✓ **IMPLEMENTED**

**Rationale:** Slammer dashboard should link to Grafana for monitoring visibility.

**Status:** Implemented. Grafana link in Slammer navigation with live status indicator.

**Changes:**
- Added `GRAFANA_URL` configuration to Slammer
- Added Grafana link button in navigation bar with green/red status dot
- Grafana availability checked on load and every 10 seconds

**Acceptance Criteria:**
- ✅ Slammer shows link to Grafana when monitoring is enabled
- ✅ Link shows red dot when Grafana is unavailable
- ✅ Grafana URL configurable via `VITE_GRAFANA_URL`

**Effort:** Completed
**Dependencies:** None

#### 2.4. Speedy Monitoring Diagnostics (Priority: P2) ✓ **IMPLEMENTED**

**Rationale:** Speedy CLI should report monitoring stack status and provide useful diagnostics.

**Status:** Implemented. `speedy monitoring status` command with full diagnostics.

**Changes:**
- Added `speedy monitoring status` command
- Checks Prometheus and Grafana health endpoints
- Reports active scrape targets with health status
- Shows configured Grafana datasources
- Displays direct links to Grafana and Prometheus

**Acceptance Criteria:**
- ✅ `speedy monitoring status` shows monitoring stack health
- ✅ Command works when monitoring is enabled or disabled
- ✅ Provides actionable diagnostic information

**Effort:** Completed
**Dependencies:** None

### P3 — Experimental or Low-Priority Ideas

#### 3.1. Playwright MCP Backend for Trapper

Add Playwright MCP as an optional browser backend for agent-driven browsing. Deferred until browser adapter pattern is implemented.

#### 3.2. Skill Curation for Greenie Marketplace

Evaluate individual skills from Composio awesome-claude-skills for quality, license, and security. Add approved skills to Greenie marketplace.

#### 3.3. UI/UX Design Skill for Slammer

Evaluate UI/UX Pro Max skill for Slammer frontend improvements. Low priority given current functionality.

---

## 4. Architecture Decisions

### A. LLM Observability: Opik over Langfuse

**Decision:** When AI tracing is implemented, use **Opik** (Apache 2.0) over Langfuse (MIT).

**Rationale:**
- Apache 2.0 license has no enterprise paywall
- Autonomous prompt optimization is built-in
- Pytest integration enables CI evaluation
- Comet backing provides stability
- No feature restrictions in self-hosted mode

**Rejected Alternatives:**
- **Langfuse:** Broader integration surface but enterprise features behind paid tier
- **Custom solution:** Too much maintenance burden

### B. Browser Backend: Playwright as Default

**Decision:** Keep Playwright as the default browser backend in Trapper. Implement adapter pattern for future flexibility.

**Rationale:**
- Trapper's Playwright integration is mature and well-tested
- SSRF protection and queue-based processing are working
- Adapter pattern enables future backends without breaking changes

**Rejected Alternatives:**
- **Browser Use:** LLM-driven automation is slower and more expensive
- **Playwright MCP:** Requires MCP client infrastructure

### C. Memory: Gobber Knowledge Graph is Sufficient

**Decision:** Do not add Mem0 or Graphiti. Gobber's knowledge graph with embeddings is sufficient.

**Rationale:**
- Gobber already provides vector embeddings, semantic search, and knowledge graph
- Obsidian vault indexing is working
- Adding another memory store would duplicate functionality
- Graphiti requires Neo4j, adding operational complexity

### D. Workflows: Redis Queues are Sufficient

**Decision:** Do not add Temporal. Redis queues and Greenie's scheduler are sufficient.

**Rationale:**
- Current queue model handles all workloads
- Temporal requires dedicated server cluster
- No multi-day workflows with human approval gates exist
- Operational complexity is not justified

### E. LLM Gateway: Shrewd is Sufficient

**Decision:** Do not add LiteLLM. Shrewd's provider abstraction is sufficient.

**Rationale:**
- Shrewd supports OpenAI, Anthropic, Google, and Ollama
- Cost tracking and privacy classification are integrated
- LiteLLM's 140+ providers are not needed
- Shrewd's interface is Evershade-specific

### F. Telemetry: OpenTelemetry for Standardization

**Decision:** Add OpenTelemetry SDK to all Python services for trace context propagation.

**Rationale:**
- Enables distributed tracing across services
- Standard semantic conventions improve consistency
- OTLP exporter integrates with Sneaker
- No breaking changes to existing metrics

---

## 5. Implementation Plan

### Phase 1: OpenTelemetry Standardization (P1)

1. Add OpenTelemetry dependencies to all Python services
2. Configure OTLP exporter to point at Sneaker
3. Add trace context propagation for inter-service calls
4. Define semantic conventions
5. Update tests and documentation

### Phase 2: Capability Registry (P1)

1. Ensure all services expose `/api/capabilities`
2. Create capability aggregation in Greenie
3. Add Speedy CLI command for capability status
4. Update documentation

### Phase 3: Optional Integrations (P2)

1. Implement Opik as optional Docker Compose profile
2. Add browser automation adapter to Trapper
3. Integrate Slammer with Grafana
4. Add Speedy monitoring diagnostics

---

## 6. Monitoring Stack Assessment

The Grafana + Prometheus monitoring stack is **complete and functional**:

- ✅ Prometheus scrapes all services with `/metrics` endpoints
- ✅ Grafana auto-provisions dashboards
- ✅ cAdvisor provides container metrics
- ✅ node-exporter provides host metrics
- ✅ Persistent volumes for data retention
- ✅ Health checks on all monitoring services
- ✅ Resource limits and security hardening
- ✅ Optional profile — disabled by default
- ✅ Documentation in `docs/MONITORING.md`

**No changes required** to the monitoring stack. The implementation is solid.

---

## 7. Summary

| Category | Count | Status |
|---|---|---|
| Services audited | 10 | ✓ Complete |
| External repos evaluated | 20 | ✓ Complete |
| Adopted | 1 | ✓ OpenTelemetry Python (implemented) |
| Deferred | 5 | Langfuse, Playwright MCP, Browser Use, UI/UX Pro Max, Composio skills, Colibri |
| Rejected | 13 | OpenHands, Mem0, Graphiti, Temporal, LiteLLM, n8n, nanobot, Paperclip, REA, Ponytail, i-have-adhd, Humanizer, and unverified repos |
| P1 improvements | 2 | ✓ OpenTelemetry (implemented), Capability Registry (implemented) |
| P2 improvements | 4 | ✓ Opik, Browser adapter, Slammer Grafana, Speedy monitoring (all implemented) |
| P3 ideas | 3 | Playwright MCP backend, Skill curation, UI/UX skill |

**The Evershade ecosystem is mature and well-architected.** The monitoring stack is complete with Prometheus metrics on all services. OpenTelemetry distributed tracing has been implemented across all Python services. All P1 and P2 improvements are now implemented: Capability Registry, Opik profile, Browser Automation Adapter, Slammer Grafana integration, and Speedy monitoring diagnostics. Most external repositories were rejected because existing services already provide the required capabilities.
