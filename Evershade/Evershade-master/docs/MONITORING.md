# Monitoring with Grafana, Prometheus & OpenTelemetry

Evershade includes an optional monitoring stack that provides real-time visibility into all services through Grafana dashboards backed by Prometheus metrics, plus distributed tracing via OpenTelemetry.

## Quick Start

```bash
# Start Evershade with monitoring enabled
docker compose --profile full --profile monitoring up -d

# Open Grafana
# http://localhost:3000 (default: admin / admin)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Grafana (port 3000) — Dashboards & Visualisation           │
│  └── Auto-provisioned dashboards from monitoring/grafana/   │
└──────────────────────────┬──────────────────────────────────┘
                           │ scrapes
┌──────────────────────────▼──────────────────────────────────┐
│  Prometheus (port 9090) — Metrics Collection & Storage      │
│  └── Config: monitoring/prometheus/prometheus.yml           │
│  └── Data: persisted in prometheus_data volume              │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────┘
   │      │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
 Greenie Sneaker Gobber Hider Polter Shrewd cAdvisor node-
  :8080  :8086  :8085  :8087  :8088  :8089  :8081  exporter
                                                :9100
```

## Components

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **Prometheus** | `prom/prometheus:v2.53.0` | `9090` | Metrics collection and storage |
| **Grafana** | `grafana/grafana:11.1.0` | `3000` | Dashboards and visualisation |
| **cAdvisor** | `gcr.io/cadvisor/cadvisor:v0.49.1` | `8081` | Container resource metrics |
| **node-exporter** | `prom/node-exporter:v1.8.2` | `9100` | Host hardware/OS metrics |

## Dashboards

Two dashboards are auto-provisioned on first start:

### 1. Evershade Overview

- **Service health** — Green status indicators for each service
- **API request rates** — Requests per second per service
- **Latency** — p50, p95, p99 request latency
- **HTTP errors** — 5xx error rates by service and status code
- **Active requests** — In-flight request count
- **Agent runs** — Run outcomes over time
- **Queue depth** — Background job queue size
- **Container CPU & memory** — Per-container resource usage
- **Host CPU, memory, disk** — System-level metrics

### 2. Evershade Containers & Infrastructure

- **Container CPU, memory, network, disk** — Detailed per-container breakdown
- **Host resources** — CPU, memory, disk with threshold alerts
- **Network traffic** — RX/TX per interface
- **Uptime** — System uptime gauge

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Grafana admin credentials (CHANGE for production!)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
GRAFANA_ROOT_URL=http://localhost:3000
```

### Prometheus Targets

Edit `monitoring/prometheus/prometheus.yml` to add or remove scrape targets. All Evershade services are pre-configured.

### Scrape Interval

Default is 15 seconds. Change in `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
```

## Data Persistence

Monitoring data is stored in Docker volumes:

| Volume | Purpose |
|--------|---------|
| `prometheus_data` | Time-series metrics (30-day retention by default) |
| `grafana_data` | Dashboard edits, users, preferences |

To backup:
```bash
docker run --rm -v evershade_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .
docker run --rm -v evershade_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

To restore:
```bash
docker compose --profile monitoring stop prometheus grafana
docker run --rm -v evershade_prometheus_data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus-backup.tar.gz -C /data
docker run --rm -v evershade_grafana_data:/data -v $(pwd):/backup alpine tar xzf /backup/grafana-backup.tar.gz -C /data
docker compose --profile monitoring start prometheus grafana
```

## Security

### Default Configuration

- All monitoring ports bind to `127.0.0.1` by default (loopback only)
- Grafana requires authentication (no anonymous access)
- Prometheus has no authentication but is not exposed to the host network
- **All Docker images are pinned to specific versions** — no `:latest` tags are used, ensuring reproducible deployments
- **Redis requires authentication** — a password is set via `EVERSHADE_REDIS_PASSWORD`; services authenticate before accessing Redis
- **No hardcoded API key defaults** — all services require API keys to be set in `.env`; services will fail to start if keys are missing
- **Container security hardening** — monitoring services drop all Linux capabilities (`cap_drop: ALL`) and enable `no-new-privileges` where applicable

### Server Mode

For server deployments, set `EVERSHADE_BIND_ADDRESS=0.0.0.0` in `.env`. In this case:

1. **Change the Grafana admin password** immediately
2. **Generate secure API keys** for all services using `openssl rand -hex 32`
3. **Set a strong Redis password** via `EVERSHADE_REDIS_PASSWORD`
4. **Use the Caddy proxy profile** to add TLS and authentication:
   ```bash
   docker compose --profile full --profile monitoring --profile proxy up -d
   ```
5. **Restrict access** via firewall rules to trusted IPs only

### Caddy Proxy Integration

Add these routes to your `Caddyfile` to expose Grafana through the proxy:

```
grafana.yourdomain.com {
    reverse_proxy grafana:3000
    encode gzip
}
```

## Resource Usage

Approximate resource consumption of the monitoring stack:

| Service | CPU (limit) | Memory (limit) | Disk |
|---------|-------------|----------------|------|
| Prometheus | 1 core | 1 GB | ~500 MB/week |
| Grafana | 0.5 core | 512 MB | ~50 MB |
| cAdvisor | 0.5 core | 256 MB | Minimal |
| node-exporter | 0.25 core | 128 MB | Minimal |

**Total monitoring overhead:** ~2 CPU cores, ~2 GB RAM, ~500 MB disk/week

## Service Metrics

Each Evershade service exposes a `/metrics` endpoint in Prometheus format:

