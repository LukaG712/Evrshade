# Evershade — Integration Setup Guide

This document provides step-by-step instructions for enabling each optional external project integration.

## Quick Reference

| Integration | Profile | Port | Status |
|-------------|---------|------|--------|
| OpenTelemetry | All services | N/A | ✅ Always enabled |
| Prometheus | monitoring | 9090 | ✅ Always enabled |
| Grafana | monitoring | 3000 | ✅ Always enabled |
| Opik | opik | 9000 | 🔧 Optional |
| Langfuse | langfuse | 3101 | 🔧 Optional |
| Loki | monitoring | 3100 | 🔧 Optional |
| Tempo | monitoring | 3200 | 🔧 Optional |
| Browser Use | browser-use | 8091 | 🔧 Optional |
| Playwright MCP | playwright-mcp | 3001 | 🔧 Optional |

---

## 1. OpenTelemetry (Always Enabled)

OpenTelemetry is enabled by default on all Python services. No configuration needed.

**What it does:**
- Distributed tracing across all services via B3 trace context propagation
- `/metrics` endpoint on every service for Prometheus scraping
- Automatic HTTP client/server instrumentation

**Configuration:**
```bash
# Point to Sneaker for OTLP trace ingestion
SNEAKER_OTLP_ENDPOINT=http://sneaker:8086

# Optional: point to Tempo for dedicated trace storage
TEMPO_OTLP_ENDPOINT=http://tempo:4317
```

**Verification:**
```bash
# Check any service's /metrics endpoint
curl http://localhost:8080/metrics

# Check trace propagation in request headers
curl -v http://localhost:8080/health 2>&1 | grep -i x-request-id
```

---

## 2. Prometheus + Grafana (Monitoring Profile)

**Start with monitoring stack:**
```bash
docker compose --profile monitoring up -d
```

**Access:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

**What's scraped:**
- All 10 Evershade services via `/metrics`
- cAdvisor for container metrics
- node-exporter for host metrics
- Loki (if enabled) on port 3100
- Tempo (if enabled) on port 3200

**Dashboards:**
- Evershade Overview — auto-provisioned
- Container Metrics — auto-provisioned

---

## 3. Opik (AI Observability)

Opik provides LLM observability with autonomous prompt optimization.

**Start Opik:**
```bash
docker compose --profile opik up -d
```

**Configure Shrewd:**
```bash
# In .env file
OPIK_ENDPOINT=http://opik:9000
```

**Access:** http://localhost:9000

**What it does:**
- Captures every LLM call made through Shrewd
- Tracks token usage, latency, and costs
- Provides prompt optimization suggestions
- Pytest integration for CI evaluation

**Verification:**
```bash
curl http://localhost:8089/api/capabilities | grep -A3 opik
```

---

## 4. Langfuse (AI Observability)

Langfuse provides LLM observability with prompt management and cost tracking.

**Start Langfuse:**
```bash
docker compose --profile langfuse up -d
```

**Configure Shrewd:**
```bash
# In .env file
LANGFUSE_ENDPOINT=http://langfuse:3000
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
```

**Get keys from Langfuse UI:**
1. Open http://localhost:3101
2. Create an account or sign in
3. Go to Settings → API Keys
4. Copy the public and secret keys

**Access:** http://localhost:3101

**What it does:**
- Creates a trace for every chat completion
- Logs generation details (model, tokens, cost)
- Tracks errors and timeouts as spans
- Provides prompt versioning and evaluation

**Verification:**
```bash
curl http://localhost:8089/api/capabilities | grep -A3 langfuse
```

---

## 5. Loki (Log Aggregation)

Loki provides log aggregation with Grafana-native integration.

**Start with monitoring stack:**
```bash
docker compose --profile monitoring up -d
```

**Access:** Via Grafana → Explore → Loki

**What it does:**
- Aggregates logs from all containers
- Provides LogQL query language
- Integrates with Grafana dashboards
- Complements Sneaker's SQLite-based log storage

**Configuration:**
- Config file: `monitoring/loki/loki.yml`
- Storage: Local TSDB at `/loki/chunks`
- Retention: 30 days

**Verification:**
```bash
curl http://localhost:3100/ready
```

---

## 6. Tempo (Distributed Tracing)

Tempo provides distributed tracing with Grafana-native visualization.

**Start with monitoring stack:**
```bash
docker compose --profile monitoring up -d
```

