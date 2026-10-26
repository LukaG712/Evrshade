# Evershade — Monitoring and Observability

**Version:** 2.0.0 (Greenfield)
**Date:** 2026-10-26

---

## Overview

Evershade uses a layered observability stack combining **OpenTelemetry** for distributed tracing, **Prometheus** for metrics collection, **Grafana** for visualization, and **Opik** (optional) for LLM-specific observability.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Evershade Services                        │
│  Greenie │ Slinker │ Trapper │ Gobber │ Shrewd │ ...        │
│                                                 │           │
│  Each service exposes:                            │           │
│  - /health  (liveness)                            │           │
│  - /ready   (readiness)                           │           │
│  - /metrics (Prometheus format)                   │           │
│  - OTLP traces (gRPC to Sneaker)                  │           │
└─────────────────────────┬─────────────────────────┘                      │
                          │                                                │
              ┌───────────▼───────────┐                                    │
              │   Sneaker (OTLP)      │                                    │
              │   Port: 8086          │                                    │
              │   - Trace collector   │                                    │
              │   - Span storage      │                                    │
              └───────────┬───────────┘                                    │
                          │                                                │
              ┌───────────▼───────────┐                                    │
              │   Prometheus          │                                    │
              │   Port: 9090          │◄──────────────────────────────────┤
              │   - Scrapes /metrics  │   Every 15s                       │
              │   - Time-series DB    │                                    │
              └───────────┬───────────┘                                    │
                          │                                                │
              ┌───────────▼───────────┐                                    │
              │   Grafana             │                                    │
              │   Port: 3000          │                                    │
              │   - Dashboards        │                                    │
              │   - Alerting          │                                    │
              └───────────────────────┘                                    │
                          │                                                │
              ┌───────────▼───────────┐                                    │
              │   cAdvisor            │                                    │
              │   Port: 8081          │                                    │
              │   - Container metrics │                                    │
              └───────────────────────┘                                    │
                          │                                                │
              ┌───────────▼───────────┐                                    │
              │   node-exporter       │                                    │
              │   Port: 9100          │                                    │
              │   - Host metrics      │                                    │
              └───────────────────────┘                                    │
                          │                                                │
      ┌──────────────────▼──────────────────┐                              │
      │   Opik (optional, profile: opik)    │                              │
      │   Port: 9000                        │                              │
      │   - LLM trace observability         │                              │
      │   - Prompt/version tracking         │                              │
      │   - Cost and latency analytics      │                              │
      └─────────────────────────────────────┘                              │
```

---

## OpenTelemetry Integration

### How It Works

Every Python service in Evershade uses the shared `evershade_telemetry` module to initialize OpenTelemetry:

1. **Traces** are exported via OTLP gRPC to Sneaker (`SNEAKER_OTLP_ENDPOINT`).
2. **Trace context** propagates across service boundaries using **B3 multi-format** headers.
3. **HTTPX client** is auto-instrumented for outgoing requests.
4. **FastAPI** is auto-instrumented for incoming requests.

### Configuration

Set the `SNEAKER_OTLP_ENDPOINT` environment variable in each service:

```yaml
environment:
  - SNEAKER_OTLP_ENDPOINT=http://Sneaker:8086
```

If `SNEAKER_OTLP_ENDPOINT` is not set, telemetry is disabled (no-op) — the service runs normally without tracing.

### Trace Context Propagation

When Service A calls Service B via HTTPX:

1. OpenTelemetry injects B3 headers (`X-B3-TraceId`, `X-B3-SpanId`, `X-B3-ParentSpanId`) into the outgoing request.
2. Service B's FastAPI instrumentation extracts these headers and continues the trace.
3. All spans appear as a single distributed trace in the collector.

To create a traced HTTPX client in your service code:

```python
from evershade_telemetry import create_traced_httpx_client

async with create_traced_httpx_client(base_url="http://Shrewd:8089") as client:
    resp = await client.post("/v1/chat/completions", json=payload)
```

### Prometheus Metrics

Each service exposes a `/metrics` endpoint in Prometheus text format. The `prometheus_client` library provides:

- **`{service}_http_requests_total`** — Counter with labels: `method`, `endpoint`, `status`.
- **`{service}_http_request_duration_seconds`** — Histogram with labels: `method`, `endpoint`.
- **`{service}_uptime_seconds`** — Gauge for process uptime.
- **`{service}_ready`** — Gauge (1=ready, 0=not ready).

Prometheus scrapes these endpoints every 15 seconds. See `monitoring/prometheus/prometheus.yml` for scrape configuration.

---

## Prometheus

### Access

- **URL:** `http://localhost:9090`
- **Profile:** `docker compose --profile monitoring up`

