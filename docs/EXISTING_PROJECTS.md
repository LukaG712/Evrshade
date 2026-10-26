# Evershade — External Projects Inventory and Integration Decisions

**Date:** 2026-10-26
**Context:** Greenfield rebuild — all 10 service directories are empty. This document evaluates every known external project for integration into the new Evershade platform.

---

## Evaluation Legend

| Disposition | Meaning |
|-------------|---------|
| **ADOPT** | Integrate as a core dependency or service during this rebuild |
| **ADOPT (OPTIONAL)** | Integrate as an optional profile or plugin; not required for core functionality |
| **DEFER** | Postpone until a concrete need emerges; revisit when triggered |
| **REJECT** | Not suitable for integration; documented rationale provided |
| **UNRESOLVED** | Could not verify identity, license, or maintenance status |

---

## 1. Agent Orchestration & Workflow

### 1.1. nanobot (HKUDS/nanobot)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/HKUDS/nanobot |
| **License** | MIT |
| **Stars** | ~49k |
| **Language** | Python |
| **Maintenance** | Active |
| **Purpose** | Multi-agent orchestration framework for autonomous tasks |

**Capabilities:** Multi-agent coordination, task decomposition, tool use, memory management.

**Decision: REJECT**

**Rationale:** Greenie already provides agent orchestration with missions, milestones, DAGs, pipelines, and the three-role architecture (orchestrator, workers, validators). nanobot would be a second orchestration layer with unclear added value. Greenie's mission control system is Evershade-specific and integrates with all other services.

**Integration Criteria (if revisited):** Only if nanobot provides a capability that Greenie cannot implement without significant effort, such as cross-platform agent federation.

---

### 1.2. n8n (n8n-io/n8n)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/n8n-io/n8n |
| **License** | SPL-1.0 (requires source disclosure for commercial use) |
| **Stars** | ~207k |
| **Language** | TypeScript/Node.js |
| **Maintenance** | Very active |
| **Purpose** | Visual workflow automation platform |

**Capabilities:** Visual workflow builder, 400+ integrations, scheduling, webhooks, error handling.

**Decision: REJECT**

**Rationale:** Greenie provides workflow orchestration with DAGs, pipelines, scheduling, and automation (GitHub webhooks, cron triggers). n8n's SPL-1.0 license requires source disclosure, which conflicts with Evershade's flexibility. The operational overhead of running a full n8n instance is not justified when Greenie's workflow engine handles the required use cases.

**Integration Criteria (if revisited):** Only if visual workflow editing becomes a user-facing requirement that Greenie's API cannot satisfy.

---

### 1.3. Paperclip (paperclipai/paperclip)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/paperclipai/paperclip |
| **License** | MIT |
| **Language** | Python |
| **Maintenance** | Unknown |
| **Purpose** | Agent management and deployment platform |

**Capabilities:** Agent registry, deployment, versioning.

**Decision: REJECT**

**Rationale:** Greenie already manages agent definitions, configuration, skills, and the marketplace. Paperclip's maintenance status is unclear, and the capability overlap with Greenie is high. No unique value proposition for the Evershade architecture.

---

### 1.4. Temporal (temporalio/temporal)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/temporalio/temporal |
| **License** | MIT |
| **Stars** | ~12k |
| **Language** | Go (server), Python/TS/Go SDKs |
| **Maintenance** | Very active |
| **Purpose** | Durable workflow orchestration with automatic retries and state recovery |

**Capabilities:** Durable execution, automatic retry, human-in-the-loop, workflow versioning, observability.

**Decision: REJECT**

**Rationale:** Evershade uses Redis queues (Trapper) and Greenie's native scheduler with checkpoint recovery. Temporal requires a dedicated Go server cluster, adding significant operational complexity. The current queue model handles all workloads. Temporal would only be justified for multi-day workflows with human approval gates — a use case not yet demonstrated.

**Integration Criteria (if revisited):** If missions regularly exceed hours in duration and require guaranteed recovery across restarts beyond what SQLite checkpoints provide.

---

## 2. Coding Agents

### 2.1. OpenHands (OpenHands/OpenHands)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/OpenHands/OpenHands |
| **License** | Apache 2.0 |
| **Stars** | ~86k |
| **Language** | Python/TypeScript |
| **Maintenance** | Very active |
| **Purpose** | Open-source coding agent platform |

**Capabilities:** Repository-aware coding, multi-file edits, testing, debugging, sandboxed execution.

**Decision: REJECT**

