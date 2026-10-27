# Hider

Evershade secrets management and encryption service.

## Features

- Encrypted secrets storage using AES-256-GCM
- Secrets CRUD operations
- Versioned configuration management
- Audit logging for all secret access
- Service-to-service authentication tokens

## API Endpoints

- `GET /health` — Health check
- `GET /metrics` — Prometheus metrics
- `GET /api/capabilities` — Service capabilities
- `POST /api/secrets/` — Create secret
- `GET /api/secrets/` — List secrets
- `GET /api/secrets/{id}` — Get secret (decrypted)
- `PUT /api/secrets/{id}` — Update secret
- `DELETE /api/secrets/{id}` — Delete secret
- `POST /api/config/` — Create config entry
- `GET /api/config/` — List config entries
- `GET /api/config/{key}` — Get config entry

## Environment Variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | API key for authentication |
| `ENCRYPTION_KEY` | Master encryption key (required) |
| `DB_PATH` | SQLite database path (default: /app/data/hider.db) |