| Service | Endpoint | Metrics |
|---------|----------|---------|
| Greenie | `/metrics` | HTTP requests, latency, agent runs, queue depth, store sizes |
| Sneaker | `/metrics` | HTTP requests, latency, stored metrics/traces/logs count |
| Gobber | `/metrics` | HTTP requests, latency |
| Hider | `/metrics` | HTTP requests, latency |
| Poltergeist | `/metrics` | HTTP requests, latency |
| Shrewd | `/metrics` | HTTP requests, latency |
| Slinker | `/metrics` | HTTP requests, latency, tasks, workers, chat completions, queue depth |
| Trapper | `/metrics` | HTTP requests, latency, scrapes, crawls, browser sessions, queue depth |

## Distributed Tracing (OpenTelemetry)

All Python services support OpenTelemetry for distributed tracing. When `SNEAKER_OTLP_ENDPOINT` is set, services automatically emit traces to Sneaker via OTLP.

### How it works

1. Each service instruments HTTP requests and outgoing calls using OpenTelemetry
2. Traces are sent to Sneaker's OTLP endpoint
3. Trace context propagates across service boundaries using B3 headers
4. Sneaker stores traces and exposes them via the `/traces` API

### Configuration

In Docker Compose mode, tracing is enabled automatically. For standalone services:

```bash
# Set the OTLP endpoint to your Sneaker instance
export SNEAKER_OTLP_ENDPOINT=http://sneaker:8086
```

### Viewing Traces

- Query traces via Sneaker API: `GET /api/traces?service=Shrewd&limit=10`
- Grafana dashboards can be extended to show trace data from Sneaker

> **Note:** OpenTelemetry is optional. If `SNEAKER_OTLP_ENDPOINT` is not set, services operate normally without tracing overhead.

## Adding Custom Dashboards

1. Create a JSON dashboard file in `monitoring/grafana/dashboards/`
2. Restart Grafana: `docker compose --profile monitoring restart grafana`
3. The dashboard will be auto-provisioned on next start

You can also import Grafana.com dashboards by:
1. Finding a dashboard at <https://grafana.com/grafana/dashboards/>
2. Clicking "JSON view" and saving to `monitoring/grafana/dashboards/`
3. Restarting Grafana

## Upgrades

To upgrade the monitoring stack:

```bash
# Pull latest images
docker compose --profile monitoring pull

# Restart with new images
docker compose --profile monitoring up -d
```

Prometheus and Grafana handle schema migrations automatically. Data is preserved across upgrades.

## Removal

To remove the monitoring stack while keeping Evershade running:

```bash
# Stop monitoring services
docker compose --profile monitoring down

# Optionally remove persistent data
docker volume rm evershade_prometheus_data evershade_grafana_data
```

To remove everything including Evershade:

```bash
./stop.sh
./uninstall.sh --remove-data
```

## Troubleshooting

### Grafana shows "No data" for services

1. Verify services are running: `docker compose ps`
2. Check Prometheus targets: open `http://localhost:9090/targets`
3. Look for "DOWN" targets — these indicate connectivity issues
4. Verify the service's `/metrics` endpoint is accessible from Prometheus

### Prometheus can't reach a service

- Ensure the service is on the `internal` Docker network
- Check the service name in `prometheus.yml` matches the Docker Compose service name
- Verify the port matches the service's exposed port

### Grafana login fails

- Check `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD` in `.env`
- Restart Grafana: `docker compose --profile monitoring restart grafana`

### High disk usage from Prometheus

Reduce retention in `docker-compose.yml`:
```yaml
command:
  - '--storage.tsdb.retention.time=7d'  # Change from 30d to 7d
```

## LLM Observability with Opik

Opik provides LLM-specific observability: prompt management, evaluations, token tracking, and agent debugging. It runs as an optional Docker Compose profile.

### Quick Start

```bash
# Start Opik
docker compose --profile opik up -d

# Open Opik UI
# http://localhost:9000
```

### Configuration

Opik is configured automatically in Docker Compose mode. To integrate with Shrewd:

```bash
# Set the Opik endpoint (Docker Compose does this automatically)
export OPIK_BASE_URL=http://opik:9000
```

### Resource Usage

| Service | CPU (limit) | Memory (limit) | Disk |
|---------|-------------|----------------|------|
| Opik | 1 core | 1 GB | ~200 MB |

### Removal

```bash
docker compose --profile opik down
docker volume rm evershade_opik_data
```

## Service Capabilities Registry

Every Evershade service exposes a `/api/capabilities` endpoint that returns:
- Service name and version
- List of supported features
- Health status (implicit — endpoint responds only when service is running)

### Querying Capabilities

```bash
# Via Speedy CLI
speedy capabilities

# Via API
curl http://localhost:8080/api/capabilities
```

### Speedy Monitoring Diagnostics

The Speedy CLI includes a `monitoring` command group for checking the monitoring stack:

```bash
# Check Prometheus and Grafana status
speedy monitoring status
```

This displays:
- Prometheus and Grafana health
- Active scrape targets and their status
- Configured Grafana datasources
- Direct links to Grafana and Prometheus UIs

## Loki & Tempo (Not Included)

We evaluated Loki (logs) and Tempo (traces) but decided not to include them by default:

- **Loki** would add ~500 MB RAM and duplicate what Docker logs already provide. Use `docker logs <service>` or the Sneaker API for log queries.
- **Tempo** would add ~1 GB RAM. Sneaker already handles OTLP trace ingestion. For distributed tracing, forward OTLP data from Sneaker to an external collector.

If you need these, they can be added to the monitoring profile later without architectural changes.