**Access:** Via Grafana → Explore → Tempo

**What it does:**
- Receives OTLP traces on ports 4317 (gRPC) and 4318 (HTTP)
- Stores traces locally with 30-day retention
- Links traces to logs (Loki) and metrics (Prometheus)
- Complements Sneaker's SQLite-based trace storage

**Configuration:**
- Config file: `monitoring/tempo/tempo.yml`
- OTLP receivers: `0.0.0.0:4317` (gRPC), `0.0.0.0:4318` (HTTP)
- All services have `TEMPO_OTLP_ENDPOINT=http://tempo:4317`

**Verification:**
```bash
curl http://localhost:3200
```

---

## 7. Browser Use (Trapper Backend)

Browser Use provides LLM-driven browser automation as an optional Trapper backend.

**Start Browser Use:**
```bash
docker compose --profile browser-use up -d
```

**Configure Trapper:**
```bash
# In .env file
TRAPPER_BROWSER_BACKEND=browser-use
BROWSER_USE_BACKEND_URL=http://browser-use:8091
```

**What it does:**
- LLM-driven browser automation for unstructured tasks
- Natural language browser control
- Screenshot-based reasoning
- Slower and more expensive than Playwright structured operations

**When to use it:**
- Unstructured browsing tasks that can't be expressed as structured operations
- When the agent needs to "figure out" how to navigate a page
- NOT for simple scraping, crawling, or structured extraction

**Fallback:** If Browser Use is unavailable, Trapper falls back to Playwright automatically.

**Verification:**
```bash
curl http://localhost:3000/api/capabilities | grep -A3 browserBackend
```

---

## 8. Playwright MCP (Trapper Backend)

Playwright MCP provides MCP-standard browser operations as an optional Trapper backend.

**Start Playwright MCP:**
```bash
docker compose --profile playwright-mcp up -d
```

**Configure Trapper:**
```bash
# In .env file
TRAPPER_BROWSER_BACKEND=playwright-mcp
PLAYWRIGHT_MCP_BACKEND_URL=http://playwright-mcp:3001
```

**What it does:**
- MCP-standard browser operations
- Agent-driven browsing through Model Context Protocol
- Microsoft-backed implementation

**When to use it:**
- When agents need to drive the browser through MCP
- When integrating with MCP-compatible agent frameworks
- NOT for direct API calls — use Playwright backend instead

**Fallback:** If Playwright MCP is unavailable, Trapper falls back to Playwright automatically.

**Verification:**
```bash
curl http://localhost:3000/api/capabilities | grep -A3 browserBackend
```

---

## Starting All Integrations

To start the full stack with all optional integrations:

```bash
# Start everything
docker compose --profile full --profile monitoring --profile opik --profile langfuse --profile browser-use --profile playwright-mcp up -d

# Or start specific profiles
docker compose --profile monitoring up -d    # Loki + Tempo
docker compose --profile opik up -d          # Opik
docker compose --profile langfuse up -d      # Langfuse
```

---

## Troubleshooting

### Service not reporting integration status
```bash
# Check if the service is running
docker compose ps

# Check the service capabilities endpoint
curl http://localhost:8089/api/capabilities

# Check environment variables
docker compose exec shrewd env | grep -i langfuse
```

### Langfuse not tracing
1. Verify `LANGFUSE_ENDPOINT`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY` are set
2. Check Shrewd capabilities: `curl http://localhost:8089/api/capabilities | grep langfuse`
3. Check Langfuse logs: `docker compose logs langfuse`

### Trapper backend not switching
1. Verify `TRAPPER_BROWSER_BACKEND` is set correctly
2. Check Trapper logs: `docker compose logs trapper`
3. Verify the backend service is running: `docker compose ps`

### Loki/Tempo not showing in Grafana
1. Verify monitoring profile is active: `docker compose --profile monitoring ps`
2. Check Grafana datasources: http://localhost:3000/connections/datasources
3. Verify Loki: `curl http://localhost:3100/ready`
4. Verify Tempo: `curl http://localhost:3200`

---

## Security Considerations

- **Langfuse keys** are secrets — use `.env` file, never commit to git
- **Opik** runs on the internal network by default
- **Browser Use** requires network access to the backend URL
- **Playwright MCP** requires network access to the backend URL
- All optional integrations are disabled by default — enable only what you need
