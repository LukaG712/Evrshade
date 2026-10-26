# Evershade FAQ

**Version:** 1.1.0
**Last Updated:** 2026-10-25

---

## Table of Contents

- [General](#general)
- [Installation & Setup](#installation--setup)
- [Agents & Missions](#agents--missions)
- [LLM Providers](#llm-providers)
- [Monitoring & Observability](#monitoring--observability)
- [Security](#security)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

---

## General

### What is Evershade?

Evershade is a self-hosted AI agent platform. It lets you create AI-powered agents that can write code, scrape websites, search knowledge bases, send notifications, and chain tasks together – all running on your own hardware.

### Is Evershade free?

Yes. Evershade is open-source under the MIT License. You self-host it at no cost. External LLM providers (OpenAI, Anthropic, etc.) may have their own pricing.

### How is Evershade different from ChatGPT or Claude?

ChatGPT and Claude are cloud-based chat interfaces. Evershade is a platform where AI agents **do real work**: write code in repositories, scrape and analyze websites, run tests, send notifications, and automate multi-step workflows. All data stays on your machine.

### Is my data private?

All data stays on your machine by default. When you connect external LLM providers, prompts and responses go through their APIs (subject to their privacy policies). Using Ollama for local models keeps everything on-premise.

### Can I run this on my laptop?

Yes. The minimal profile needs ~4 GB RAM and 2 CPU cores. See [Resource Requirements](RESOURCES.md) for details.

### What platforms are supported?

- **Windows 10/11** (via Docker Desktop with WSL2)
- **macOS 12+** (via Docker Desktop)
- **Linux** (Ubuntu 22.04+, Debian 12+, etc. via Docker Engine)

---

## Installation & Setup

### Why do I need to run `install.sh` after cloning?

Evershade's services live in separate Git repositories for independent development. The install script clones them into the correct directories. Without it, you only have the orchestration files (docker-compose.yml, scripts).

### Which profile should I choose?

| Profile | When to Use |
|---------|-------------|
| `minimal` | First time, core functionality only (4 services) |
| `standard` | You need observability, notifications, and LLM routing (8 services) |
| `full` | You want the Slammer web dashboard (+1 service) |
| `monitoring` | You want Grafana + Prometheus dashboards (add to any profile) |
| `opik` | You want Opik LLM observability (add to any profile) |
| `ollama` | You want local LLM support (add to any profile) |
| `proxy` | You want Caddy reverse proxy with TLS (add to any profile) |

Start with `minimal` and add profiles as needed. Profiles are composable — you can combine multiple profiles, e.g., `--profile standard --profile monitoring`.

### I'm on Windows. Will this work?

Yes. Use the PowerShell scripts (`install.ps1`, `start.ps1`, `stop.ps1`). Ensure Docker Desktop is running with WSL2 backend.

### Can I use WSL2 on Windows?

Yes. Run the bash scripts from within WSL2, or use the PowerShell scripts from PowerShell. Both work.

### How much disk space do I need?

| Profile | Minimum | Recommended |
|---------|---------|-------------|
| Minimal | 10 GB | 20 GB |
| Standard | 20 GB | 40 GB |
| + Monitoring | 25 GB | 50 GB (Prometheus + Grafana data) |
| + Ollama | 40 GB | 80 GB (models take 4-8 GB each) |

### How do I update Evershade?

```bash
# Backup first
evershade backup

# Pull latest changes
git pull

# Rebuild and restart
docker compose up -d --build
```

See [Release Notes](RELEASES.md) for version-specific migration notes.

---

## Agents & Missions

### What's an agent?

An agent is an AI-powered worker with a name, a runner (execution engine), and guidelines (behavior instructions). Agents can chat, execute code, scrape the web, and more.

### What's a mission?

A mission is a structured project that breaks large tasks into milestones and features. It includes automated planning, execution, validation, and fix-revalidate cycles. Think of it as an AI-powered software engineering sprint.

### What's the difference between an agent and a mission?

An agent is a single worker. A mission is a project that uses one or more agents to complete structured work with planning, execution, and validation.

### Can agents work together?

Yes. Missions support parallel workers, and pipelines chain multiple services together. Agents collaborate through Greenie (the orchestrator), not directly.

### What is Spec Mode?

Spec Mode is a research-first workflow. Before any code changes, the agent analyzes the repository, proposes a concrete plan, and waits for your approval. It's the safe way to use AI for code changes.

### What are droids?

Droids are specialized subagents with their own prompts, models, and tool policies. Built-in droids include `worker` (implementation), `explorer` (research), `reviewer` (code review), and `validator` (validation).

### What are skills?

Skills are reusable `SKILL.md` workflows that can be auto-discovered and invoked by agents. They're matched to tasks based on trigger phrases.

---

## Monitoring & Observability

### What monitoring tools does Evershade use?

Evershade uses a Grafana + Prometheus monitoring stack, deployed as an optional Docker Compose profile. It also supports OpenTelemetry for distributed tracing across all Python services.

### How do I enable monitoring?

```bash
# Start with monitoring profile
docker compose --profile standard --profile monitoring up -d

# Or use the start script
./start.sh --monitoring
```

Grafana will be available at `http://localhost:3000` and Prometheus at `http://localhost:9090`.

### What dashboards are available?

Two dashboards are auto-provisioned:
1. **Evershade Overview** — Service health, API request rates, latency (p50/p95/p99), HTTP errors, agent runs, queue depth, container CPU/memory, and host CPU/memory/disk.
2. **Evershade Containers** — Detailed container metrics (CPU, memory, network, disk I/O) and host resource gauges with threshold alerts.

### Which services expose metrics?

All core services expose a `/metrics` endpoint in Prometheus format:
- **Greenie** — Agent and session metrics
- **Sneaker** — OTLP ingest, stored metrics/traces/logs count
- **Gobber** — Storage and search request metrics
- **Hider** — Secret and config request metrics
- **Poltergeist** — Notification delivery metrics
- **Shrewd** — LLM routing and cost metrics
- **Slinker** — Coding agent task and worker metrics
- **Trapper** — Web scraping and crawl job metrics

Additionally, cAdvisor provides container-level metrics and node-exporter provides host-level metrics.

### How do I check monitoring status from the CLI?

```bash
# Check monitoring stack health
speedy monitoring status

# This shows Prometheus/Grafana status, scrape targets, and datasources
```

### What is the Capability Registry?

The capability registry lets you query what each service supports. Every service exposes `/api/capabilities` with version and feature information:

```bash
# Query all service capabilities
speedy capabilities

# Or query a single service
curl http://localhost:8080/api/capabilities
```

### What is OpenTelemetry integration?

All Python services support OpenTelemetry distributed tracing. When `SNEAKER_OTLP_ENDPOINT` is configured, traces flow through Sneaker as the OTLP collector. This enables end-to-end request tracing across services.

Configure in `.env`:
```
SNEAKER_OTLP_ENDPOINT=http://sneaker:4318
```

### What is Opik and how do I use it?

Opik provides LLM observability — trace individual LLM calls, track token usage, latency, and costs. Start with the Opik profile:

```bash
docker compose --profile opik up -d
```

Opik will be available at `http://localhost:9000`.

### Can I access Grafana from Slammer?

Yes. The Slammer dashboard shows a Grafana link button in the navigation bar. It automatically checks Grafana availability and shows a green/red status indicator.

### Why aren't Loki and Tempo included?

Loki (logs) and Tempo (traces) were evaluated but not included. They would add ~1.5 GB RAM overhead. Docker logs provide adequate log access, and Sneaker already handles OTLP trace ingestion. They can be added later without architectural changes.

### How do I backup monitoring data?

```bash
# Backup Prometheus data
docker run --rm -v evershade_prometheus_data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

# Backup Grafana data
docker run --rm -v evershade_grafana_data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

See [MONITORING.md](MONITORING.md) for full backup and restore instructions.

---

## LLM Providers

### Do I need an AI API key?

No. You can run Evershade without any LLM provider for basic agent management and web scraping. LLM features (chat, code generation, planning) require a provider.

### Which LLM providers are supported?

| Provider | Type | Cost |
|----------|------|------|
| OpenAI | Cloud | Per-token |
| Anthropic | Cloud | Per-token |
| Google AI | Cloud | Per-token |
| Ollama | Local | Free (your hardware) |

### How do I use a local LLM?

1. Install [Ollama](https://ollama.ai)
2. Pull a model: `ollama pull gemma4:12b`
3. Add to `.env`: `EVERSHADE_OLLAMA_URL=http://host.docker.internal:11434`
4. Start with Ollama profile: `docker compose --profile standard --profile ollama up -d`

### Can I switch between providers?

Yes. Shrewd (the LLM abstraction layer) supports multiple providers simultaneously. You can configure routing rules to use different providers for different tasks.

### How do I track LLM costs?

Shrewd tracks token usage and estimated costs. Query the usage API:
```bash
curl http://localhost:8089/api/usage \
  -H "Authorization: Bearer $EVERSHADE_SHREWD_API_KEY"
```

---

## Security

### How secure is Evershade?

Very. Services run in hardened containers with:
- Dropped Linux capabilities
- Read-only filesystems
- Network isolation (internal Docker network)
- Resource limits (CPU, memory)
- No privilege escalation

### Are secrets encrypted?

Yes. Hider encrypts all secrets at rest using AES-256-GCM. API keys use constant-time comparison to prevent timing attacks.

### Why won't my services start without API keys?

Since version 1.14.0, Evershade no longer uses insecure default API keys. All services require you to generate and set API keys in `.env` before starting. Generate keys using:

```bash
openssl rand -hex 32
```

Copy the generated key into the appropriate `EVERSHADE_*_API_KEY` variable in your `.env` file. This prevents accidental exposure of services with predictable credentials.

### Are Docker images pinned to specific versions?

Yes. All Docker images in `docker-compose.yml` and `version-manifest.json` are pinned to specific version tags (e.g., `prom/prometheus:v2.53.0`, `grafana/grafana:11.1.0`). No `:latest` tags are used, ensuring reproducible deployments and preventing unexpected breaking changes.

### Is Redis secured?

Yes. Redis requires authentication via the `EVERSHADE_REDIS_PASSWORD` variable. Services authenticate before accessing Redis, and the health check also authenticates. Generate a password using `openssl rand -hex 32` and set it in `.env`.

### Can I expose Evershade to the internet?

Yes, but you should:
1. Use the Caddy reverse proxy profile for TLS
2. Generate strong, unique API keys
3. Set a strong Redis password
4. Configure firewall rules
5. Change the Grafana admin password if monitoring is enabled

All services run with dropped Linux capabilities and no privilege escalation.

### What authentication methods are supported?

- **Service-to-service:** Bearer token API keys
- **Browser users:** Username/password with bcrypt hashing, HMAC-signed session cookies
- **RBAC:** Admin, user, and viewer roles

### Is there CSRF protection?

Yes. Greenie implements CSRF protection for cookie-authenticated sessions using the double-submit cookie pattern with HMAC-signed tokens.

---

## Performance

### How many concurrent agents can I run?

This depends on your hardware and the `EVERSHADE_MAX_CONCURRENT_WORKERS` setting:

| Workers | RAM | Use Case |
|---------|-----|----------|
| 1 | ~512 MB | Default, safe |
| 2-4 | ~1-2 GB | Moderate workloads |
| 5+ | ~2.5+ GB | Heavy workloads |

### How do I improve web scraping speed?

```bash
# Increase crawl concurrency
EVERSHADE_CRAWL_MAX_CONCURRENCY=10

# Increase page limit
EVERSHADE_CRAWL_MAX_PAGES=500
```

### What's the startup time?

| Profile | Time |
|---------|------|
| Minimal | ~30 seconds |
| Standard | ~45 seconds |
| + Monitoring | ~60 seconds (additional Prometheus + Grafana startup) |
| Full + Ollama | ~2 minutes (first time, model download) |

---

## Troubleshooting

### Services won't start

```bash
# Run diagnostics
evershade doctor

# Check logs
docker compose logs -f Greenie

# Verify Docker is running
docker info
```

### Port already in use

1. Find the conflicting process: `netstat -ano | findstr :8080` (Windows) or `lsof -i :8080` (Linux/macOS)
2. Stop the conflicting service or change the port in `docker-compose.yml`

### I can't reach the dashboard

1. Verify services are running: `docker compose ps`
2. Check bind address in `.env`: `EVERSHADE_BIND_ADDRESS=127.0.0.1` for desktop
3. Try `http://localhost:8080` (API) and `http://localhost:5173` (Slammer)

### API key authentication failed

Ensure your `.env` values match what you're passing in requests. Check the key:
```bash
grep EVERSHADE_GREENIE_API_KEY .env
```

### Docker out of memory

- **Docker Desktop:** Settings → Resources → Memory → Set to 8 GB+
- **Linux:** Check `docker info` for memory limits

### Ollama not responding

- Verify Ollama is running: `ollama list`
- Check URL: `EVERSHADE_OLLAMA_URL=http://host.docker.internal:11434`
- On Linux Docker, ensure `extra_hosts` is configured in docker-compose.yml

### How do I reset everything?

```bash
# Stop and remove all containers and volumes
docker compose down -v

# Start fresh
./start.sh --profile minimal
```

### Redis connection refused

Ensure the Redis container is running:
```bash
docker compose ps redis
docker compose logs redis
```

### Grafana won't start

1. Check if port 3000 is available: `netstat -ano | findstr :3000` (Windows) or `lsof -i :3000` (Linux/macOS)
2. Verify the monitoring profile is enabled: `docker compose --profile monitoring ps`
3. Check logs: `docker compose logs grafana`

### Prometheus shows no targets

1. Verify services are running: `docker compose ps`
2. Check Prometheus targets: `http://localhost:9090/targets`
3. Ensure services have `/metrics` endpoints — all Python services and Trapper expose them

### How do I disable monitoring?

Simply don't include the `monitoring` profile when starting:
```bash
# Start without monitoring
docker compose --profile standard up -d
```

To remove monitoring data:
```bash
docker compose --profile monitoring down -v
```

---

## Development

### How do I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on reporting bugs, suggesting features, and submitting pull requests.

### How do I run the tests?

```bash
# Unit tests (no services required)
./tests/run-all-tests.sh unit

# All tests (requires running services)
docker compose --profile standard up -d
./tests/run-all-tests.sh all
```

### How do I add a new service?

1. Create the service directory with Dockerfile and source code
2. Add to `docker-compose.yml` with appropriate profile
3. Add API key to `.env.example`
4. Add health check endpoint (`/health`)
5. Add capabilities endpoint (`/api/capabilities`) with version and features
6. Add Prometheus `/metrics` endpoint if the service has an HTTP server
7. Add OpenTelemetry instrumentation if it's a Python service
8. Update `version-manifest.json`
9. Update Prometheus scrape config in `monitoring/prometheus/prometheus.yml`
10. Update [ARCHITECTURE.md](ARCHITECTURE.md)

### What's the code style?

- **Python:** PEP 8, `ruff` for linting and formatting
- **TypeScript:** ESLint config, `prettier` for formatting
- **Commits:** Conventional Commits format (`feat:`, `fix:`, `docs:`, etc.)

### Where do I file bugs?

Use [GitHub Issues](https://github.com/LukaG712/Evershade/issues). For security vulnerabilities, report privately to the maintainers.
