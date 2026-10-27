# Poltergeist

Notification and messaging hub. Send notifications to Slack, Discord, Email, Telegram, and webhooks with retry logic and templates.

[MIT License](LICENSE) · Python 3.10+ · FastAPI

---

Poltergeist is the notification and messaging hub for the Evershade ecosystem. It sends notifications through a unified API with async delivery, retry logic with exponential backoff, and notification templates with variable substitution.

**Features:**

- Slack notifications via Incoming Webhooks with Block Kit formatting
- Discord notifications via Webhooks with embedded messages
- Email via SMTP with TLS and authentication
- Telegram via Bot API with HTML formatting
- Generic HTTP webhooks
- Reusable templates with `{{variable}}` substitution
- Automatic retry with exponential backoff
- Delivery status tracking in SQLite
- Prometheus metrics at `/metrics`
- SQLite persistence

---

## Quick Start

### With Docker

```bash
docker compose up -d Poltergeist
```

### Direct

```bash
pip install -e ".[dev]"
python -m uvicorn poltergeist.api:app --host 0.0.0.0 --port 8088
```

The API is available at `http://localhost:8088`. Swagger UI at `/docs`.

---

## API Reference

All endpoints require `Authorization: Bearer <API_KEY>` except `/health` and `/metrics`.

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /metrics` | Prometheus metrics |
| `POST /api/notifications` | Send a notification |
| `GET /api/notifications` | List notifications |
| `GET /api/notifications/{id}` | Get notification by ID |
| `POST /api/templates` | Create a template |
| `GET /api/templates` | List templates |
| `POST /api/templates/{name}/send` | Send using a template |
| `DELETE /api/templates/{name}` | Delete a template |

**Send a notification:**

```bash
curl -X POST http://localhost:8088/api/notifications \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"channel": "slack", "recipient": "https://hooks.slack.com/services/T00/B00/XXX", "title": "Deployment", "message": "Version 1.14.0 deployed"}'
```

**Send using a template:**

```bash
curl -X POST http://localhost:8088/api/templates/deployment-alert/send \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"variables": {"version": "1.14.0", "environment": "production"}}'
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | *(required)* | Bearer token for API authentication |
| `PORT` | `8088` | Server port |
| `DB_PATH` | `/app/data/poltergeist.db` | SQLite database path |
| `POLTERGEIST_MAX_RETRIES` | `3` | Max delivery retry attempts |
| `SLACK_WEBHOOK_URL` | *(none)* | Slack incoming webhook URL |
| `DISCORD_WEBHOOK_URL` | *(none)* | Discord webhook URL |
| `SMTP_HOST` | `localhost` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USER` | *(none)* | SMTP username |
| `SMTP_PASSWORD` | *(none)* | SMTP password |
| `SMTP_FROM` | `noreply@evershade.local` | From address |
| `TELEGRAM_BOT_TOKEN` | *(none)* | Telegram bot token |

---

## FAQ

**What is Poltergeist's role in Evershade?**
The notification hub sending messages to Slack, Discord, email, Telegram, and webhooks.

**How does retry logic work?**
Failed notifications are retried with exponential backoff (2s, 4s, 8s). Max retries configurable via `POLTERGEIST_MAX_RETRIES`.

**Can I use templates?**
Yes. Create templates with `{{variable}}` placeholders and send notifications by providing variable values.

**How do I receive alerts from Sneaker?**
Set `EVERSHADE_POLTERGEIST_URL` and `EVERSHADE_POLTERGEIST_API_KEY` in Sneaker's environment.

---

## Support & Community

| Channel | Purpose |
|---------|---------|
| [GitHub Issues](https://github.com/LukaG712/Poltergeist/issues) | Bug reports and feature requests |
| [Evershade Docs](https://github.com/LukaG712/Evershade) | Comprehensive guides and references |
| [Discussions](https://github.com/LukaG712/Evershade/discussions) | Community discussions and Q&A |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
