# Evershade Operations Guide

**Version:** 3.3.0  
**Last Updated:** 2026-10-26  
**Audience:** System administrators and operators managing Evershade deployments.

---

## Table of Contents

- [Service Architecture](#service-architecture)
- [Required vs Optional Services](#required-vs-optional-services)
- [Diagnostics](#diagnostics)
- [Troubleshooting](#troubleshooting)
- [Backup and Restore](#backup-and-restore)
- [Upgrade Procedures](#upgrade-procedures)
- [Adding New Services](#adding-new-services)
- [Security Checklist](#security-checklist)

---

## Service Architecture

Evershade consists of 10 services plus infrastructure:

| Service | Port | Language | Purpose | Required |
|---------|------|----------|---------|----------|
| **Greenie** | 8080 | Python/FastAPI | Agent orchestration, workflows, registry | ✅ Yes |
| **Slinker** | 8000 | Python/FastAPI | Coding-agent execution | ✅ Yes |
| **Trapper** | 3000 | TypeScript/Fastify | Browser automation, scraping | ✅ Yes |
| **Gobber** | 8085 | Python/FastAPI | Memory, knowledge, storage | ✅ Yes |
| **Shrewd** | 8089 | Python/FastAPI | LLM providers, model routing | ✅ Yes |
| **Sneaker** | 8086 | Python/FastAPI | Observability, logs, metrics | ✅ Yes |
| **Hider** | 8087 | Python/FastAPI | Secrets, credentials, security | ✅ Yes |
| **Poltergeist** | 8088 | Python/FastAPI | Notifications, event delivery | ✅ Yes |
| **Slammer** | 5173 | React/Vite | Web dashboard | ✅ Yes |
| **Speedy** | CLI | Python/Click | CLI, lifecycle management | ✅ Yes |

### Optional Integrations

| Integration | Profile | Purpose |
|-------------|---------|---------|
| Prometheus | `full` / `monitoring` | Metrics collection |
| Grafana | `full` / `monitoring` | Dashboards |
| cAdvisor | `full` / `monitoring` | Container monitoring |
| node-exporter | `full` / `monitoring` | Host metrics |
| Opik | `opik` | AI observability |
| Langfuse | `langfuse` | AI trace logging |
| Loki | `monitoring` | Log aggregation |
| Tempo | `monitoring` | Distributed tracing |
| Browser Use | `browser-use` | Alternative browser backend |
| Playwright MCP | `playwright-mcp` | MCP browser backend |

---

## Diagnostics

### Quick Health Check

```bash
# Check all services
evershade status

# Run full diagnostics
evershade diagnose

# Validate configuration
evershade validate

# Check versions
evershade version
```

### Dashboard Diagnostics

Navigate to **Diagnostics** in the Slammer dashboard for:
- Service health with latency measurements
- Integration connection status
- Troubleshooting guidance

### Individual Service Checks

```bash
# Check a specific service
curl http://localhost:8080/health    # Greenie
curl http://localhost:8000/health    # Slinker
curl http://localhost:3000/health    # Trapper
curl http://localhost:8085/health    # Gobber
curl http://localhost:8086/health    # Sneaker
curl http://localhost:8087/health    # Hider
curl http://localhost:8088/health    # Poltergeist
curl http://localhost:8089/health    # Shrewd

# Check metrics
curl http://localhost:8080/metrics
curl http://localhost:8000/metrics
# ... all services expose /metrics
```

### Service Registry

```bash
# List registered services
evershade registry

# Via API
curl http://localhost:8080/api/registry
```

---

## Troubleshooting

### Service Won't Start

1. Check Docker logs:
   ```bash
   docker compose logs --tail=100 <service-name>
   ```

2. Verify environment variables:
   ```bash
   docker compose exec <service-name> env | grep EVERSHADE
   ```

3. Check port conflicts:
   ```bash
   # Windows
   netstat -ano | findstr :8080
   # Linux/macOS
   lsof -i :8080
   ```

### Database Issues

All Python services use SQLite with WAL mode. Common issues:

1. **Database locked**: Service may not have shut down cleanly.
   ```bash
   # Remove WAL files (service will recreate)
   docker compose exec <service-name> rm -f /data/app.db-wal /data/app.db-shm
   ```

2. **Corrupted database**: Restore from backup.
   ```bash
   cp backups/app.db.bak /path/to/data/app.db
   ```

### Network Issues

1. **Inter-service communication fails**:
   - Verify services are on the same Docker network (`internal`)
   - Check DNS resolution: `docker compose exec <service> ping <other-service>`

2. **External API calls fail**:
   - Check `EXTERNAL_NETWORK` configuration
   - Verify proxy settings if behind a firewall

### LLM Provider Issues

1. **Model not responding**:
   ```bash
   # Check Shrewd provider status
   evershade models
   
   # Check usage stats
   curl http://localhost:8089/api/usage/stats
   ```

2. **Authentication errors**:
   - Verify API keys in Hider: `evershade secrets list`
   - Check provider configuration: `curl http://localhost:8089/api/providers`

### Notification Delivery Failures

1. Check Poltergeist logs:
   ```bash
   docker compose logs --tail=100 poltergeist
   ```

2. Verify channel configuration:
   ```bash
   curl http://localhost:8088/api/channels
   ```

3. Process pending queue:
   ```bash
   curl -X POST http://localhost:8088/api/process-queue
   ```

---

## Backup and Restore

### Database Backup

All persistent data is stored in SQLite databases in Docker volumes:

```bash
# Backup all databases
mkdir -p backups
for service in greenie slinker trapper gobber sneaker hider poltergeist shrewd; do
  docker compose exec $service tar czf /tmp/${service}-db-backup.tar.gz -C /data .
  docker compose cp $service:/tmp/${service}-db-backup.tar.gz backups/
done

# Backup encryption key (CRITICAL)
docker compose exec hider cat /data/encryption.key > backups/encryption.key
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh — Run daily via cron
DATE=$(date +%Y%m%d)
BACKUP_DIR="backups/$DATE"
mkdir -p "$BACKUP_DIR"

for service in greenie slinker gobber sneaker hider poltergeist shrewd; do
  docker compose exec $service tar czf /tmp/${service}-db.tar.gz -C /data .
  docker compose cp $service:/tmp/${service}-db.tar.gz "$BACKUP_DIR/"
done

docker compose exec hider cat /data/encryption.key > "$BACKUP_DIR/encryption.key"

# Keep only last 7 days
find backups -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;

echo "Backup complete: $BACKUP_DIR"
```

### Restore

```bash
# Stop services
evershade stop

# Restore databases
for service in greenie slinker gobber sneaker hider poltergeist shrewd; do
  docker compose cp "backups/$DATE/${service}-db.tar.gz" $service:/tmp/
  docker compose exec $service tar xzf /tmp/${service}-db.tar.gz -C /data/
done

# Restore encryption key
docker compose cp "backups/$DATE/encryption.key" hider:/data/encryption.key

# Start services
evershade start
```

---

## Upgrade Procedures

### Minor Version Upgrade (e.g., 3.2.0 → 3.3.0)

```bash
# 1. Backup
bash backup.sh

# 2. Pull latest code
git pull origin master

# 3. Rebuild images
docker compose build

# 4. Restart services
docker compose up -d

# 5. Verify
evershade status
evershade validate
```

### Major Version Upgrade

1. **Read release notes** for breaking changes
2. **Backup** all databases and encryption keys
3. **Update .env** with any new required variables
4. **Rebuild** all images: `docker compose build --no-cache`
5. **Run migrations** if applicable
6. **Verify** all services: `evershade diagnose`

---

## Adding New Services

### 1. Create Service Skeleton

```bash
# Create directory
mkdir services/MyService
cd services/MyService

# Create Dockerfile (Python example)
cat > Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 8090
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
EOF
```

### 2. Add to docker-compose.yml

```yaml
myservice:
  build: ./services/MyService
  container_name: evershade-myservice
  ports:
    - "8090:8090"
  networks:
    - internal
  environment:
    - EVERSHADE_ENVIRONMENT=${EVERSHADE_ENVIRONMENT}
    - GREENIE_URL=http://greenie:8080
  depends_on:
    - greenie
  profiles:
    - full
```

### 3. Update nginx.conf (Slammer)

Add proxy pass for the new service API endpoints.

### 4. Update Speedy CLI

Add the service to `services_list` in `main.py`.

### 5. Update Dashboard

Add the service to the diagnostics and status views.

---

## Security Checklist

- [ ] `HIDER_ENCRYPTION_KEY` is set and secure
- [ ] API keys are stored in Hider, not in code
- [ ] Services use internal Docker network
- [ ] No sensitive data in logs
- [ ] SSL/TLS configured for production (Caddy)
- [ ] Rate limiting enabled on public endpoints
- [ ] SSRF protection verified in Trapper
- [ ] Content safety audit enabled in Hider
- [ ] Service-to-service auth configured
- [ ] Regular backup schedule established

---

## Monitoring

### Grafana Dashboards

Access at `http://localhost:3000` (default admin/admin):
- **Evershade Overview** — Service health, request rates, error rates
- **Container Metrics** — CPU, memory, disk I/O per container
- **LLM Usage** — Token consumption, latency, costs

### Prometheus Queries

Access at `http://localhost:9090`:
- `http_requests_total` — Total request count
- `http_request_duration_seconds` — Request latency
- `up` — Service availability

### Alert Rules

Configure in Sneaker:
```bash
curl -X POST http://localhost:8086/api/alerts/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Error Rate",
    "metric": "http_errors_total",
    "condition": ">",
    "threshold": 100,
    "window_seconds": 300,
    "channel": "slack-alerts"
  }'
```
