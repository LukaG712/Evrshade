# Evershade

**A self-hosted AI agent platform built as a collection of specialized microservices.**

[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-React%20Dashboard-blue.svg)](https://www.typescriptlang.org)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## What Is Evershade

Evershade is a **self-hosted AI agent platform** that lets you create, manage, and run AI-powered agents on your own hardware. Think of it as your personal AI workforce that lives on your computer or server.

- **You own everything.** Your data, your agents, your conversations – nothing leaves your machine unless you explicitly connect an external AI provider.
- **It runs in Docker.** No complex setup. If you can run Docker, you can run Evershade.
- **Agents do real work.** Write code, scrape websites, search knowledge bases, send notifications, and chain tasks together.
- **Mission Control orchestrates complex projects.** Break large tasks into milestones, let AI plan and execute, then validate automatically.
- **It's modular.** Use just the core services or add observability, notifications, local LLMs – you choose what you need.

---

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **[Junie CLI](https://junie.jetbrains.com)** (optional, for code agents)

### Get Started

```bash
git clone https://github.com/LukaG712/Evershade.git && cd Evershade

# Install service repositories (required)
./install.sh --profile minimal    # Linux/macOS
# .\install.ps1 -Profile minimal  # Windows PowerShell

cp .env.example .env
# Edit .env with your API keys (required — no insecure defaults)

# Start services
./start.sh --profile minimal      # Linux/macOS
# .\start.ps1 -Profile minimal    # Windows PowerShell
```

The API will be available at **http://localhost:8080**.

> **⚠️ Security:** All services require API keys to start. There are no default or placeholder keys — generate secure keys using `openssl rand -hex 32` and set them in `.env`. Services will fail to start if required keys are missing.

> **Note:** Service repositories are maintained separately and must be cloned by the install script.

---

## GUI Installers

Evershade provides visual, step-by-step GUI installers for both **Linux** and **Windows**. The wizard handles everything: dependency checks, Docker setup, service installation, configuration, and auto-start.

### Linux GUI Installer

For a visual installation experience on Ubuntu Desktop, use the GUI installer:

```bash
# Run the launcher script (checks prerequisites and installs missing ones)
bash run-install-gui.sh

# Or run directly with sudo
sudo python3 install-gui.py
```

The Linux GUI wizard guides you through 9 steps:
1. **Welcome** — Overview of Evershade and requirements
2. **System Check** — Verifies OS version, architecture, and installed tools
3. **Installation Options** — Choose profile (minimal/standard/full/custom) and install directory. Custom mode lets you pick individual services via checkboxes.
4. **Install Docker** — Installs Docker Engine and Compose if missing
5. **Clone & Install** — Clones the repository with all services included
6. **Configure** — Creates `.env` with auto-generated secure API keys
7. **System Integration** — Optional systemd service and desktop launcher
8. **Start Services** — Launches all services with your chosen profile
9. **Complete** — Summary with quick commands and next steps

**Requirements:** Python 3.6+, Tkinter (usually pre-installed on Ubuntu Desktop), and a graphical display (X11/Wayland). For SSH sessions, use `ssh -X`.

### Windows GUI Installer

For a visual installation experience on Windows, use the GUI installer:

```batch
:: Double-click the launcher (checks Python and Tkinter)
run-install-gui.bat

:: Or run directly with Python
python install-gui-win.py
```

The Windows GUI wizard guides you through 9 steps:
1. **Welcome** — Overview of Evershade and requirements
2. **System Check** — Verifies Windows version, architecture, and installed tools
3. **Installation Options** — Choose profile (minimal/standard/full/custom) and install directory. Custom mode lets you pick individual services via checkboxes.
4. **Docker Check** — Verifies Docker Desktop is installed and running (with download link if missing)
5. **Clone & Install** — Clones the repository and installs services via PowerShell
6. **Configure** — Creates `.env` with auto-generated secure API keys
7. **Desktop Shortcut** — Optionally creates a desktop shortcut for easy launching
8. **Start Services** — Launches all services with your chosen profile
9. **Complete** — Summary with quick commands and next steps

**Requirements:** Python 3.6+ with Tkinter (included by default), Docker Desktop, and Git.

---

## Updating

Keep your Evershade installation up to date with the update scripts. These pull the latest version manifest and update each service to its pinned commit.

```bash
# Update all services (Linux/macOS)
./update.sh

# Update all services (Windows PowerShell)
.\update.ps1

# Update with a specific profile
./update.sh --profile full
.\update.ps1 -Profile full

# Force update even if already at correct commit
./update.sh --force
.\update.ps1 -Force

# Also pull latest changes from main Evershade repo
./update.sh --pull-main
.\update.ps1 -PullMain
```

### Ubuntu Desktop Update

For Ubuntu Desktop installations, use the dedicated update script that handles everything in one step:

```bash
# Interactive update with prompts
sudo bash update-ubuntu.sh

# Non-interactive update (accepts defaults)
sudo bash update-ubuntu.sh --auto

# Update without restarting services
sudo bash update-ubuntu.sh --skip-restart
```

The Ubuntu update script will:
1. Pull latest changes from the Evershade repository
2. Install any new services added to your profile
3. Update all existing services to their pinned commits
4. Optionally restart running services to apply changes
5. Update the systemd service file if present

### Installation Profiles

| Profile | Services | Command |
|---------|----------|---------|
| **Minimal** | Core only (4 services) | `docker compose --profile minimal up -d` |
| **Standard** | All services (8 services) | `docker compose --profile standard up -d` |
| **Full** | + Slammer Dashboard | `docker compose --profile full up -d` |
| **Custom** | Choose individual services | See below |
| **+ Monitoring** | Grafana + Prometheus dashboards | `docker compose --profile standard --profile monitoring up -d` |
| **+ Ollama** | Local LLM support | `docker compose --profile standard --profile ollama up -d` |
| **+ Proxy** | Caddy reverse proxy with TLS | `docker compose --profile standard --profile proxy up -d` |

### Custom Service Selection

Instead of using predefined profiles, you can choose exactly which services to install. The 4 required services (Greenie, Slinker, Trapper, Gobber) are always included, and you can toggle the optional ones:

| Service | Description |
|---------|-------------|
| **Sneaker** | Observability & alerting |
| **Hider** | Encrypted secrets management |
| **Poltergeist** | Notifications (Slack, Discord, Email, Telegram) |
| **Shrewd** | LLM providers (OpenAI, Anthropic, Google, Ollama) |
| **Slammer** | Web dashboard |
| **Speedy** | CLI tool |

**Shell (interactive menu):**
```bash
./install.sh --profile custom
.\install.ps1 -Profile custom
```

**Shell (command-line):**
```bash
./install.sh --profile custom --custom "Greenie,Slinker,Trapper,Gobber,Sneaker,Shrewd"
.\install.ps1 -Profile custom -CustomServices "Greenie,Slinker,Trapper,Gobber,Sneaker,Shrewd"
```

**Ubuntu Desktop:**
```bash
sudo bash install-ubuntu.sh --profile custom
sudo bash install-ubuntu.sh --profile custom --custom "Greenie,Slinker,Trapper,Gobber,Sneaker,Shrewd"
```

**GUI Installer:** Select "Custom" in the Installation Options step, then check/uncheck the services you want.

---

## Uninstalling

To cleanly remove Evershade from your system, use the provided uninstall scripts. They stop Docker containers, remove system services, and optionally delete the installation directory and persistent data.

### Linux

The uninstall script auto-detects your installation directory, so you can run it from anywhere:

```bash
# Basic uninstall (preserves install directory and Docker volumes)
sudo bash uninstall.sh

# Remove everything, including the install directory
sudo bash uninstall.sh --remove-dir

# Remove everything, including Docker volumes (persistent data)
sudo bash uninstall.sh --remove-dir --remove-data

# Skip confirmation prompts
sudo bash uninstall.sh --remove-dir --force
```

> **Installed in `/root/Evershade/`?** If you originally installed with `sudo` and the directory is under `/root/`, you can still uninstall — just run `sudo bash /root/Evershade/uninstall.sh --remove-dir --force`.

The uninstall script will:
1. Stop and remove all Evershade Docker containers and networks
2. Remove the systemd service (`evershade.service`) if present
3. Remove the desktop launcher if present
4. Optionally remove the installation directory (`--remove-dir`)
5. Optionally remove Docker volumes with persistent data (`--remove-data`)

### Windows

The uninstall script auto-detects your installation directory:

```powershell
# Basic uninstall (preserves install directory and Docker volumes)
powershell -ExecutionPolicy Bypass -File uninstall.ps1

# Remove everything, including the install directory
powershell -ExecutionPolicy Bypass -File uninstall.ps1 -RemoveDir

# Remove everything, including Docker volumes (persistent data)
powershell -ExecutionPolicy Bypass -File uninstall.ps1 -RemoveDir -RemoveData

# Skip confirmation prompts
powershell -ExecutionPolicy Bypass -File uninstall.ps1 -RemoveDir -Force
```

The Windows uninstall script will:
1. Stop and remove all Evershade Docker containers and networks
2. Remove the desktop shortcut if present
3. Optionally remove the installation directory (`-RemoveDir`)
4. Optionally remove Docker volumes with persistent data (`-RemoveData`)

### Manual Removal

If the uninstall script is unavailable or you simply want to remove the Evershade directory, you can do it manually:

```bash
# Stop and remove any running Evershade Docker containers
sudo docker rm -f $(sudo docker ps -aq --filter label=com.evershade) 2>/dev/null

# Remove the Docker network
sudo docker network rm evershade-network 2>/dev/null

# Remove the Evershade directory (replace with your install path)
sudo rm -rf /root/Evershade

# Optional: Remove Docker volumes (persistent data like databases)
sudo docker volume prune --filter label=com.evershade
```

> **Warning:** Manual removal skips cleaning up system services (systemd) and desktop launchers. You may need to remove them manually:
> ```bash
> # Remove systemd service (if present)
> sudo systemctl disable evershade.service 2>/dev/null
> sudo rm -f /etc/systemd/system/evershade.service
> sudo systemctl daemon-reload
>
> # Remove desktop launcher (if present)
> sudo rm -f /usr/share/applications/evershade.desktop
> ```

---

## Your First Agent

1. **Install and start** using the Quick Start commands above
2. **Open** http://localhost:8080 in your browser
3. **Create an agent:** Dashboard → Agents → Create Agent (e.g., name: `researcher`, runner: `junie`)
4. **Run a task:** Go to Chat, select your agent, and type a prompt
5. **Explore more:** Workflows, Slammer Dashboard (`:5173`), Speedy CLI (`evershade agents list`)

---

## Services at a Glance

| Service | Port | Role |
|---------|------|------|
| **Greenie** | `8080` | Central orchestrator & API backend |
| **Slinker** | `8000` | Code execution engine |
| **Trapper** | `3000` | Web scraping & crawling |
| **Gobber** | `8085` | Persistent storage & knowledge graph |
| **Sneaker** | `8086` | Observability (metrics, traces, logs) |
| **Hider** | `8087` | Encrypted secrets management |
| **Poltergeist** | `8088` | Notifications (Slack, Discord, email, Telegram) |
| **Shrewd** | `8089` | LLM provider abstraction |
| **Slammer** | `5173` | React web dashboard |
| **Speedy** | – | CLI tool (`evershade` command) |

> **🌐 Website:** Visit the [Evershade website](website/index.html) for interactive documentation.

---

## Web Interfaces

| Interface | URL |
|-----------|-----|
| **Slammer Dashboard** | `http://localhost:5173` |
| **Grafana** (monitoring) | `http://localhost:3000` |
| **Prometheus** (monitoring) | `http://localhost:9090` |
| **Greenie API Docs** | `http://localhost:8080/docs` |
| **Slinker API Docs** | `http://localhost:8000/docs` |
| **Trapper API Docs** | `http://localhost:3000/docs` |

---

## Documentation

### Getting Started

| Document | Description |
|----------|-------------|
| [Getting Started Guide](docs/GETTING_STARTED.md) | Detailed walkthrough for first-time users |
| [FAQ](docs/FAQ.md) | Answers to common questions |
| [Glossary](docs/GLOSSARY.md) | Key terms explained |

### Core Reference

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System architecture, service boundaries, data flow |
| [Service Catalog](docs/SERVICE_CATALOG.md) | Every API endpoint for every service |
| [Mission Control](docs/MISSION_CONTROL.md) | Orchestrated AI missions with milestones |
| [Agent Harness](docs/AGENT_HARNESS.md) | Spec mode, droids, skills, and hooks |
| [Workstations](docs/WORKSTATIONS.md) | Isolated agent environments |

### Configuration & Deployment

| Document | Description |
|----------|-------------|
| [Configuration](docs/CONFIGURATION.md) | Complete environment variable reference |
| [Deployment](docs/DEPLOYMENT.md) | Server mode, Proxmox, auto-start, firewall |
| [Security](docs/SECURITY.md) | Security model and best practices |

### Operations

| Document | Description |
|----------|-------------|
| [Backup & Restore](docs/BACKUP_RESTORE.md) | Data protection strategies |
| [Monitoring](docs/MONITORING.md) | Grafana, Prometheus, dashboards, and metrics |
| [Testing](docs/TESTING.md) | Test suite and quality gates |
| [Resource Requirements](docs/RESOURCES.md) | CPU, RAM, disk requirements |
| [Releases](docs/RELEASES.md) | Version compatibility and upgrade paths |

### Development

| Document | Description |
|----------|-------------|
| [Development Guide](docs/DEVELOPMENT.md) | Local setup, debugging, code style |
| [Contributing](CONTRIBUTING.md) | How to report bugs and submit PRs |

### Advanced

| Document | Description |
|----------|-------------|
| [Advanced Guide](docs/ADVANCED.md) | Internals, performance tuning, power-user patterns |

---

## Naming Theme

All services are named after ghosts from the **Luigi's Mansion** series. The repository is named **Evershade** after *Evershade Valley* from Luigi's Mansion: Dark Moon.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
