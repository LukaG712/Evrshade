# Speedy

Command-line interface for the Evershade ecosystem. Manage services, agents, backups, and diagnostics from your terminal.

[MIT License](LICENSE) · Python 3.10+ · Click

---

Speedy is the command-line interface for the Evershade ecosystem. It provides the `evershade` command for managing services, agents, tasks, backups, and diagnostics from the terminal.

**Features:**

- Docker management — install, start, and stop services via Docker Compose
- Service status — check health and availability of all services
- System diagnostics — comprehensive health checks with `doctor`
- Log viewing — view logs from all or specific services
- Capabilities query — list all service capabilities, versions, and features
- Backup and restore — timestamped archives of all service databases
- Monitoring checks — Prometheus/Grafana health, scrape targets, datasources

---

## Installation

```bash
git clone https://github.com/LukaG712/Speedy.git && cd Speedy
pip install -e .
```

Verify installation:

```bash
evershade --version
```

---

## Commands

| Command | Description |
|---------|-------------|
| `evershade install` | Validate environment and install services |
| `evershade start` | Start all services |
| `evershade stop` | Stop all services |
| `evershade status` | Check status of all services |
| `evershade logs [service]` | View logs from all or a specific service |
| `evershade doctor` | Run comprehensive system diagnostics |
| `evershade capabilities` | List all service capabilities |
| `evershade backup` | Backup all service databases |
| `evershade restore` | Restore from the latest backup |
| `evershade monitoring status` | Check Prometheus/Grafana health |
| `evershade monitoring targets` | View Prometheus scrape targets |
| `evershade monitoring datasources` | View Grafana datasources |

**Quick start:**

```bash
evershade install
evershade start
evershade status
evershade doctor
```

**Backup before updates:**

```bash
evershade backup
evershade stop
evershade start
evershade doctor
```

---

## Configuration

Speedy reads configuration from environment variables, `~/.evershade/config.yaml`, or built-in defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `EVERSHADE_DIR` | `./` | Root Evershade directory |
| `EVERSHADE_GREENIE_URL` | `http://localhost:8080` | Greenie API URL |
| `EVERSHADE_API_KEY` | *(none)* | Default API key for all services |
| `DOCKER_COMPOSE_FILE` | `docker-compose.yml` | Path to docker-compose file |

**Config file (`~/.evershade/config.yaml`):**

```yaml
evershade_dir: /opt/evershade
greenie_url: http://localhost:8080
api_key: your-api-key-here
```

---

## FAQ

**What is Speedy's role in Evershade?**
The CLI for managing services via Docker Compose, checking health, viewing logs, and diagnosing issues.

**Does Speedy have a /metrics endpoint?**
No. Speedy is a CLI tool with no HTTP server.

**Can I use Speedy without Docker?**
`start`, `stop`, and `install` require Docker Compose. `capabilities`, `status`, and `monitoring` work by querying service APIs directly.

**How do backups work?**
`evershade backup` creates a timestamped tar.gz archive of all service SQLite databases in `backups/`. Use `evershade restore` to restore.

---

## Support & Community

| Channel | Purpose |
|---------|---------|
| [GitHub Issues](https://github.com/LukaG712/Speedy/issues) | Bug reports and feature requests |
| [Evershade Docs](https://github.com/LukaG712/Evershade) | Comprehensive guides and references |
| [Discussions](https://github.com/LukaG712/Evershade/discussions) | Community discussions and Q&A |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