### Scrape Targets

| Service | Port | Metrics Path | Job Name |
|---------|------|-------------|----------|
| Greenie | 8080 | `/metrics` | `greenie` |
| Slinker | 8000 | `/metrics` | `slinker` |
| Trapper | 3000 | `/metrics` | `trapper` |
| Gobber | 8085 | `/metrics` | `gobber` |
| Sneaker | 8086 | `/metrics` | `sneaker` |
| Hider | 8087 | `/metrics` | `hider` |
| Poltergeist | 8088 | `/metrics` | `poltergeist` |
| Shrewd | 8089 | `/metrics` | `shrewd` |
| cAdvisor | 8080 | `/metrics` | `cadvisor` |
| node-exporter | 9100 | `/metrics` | `node-exporter` |
| Redis | 6379 | N/A | `redis` |

### Configuration

Edit `monitoring/prometheus/prometheus.yml` to add or modify scrape targets.

---

## Grafana

### Access

- **URL:** `http://localhost:3000`
- **Default credentials:** Check `.env` for `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`.
- **Profile:** `docker compose --profile monitoring up`

### Auto-Provisioned Data Sources

Grafana auto-provisions Prometheus as a data source via `monitoring/grafana/provisioning/datasources/prometheus.yml`.

### Dashboards

Dashboard definitions are stored in `monitoring/grafana/dashboards/` and auto-provisioned via `monitoring/grafana/provisioning/dashboards/dashboards.yml`.

---

## Opik (Optional)

### What is Opik?

Opik (by Comet ML) provides LLM-specific observability:

- **LLM call tracing** — Track individual model invocations with inputs, outputs, and metadata.
- **Prompt versioning** — Track which prompt version was used for each call.
- **Cost analytics** — Monitor token usage and costs per model/provider.
- **Latency tracking** — Measure time-to-first-token and total response time.
- **Evaluation** — Score LLM outputs against ground truth.

### Setup

1. Start Opik with the `opik` profile:
   ```bash
   docker compose --profile opik up -d
   ```

2. Access the Opik UI at `http://localhost:9000`.

3. Configure Shrewd to send traces to Opik:
   ```bash
   export OPIK_ENDPOINT=http://opik:9000
   ```

   (Already configured in `docker-compose.yml` for the Shrewd service.)

### Integration with Shrewd

Shrewd reads the `OPIK_ENDPOINT` environment variable. When set, Shrewd can send LLM invocation traces to Opik. Check the integration status:

```bash
curl http://localhost:8089/api/capabilities | jq .integrations.opik
```

Expected response when enabled:
```json
{
  "enabled": true,
  "endpoint": "http://opik:9000"
}
```

### Persistent Storage

Opik data is stored in the Docker volume `opik_data`. To preserve data across restarts, ensure the volume is not removed.

---

## cAdvisor

cAdvisor provides container-level metrics:

- CPU usage per container
- Memory usage per container
- Network I/O per container
- Disk I/O per container

Access at `http://localhost:8081`.

---

## node-exporter

node-exporter provides host-level metrics:

- CPU load averages
- Memory usage
- Disk usage and I/O
- Network interfaces

Metrics available at `http://localhost:9100/metrics`.

---

## Running the Monitoring Stack

### Start all services with monitoring:

```bash
docker compose --profile full --profile monitoring up -d
```

### Start with Opik as well:

```bash
docker compose --profile full --profile monitoring --profile opik up -d
```

### Start monitoring only (for debugging):

```bash
docker compose --profile monitoring up -d
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SNEAKER_OTLP_ENDPOINT` | (empty) | OTLP gRPC endpoint for trace collection |
| `OPIK_ENDPOINT` | `http://opik:9000` | Opik API endpoint for LLM observability |
| `GRAFANA_ADMIN_USER` | `admin` | Grafana admin username |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Grafana admin password |
| `GRAFANA_ROOT_URL` | `http://localhost:3000` | Grafana root URL for alerts |

---

## Security Considerations

- **Traces** are sent over gRPC without TLS (`insecure=True`) — acceptable for local development. For production, configure mTLS between services and Sneaker.
- **Prometheus and Grafana** bind to `127.0.0.1` by default — not exposed to the network.
- **Opik** binds to `127.0.0.1:9000` by default — not exposed to the network.
- Use the `Caddy` reverse proxy (`--profile proxy`) for TLS-terminated access in production.
