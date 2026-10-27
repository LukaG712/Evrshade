# Sneaker

Observability and alerting platform. Collect metrics, traces, and logs from all services with OpenTelemetry support.

[MIT License](LICENSE) · Python 3.10+ · FastAPI · OpenTelemetry

---

Sneaker is the observability service for the Evershade ecosystem. It collects metrics, traces, and logs from all services, acts as an OpenTelemetry OTLP collector, exposes Prometheus metrics for Grafana scraping, and includes a built-in alerting system with rule-based detection and deduplication.

**Features:**

- Time-series metrics storage with labels
- Distributed tracing via OTLP ingestion
- Centralized logging with level and service filtering
- OTLP collector endpoints (`/v1/traces`, `/v1/metrics`, `/v1/logs`)
- Automatic secret redaction from OTLP data
- Rule-based alerting with deduplication and cooldown
- Alert delivery via Poltergeist (Slack, Discord, email, Telegram)
- Prometheus metrics at `/metrics`
- Metrics summary with latency percentiles (p50/p95/p99)
- SQLite persistence that survives restarts
- OTLP forwarding to external collectors

---

## Quick Start

### With Docker

```bash
docker compose up -d Sneaker
```

### Direct

```bash
pip install -e ".[dev]"
python -m uvicorn sneaker.api:app --host 0.0.0.0 --port 8086
```

The API is available at `http://localhost:8086`. Swagger UI at `/docs`.

---

## API Reference

All endpoints require `Authorization: Bearer <API_KEY>` except `/health` and `/metrics`.

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /metrics` | Prometheus metrics |
| `POST /api/metrics` | Record a metric |
| `GET /api/metrics` | Query metrics |
| `GET /api/metrics/summary` | Latency percentiles, error counts |
| `POST /api/traces` | Record a trace span |
| `GET /api/traces` | Query traces |
| `POST /api/logs` | Record a log entry |
| `GET /api/logs` | Query logs |
| `POST /v1/traces` | OTLP trace ingestion (no auth) |
| `POST /v1/metrics` | OTLP metrics ingestion (no auth) |
| `POST /v1/logs` | OTLP logs ingestion (no auth) |
| `GET /api/alerts/rules` | List alert rules |
| `GET /api/alerts` | List fired alerts |
| `POST /api/alerts/{id}/acknowledge` | Acknowledge an alert |

**Record a metric:**

```bash
curl -X POST http://localhost:8086/api/metrics \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "http_requests_total", "value": 42, "labels": {"method": "GET"}}'
```

**Send OTLP traces:**

```bash
export SNEAKER_OTLP_ENDPOINT=http://sneaker:8086
```

All Python services with OpenTelemetry support will automatically send traces to Sneaker.

---

## Alerting

Built-in alert rules with deduplication and cooldown:

| Rule | Severity | Condition | Cooldown |
|------|----------|-----------|----------|
| Service Down | Critical | A required service is down | 120s |
| Workflow Failed | Warning | A workflow or scheduled run failed | 60s |
| Disk Usage High | Warning | Disk usage above 85% | 600s |
| Auth Failures | Critical | Repeated auth failures (5+) | 300s |
| Budget Exceeded | Warning | A budget or usage limit was reached | 600s |

Set `EVERSHADE_POLTERGEIST_URL` and `EVERSHADE_POLTERGEIST_API_KEY` to enable alert delivery.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | *(required)* | Bearer token for API authentication |
| `PORT` | `8086` | Server port |
| `DB_PATH` | `/app/data/sneaker.db` | SQLite database path |
| `OTLP_ENDPOINT` | *(none)* | External OTLP collector to forward to |
| `EVERSHADE_POLTERGEIST_URL` | `http://Poltergeist:8088` | Poltergeist URL for alerts |
| `EVERSHADE_POLTERGEIST_API_KEY` | *(none)* | Poltergeist API key |

---

## FAQ

**What is Sneaker's role in Evershade?**
The central observability service collecting metrics, traces, and logs with alerting.

**How do I send OTLP traces to Sneaker?**
Set `SNEAKER_OTLP_ENDPOINT=http://sneaker:8086` in your environment.

**Does Sneaker persist data?**
Yes. All data is stored in SQLite and survives restarts. In-memory stores are capped at 10,000 entries.

**Can I forward OTLP data externally?**
Yes. Set `OTLP_ENDPOINT` to an external OTLP collector URL.

---

## Support & Community

| Channel | Purpose |
|---------|---------|
| [GitHub Issues](https://github.com/LukaG712/Sneaker/issues) | Bug reports and feature requests |
| [Evershade Docs](https://github.com/LukaG712/Evershade) | Comprehensive guides and references |
| [Discussions](https://github.com/LukaG712/Evershade/discussions) | Community discussions and Q&A |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