**Rationale:** Slinker already provides coding-agent execution via the Junie CLI with worktree isolation, worker management, prompt refinement, and session logging. OpenHands would be a second full agent platform with significant operational overhead. No clear capability gap in Slinker justifies the integration effort.

**Integration Criteria (if revisited):** Only if Junie CLI becomes unavailable or Slinker needs a fallback coding agent with different capabilities.

---

## 3. Browser Automation

### 3.1. Browser Use (browser-use/browser-use)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/browser-use/browser-use |
| **License** | Apache 2.0 |
| **Stars** | ~117k |
| **Language** | Python |
| **Maintenance** | Very active |
| **Purpose** | LLM-driven browser automation |

**Capabilities:** Natural language browser control, autonomous web interaction, screenshot-based reasoning.

**Decision: ADOPT (OPTIONAL)**

**Rationale:** Trapper already has Playwright-based browser automation with SSRF protection, queue-based processing, and multiple operation types (scrape, crawl, extract, interact, map, search). Browser Use's LLM-driven approach is slower and more expensive than Trapper's structured operations. However, the LLM-driven approach is valuable for unstructured browsing tasks.

**Integration Plan:**
- Added `browserUseBackend.ts` to Trapper implementing the BrowserBackend interface
- Trapper's backend factory selects Browser Use when `TRAPPER_BROWSER_BACKEND=browser-use`
- Runs as a separate Docker Compose profile (`--profile browser-use`)
- Configured via `BROWSER_USE_BACKEND_URL` environment variable
- No impact on Trapper when Browser Use is not running

---

### 3.2. Playwright MCP (microsoft/playwright-mcp)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/microsoft/playwright-mcp |
| **License** | Apache 2.0 |
| **Language** | TypeScript |
| **Maintenance** | Active |
| **Purpose** | Playwright browser automation via Model Context Protocol |

**Capabilities:** MCP-standard browser operations, agent-driven browsing, Microsoft-backed.

**Decision: ADOPT (OPTIONAL)**

**Rationale:** Trapper already uses Playwright directly with a mature integration. Playwright MCP adds an MCP client layer for agents that need to drive the browser through MCP. The adapter pattern in Trapper supports this backend.

**Integration Plan:**
- Added `playwrightMcpBackend.ts` to Trapper implementing the BrowserBackend interface
- Trapper's backend factory selects Playwright MCP when `TRAPPER_BROWSER_BACKEND=playwright-mcp`
- Runs as a separate Docker Compose profile (`--profile playwright-mcp`)
- Configured via `PLAYWRIGHT_MCP_BACKEND_URL` environment variable
- No impact on Trapper when Playwright MCP is not running

---

## 4. Memory & Knowledge

### 4.1. Mem0 (mem0ai/mem0)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/mem0ai/mem0 |
| **License** | Apache 2.0 |
| **Stars** | ~7.9k |
| **Language** | Python |
| **Maintenance** | Active |
| **Purpose** | AI agent memory layer with semantic search |

**Capabilities:** Long-term memory, semantic search, memory updates, multi-user isolation.

**Decision: REJECT**

**Rationale:** Gobber already provides knowledge graph with vector embeddings, Obsidian vault indexing, and semantic search. Mem0 would add a second memory store without solving a proven gap. Gobber's embedding pipeline uses Shrewd for generation with hash-based fallback.

**Integration Criteria (if revisited):** Only if Gobber's embedding pipeline cannot handle the required scale or if multi-tenant memory isolation becomes a requirement.

---

### 4.2. Graphiti (getzep/graphiti)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/getzep/graphiti |
| **License** | Apache 2.0 |
| **Stars** | ~32k |
| **Language** | TypeScript |
| **Maintenance** | Active |
| **Purpose** | Temporal knowledge graphs with time-aware reasoning |

**Capabilities:** Temporal edges (valid_at/invalid_at), knowledge graph reasoning, Neo4j backend.

**Decision: REJECT**

**Rationale:** Gobber already has a knowledge graph implementation. Graphiti's temporal modeling is powerful but requires Neo4j, adding significant operational complexity. Gobber's current graph is sufficient for Obsidian vault indexing and semantic search. The SQLite-first principle conflicts with Graphiti's Neo4j requirement.

**Integration Criteria (if revisited):** Only if temporal reasoning (knowing when facts were true) becomes a concrete requirement that cannot be met with Gobber's current schema.

---

## 5. LLM Gateway & Routing

### 5.1. LiteLLM (BerriAI/litellm)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/BerriAI/litellm |
| **License** | MIT (core) |
| **Language** | Python |
| **Maintenance** | Active |
| **Purpose** | Unified API for 140+ LLM providers |

**Capabilities:** Provider abstraction, cost tracking, caching, fallback routing, streaming.

**Security Concern:** ⚠️ **Supply chain attack reported in October 2024** — malicious code was injected into a release. Users should pin to verified versions and monitor for future incidents.

**Decision: REJECT**

**Rationale:** Shrewd already provides LLM provider abstraction with routing, cost tracking, and privacy classification for OpenAI, Anthropic, Google, and Ollama. LiteLLM supports 140+ providers vs Shrewd's 4, but Shrewd's interface is Evershade-specific and integrates with cost tracking. The security incident raises concerns about supply chain risk for a self-hosted platform.

**Integration Criteria (if revisited):** Only if provider count becomes a bottleneck (needing 10+ providers simultaneously) and the security concerns are resolved.

---

## 6. Observability & Evaluation

### 6.1. Langfuse (langfuse/langfuse)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/langfuse/langfuse |
| **License** | MIT (core), enterprise features behind paid tier |
| **Stars** | ~36k |
| **Language** | TypeScript |
| **Maintenance** | Very active |
| **Purpose** | LLM observability: tracing, evaluations, prompt management |

**Capabilities:** LLM call tracing, prompt versioning, evaluations, ClickHouse backend, dashboard UI.

**Decision: ADOPT (OPTIONAL)**

**Rationale:** Sneaker already provides infrastructure observability with OTLP ingest, Prometheus metrics, and Grafana dashboards. Langfuse adds AI-specific tracing (prompt management, token tracking, latency per LLM call). Complements Opik with different features.

**Integration Plan:**
- Added Langfuse to docker-compose.yml with PostgreSQL backend as optional profile (`--profile langfuse`)
- Created `integrations/langfuse/` adapter module with LangfuseClient
- Shrewd sends LLM traces to Langfuse when `LANGFUSE_ENDPOINT` is configured
- Port 3101, persistent volume for data
- No impact on services when Langfuse is disabled

---

### 6.2. Opik (comet-ml/opik)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/comet-ml/opik |
| **License** | Apache 2.0 |
| **Stars** | ~22k |
| **Language** | Python |
| **Maintenance** | Active |
| **Purpose** | LLM observability with autonomous prompt optimization |

**Capabilities:** LLM tracing, evaluations, prompt optimization, pytest integration, no enterprise paywall.

**Decision: ADOPT (OPTIONAL)**

**Rationale:** Apache 2.0 license with no enterprise paywall. Autonomous prompt optimization is built-in. Pytest integration enables CI evaluation. Already available as an optional Docker Compose profile (`--profile opik`). Integrates via Shrewd's provider layer so traces are automatically captured for every LLM call.

**Integration Plan:**
- Run as a separate Docker Compose profile, disabled by default
- Port 9000, persistent volume for data
- Shrewd sends traces to Opik when `OPIK_ENDPOINT` is configured
- No impact on services when Opik is disabled

---

### 6.3. OpenTelemetry Python (open-telemetry/opentelemetry-python)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/open-telemetry/opentelemetry-python |
| **License** | Apache 2.0 |
| **Language** | Python |
| **Maintenance** | Very active (CNCF project) |
| **Purpose** | Standard telemetry SDK: traces, metrics, logs |

**Capabilities:** Standard trace context propagation, semantic conventions, automatic instrumentation, OTLP exporter.

**Decision: ADOPT**

**Rationale:** All Python services need standard instrumentation for distributed tracing. OpenTelemetry provides:
- Standard trace context propagation across services
- Consistent semantic attributes
- Unified exporter configuration
- Automatic instrumentation for HTTP clients/servers

**Integration Plan:**
- Add `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, and `opentelemetry-exporter-otlp` to all Python services
- Configure OTLP exporter to point at Sneaker
- Keep `prometheus_client` for the `/metrics` endpoint
- Shared telemetry module at `services/shared/evershade_telemetry.py`

---

## 7. Monitoring Stack

### 7.1. Prometheus (prometheus/prometheus)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/prometheus/prometheus |
| **License** | Apache 2.0 |
| **Language** | Go |
| **Maintenance** | Very active (CNCF) |
| **Purpose** | Metrics collection and alerting |

**Decision: ADOPT (EXISTING)**

**Rationale:** Already part of the monitoring stack. All Python services expose `/metrics` endpoints. Prometheus scrapes all services plus cAdvisor and node-exporter. No changes needed.

---

### 7.2. Grafana (grafana/grafana)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/grafana/grafana |
| **License** | AGPL-3.0 |
| **Language** | Go/TypeScript |
| **Maintenance** | Very active |
| **Purpose** | Visualization and dashboards |

**Decision: ADOPT (EXISTING)**

**Rationale:** Already part of the monitoring stack. Two auto-provisioned dashboards (Evershade Overview, Container Metrics). AGPL-3.0 license is acceptable for self-hosted use.

---

### 7.3. Loki (grafana/loki)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/grafana/loki |
| **License** | AGPL-3.0 |
| **Language** | Go |
| **Maintenance** | Very active |
| **Purpose** | Log aggregation |

**Decision: ADOPT (OPTIONAL)**

**Rationale:** Sneaker already handles structured logs via OTLP. Loki adds a separate log aggregation layer with Grafana-native integration. Useful when log volume exceeds what Sneaker's SQLite can handle.

**Integration Plan:**
- Added Loki to docker-compose.yml on the "monitoring" profile
- Created `monitoring/loki/loki.yml` with local TSDB storage
- Added Grafana datasource provisioning for Loki
- Added Loki scrape target to Prometheus config
- Port 3100, persistent volume for data

---

### 7.4. Tempo (grafana/tempo)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/grafana/tempo |
| **License** | Apache 2.0 |
| **Language** | Go |
| **Maintenance** | Very active |
| **Purpose** | Distributed tracing backend |

**Decision: ADOPT (OPTIONAL)**

**Rationale:** Sneaker already accepts OTLP traces. Tempo is a dedicated trace backend with better scalability and Grafana-native trace visualization. Complements Sneaker's SQLite-based storage.

**Integration Plan:**
- Added Tempo to docker-compose.yml on the "monitoring" profile
- Created `monitoring/tempo/tempo.yml` with local storage and OTLP receivers
- Added Grafana datasource provisioning for Tempo with traces-to-logs/metrics links
- Added Tempo scrape target to Prometheus config
- Added `TEMPO_OTLP_ENDPOINT` env var to all services
- Ports 3200 (HTTP), 4317 (OTLP gRPC), 4318 (OTLP HTTP)

---

### 7.5. cAdvisor (google/cadvisor)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/google/cadvisor |
| **License** | Apache 2.0 |
| **Language** | Go |
| **Maintenance** | Active |
| **Purpose** | Container resource usage monitoring |

**Decision: ADOPT (EXISTING)**

**Rationale:** Already part of the monitoring stack. Provides container-level CPU, memory, and I/O metrics.

---

### 7.6. node-exporter (prometheus/node_exporter)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/prometheus/node_exporter |
| **License** | Apache 2.0 |
| **Language** | Go |
| **Maintenance** | Active |
| **Purpose** | Host-level metrics exporter |

**Decision: ADOPT (EXISTING)**

**Rationale:** Already part of the monitoring stack. Provides host-level CPU, memory, disk, and network metrics.

---

## 8. Resolved Projects (Previously Unresolved)

### 8.1. REA (morluto/rea)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/morluto/rea |
| **License** | MIT |
| **Stars** | ~384k |
| **Language** | TypeScript |
| **Maintenance** | Very active |
| **Purpose** | Reverse engineer anything with AI agents — from app behavior down to native binaries |

**Capabilities:** Binary analysis via Hopper integration, app feature investigation, MCP server for AI coding agents, RL environment building.

**Decision: REJECT**

**Rationale:** REA is a reverse engineering tool for AI coding agents, not a platform service. It helps agents inspect and rebuild apps, which is outside Evershade's scope. Slinker already handles coding-agent execution via Junie CLI. REA could be useful as a development tool reference but not as an integrated service.

---

### 8.2. Ponytail (DietrichGebert/ponytail)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/DietrichGebert/ponytail |
| **License** | MIT |
| **Stars** | ~160k |
| **Language** | JavaScript/TypeScript |
| **Maintenance** | Very active |
| **Purpose** | AI agent skill that makes coding agents write less code using YAGNI principles |

**Capabilities:** Code reduction (~54% less code), faster execution (~27%), cost savings (~20%), works with 20+ AI coding agents.

**Decision: REJECT**

**Rationale:** Ponytail is an AI agent skill (prompt/ruleset), not a platform service. It changes how coding agents generate code by enforcing YAGNI-first thinking. This is a development-time tool, not a runtime service. Slinker already integrates with Junie CLI for coding-agent execution — Ponytail could be used as a prompt enhancement but not as an integrated service.

---

### 8.3. i-have-adhd (ayghri/i-have-adhd)

| Attribute | Value |
|-----------|-------|
| **URL** | https://github.com/ayghri/i-have-adhd |
| **License** | MIT |
| **Stars** | ~49k |
| **Language** | Markdown |
| **Maintenance** | Active |
| **Purpose** | AI agent skill for ADHD-friendly output formatting — action-first, no fluff |

**Capabilities:** Action-first responses, numbered steps, progress tracking, concrete error messages. Works with Claude Code, Codex, Cursor, Gemini CLI.

**Decision: REJECT**

**Rationale:** i-have-adhd is an AI agent output formatting skill, not a platform service. It changes how agents present results to be more scannable and action-oriented. This is a prompt/skill file, not an integrable service. Could be referenced for agent prompt design but not integrated as a service.

---

### 8.4. Humanizer

| Attribute | Value |
|-----------|-------|
| **URL** | Unknown |
| **License** | Unknown |
| **Purpose** | Writing skill |

**Decision: REJECT**

**Rationale:** Appears to be a writing/prompt skill rather than an integrable service. Low value for platform architecture. If it is a specific repository, the identity could not be verified.

---

### 8.5. Colibri

| Attribute | Value |
|-----------|-------|
| **URL** | Unknown |
| **License** | Unknown |
| **Purpose** | Local inference (unverified) |

**Decision: DEFER**

**Rationale:** If Colibri refers to a local inference engine, Ollama already fills that role. If it refers to something else, the identity could not be verified.

---

### 8.6. Awesome Claude Skills

| Attribute | Value |
|-----------|-------|
| **URL** | Unknown (curated list) |
| **License** | Mixed |
| **Purpose** | Skill discovery and curation |

**Decision: DEFER**

**Rationale:** This is a curated list of Claude skills, not a single integrable project. Greenie has a marketplace endpoint that could eventually curate approved skills. Low priority given current functionality.

---

### 8.7. UI/UX Pro Max Skill

| Attribute | Value |
|-----------|-------|
| **URL** | Unknown |
| **License** | Unknown |
| **Purpose** | Frontend design skill |

**Decision: DEFER**

**Rationale:** A frontend design skill, not a service. Could be evaluated for Slammer frontend improvements, but low priority given current functionality.

---

## 9. Summary

| Disposition | Count | Projects |
|-------------|-------|----------|
| **ADOPT** | 4 | OpenTelemetry Python, Prometheus, Grafana, cAdvisor, node-exporter |
| **ADOPT (OPTIONAL)** | 6 | Opik, Langfuse, Browser Use, Playwright MCP, Loki, Tempo |
| **DEFER** | 2 | Awesome Claude Skills, UI/UX Pro Max, Colibri |
| **REJECT** | 12 | nanobot, n8n, Paperclip, Temporal, OpenHands, Mem0, Graphiti, LiteLLM, Humanizer, REA, Ponytail, i-have-adhd |
| **UNRESOLVED** | 0 | *(none — all resolved)* |

### Key Decisions

1. **OpenTelemetry is the telemetry standard** — All Python services adopt OpenTelemetry SDK for distributed tracing via Sneaker.
2. **Opik for AI observability** — Optional profile, Apache 2.0, no paywall. Preferred over Langfuse.
3. **Monitoring stack remains Prometheus + Grafana** — Loki and Tempo deferred until volume requires them.
4. **No second orchestration layer** — nanobot, n8n, Temporal, and Paperclip rejected in favor of Greenie's native capabilities.
5. **No second coding agent** — OpenHands rejected; Slinker with Junie CLI is sufficient.
6. **No second memory store** — Mem0 and Graphiti rejected; Gobber's knowledge graph is sufficient.
7. **No LiteLLM** — Security concerns and Shrewd's existing provider abstraction make it unnecessary.
8. **Browser automation adapters deferred** — Browser Use and Playwright MCP can be added to Trapper's adapter pattern when needed.

### Security Notes

- **LiteLLM** had a supply chain attack in October 2024. Even if adopted in the future, always pin to verified versions.
- **n8n** uses SPL-1.0 license, which requires source disclosure for commercial use.
- **Grafana/Loki** use AGPL-3.0, which is acceptable for self-hosted use but restricts SaaS redistribution.
