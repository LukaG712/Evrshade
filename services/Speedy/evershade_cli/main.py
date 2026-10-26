"""Speedy — CLI entry point for Evershade platform management.

Provides commands for service lifecycle, health checks, agent/task management,
configuration, and monitoring stack status.

Usage:
    evershade status          Show all service health
    evershade agents          List agents
    evershade tasks           List tasks
    evershade config          Configuration management
    evershade capabilities    Show service capabilities
    evershade monitoring      Monitoring stack health
    evershade install         Install Evershade
    evershade start           Start all services
    evershade stop            Stop all services
    evershade registry        List discovered services
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()


# ─── Configuration ───────────────────────────────────────────────────────────

class CLIConfig:
    """Validated CLI configuration using environment variables."""

    def __init__(self) -> None:
        self.base_url = os.getenv("EVERSHADE_BASE_URL", "http://localhost:8080")
        self.compose_file = os.getenv(
            "EVERSHADE_COMPOSE_FILE",
            str(Path.home() / "EvershadePage" / "Evershade" / "Evershade-master" / "docker-compose.yml"),
        )
        self.hider_url = os.getenv("HIDER_URL", "http://localhost:8087")
        self.sneaker_url = os.getenv("SNEAKER_URL", "http://localhost:8086")
        self.slinker_url = os.getenv("SLINKER_URL", "http://localhost:8000")
        self.greenie_url = os.getenv("GREENIE_URL", self.base_url)
        self.environment = os.getenv("EVERSHADE_ENVIRONMENT", "development")


cli_config = CLIConfig()


def api_get(path: str, base_url: str | None = None) -> dict[str, Any] | None:
    """Make an API GET request with timeout."""
    try:
        url = (base_url or cli_config.base_url).rstrip("/")
        response = httpx.get(f"{url}{path}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return None


def check_health(url: str) -> str:
    """Check a single service health endpoint."""
    try:
        response = httpx.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            return "healthy"
        return "unhealthy"
    except Exception:
        return "unreachable"


def run_compose(args: list[str], cwd: str | None = None) -> int:
    """Run a docker compose command."""
    cmd = [
        "docker", "compose",
        "-f", cli_config.compose_file,
    ] + args
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(result.stderr, style="dim")
        return result.returncode
    except FileNotFoundError:
        console.print("[red]Error: docker not found. Is Docker installed?[/red]")
        return 1


services_list = [
    {"name": "Greenie", "port": 8080, "desc": "Agent orchestration"},
    {"name": "Slinker", "port": 8000, "desc": "Code execution"},
    {"name": "Trapper", "port": 3000, "desc": "Browser automation"},
    {"name": "Gobber", "port": 8085, "desc": "Memory & storage"},
    {"name": "Sneaker", "port": 8086, "desc": "Observability"},
    {"name": "Hider", "port": 8087, "desc": "Secrets management"},
    {"name": "Poltergeist", "port": 8088, "desc": "Notifications"},
    {"name": "Shrewd", "port": 8089, "desc": "LLM routing"},
    {"name": "Slammer", "port": 5173, "desc": "Dashboard"},
]


@click.group()
@click.version_option(version="2.0.0", prog_name="evershade")
def cli():
    """Evershade — Self-hosted AI agent platform."""
    pass


# ─── Status ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def status(base_url: str | None):
    """Show the status of all Evershade services."""
    table = Table(title="Evershade Services")
    table.add_column("Service", style="cyan")
    table.add_column("Port", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Description", style="dim")

    base = (base_url or cli_config.base_url).rstrip("/")

    for svc in services_list:
        health = check_health(f"http://localhost:{svc['port']}")
        status_style = {
            "healthy": "green",
            "unhealthy": "red",
            "unreachable": "yellow",
        }.get(health, "yellow")

        table.add_row(
            svc["name"],
            str(svc["port"]),
            f"[{status_style}]{health}[/{status_style}]",
            svc["desc"],
        )

    console.print(table)

    # Check Greenie API
    data = api_get("/api/status", base)
    if data:
        console.print(f"\n[green]Greenie API connected[/green] — {data.get('version', 'v2.0.0')}")


# ─── Agents ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def agents(base_url: str | None):
    """List all configured agents."""
    data = api_get("/api/agents", base_url)
    if not data or "agents" not in data:
        console.print("[yellow]No agents found or Greenie is unreachable.[/yellow]")
        return

    table = Table(title="Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("Description", style="dim")

    for agent in data["agents"]:
        table.add_row(
            agent.get("name", "Unknown"),
            agent.get("status", "unknown"),
            agent.get("model", "—"),
            agent.get("description", "")[:50],
        )

    console.print(table)


# ─── Tasks ───────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Slinker API")
def tasks(base_url: str | None):
    """List all execution tasks."""
    data = api_get("/api/v1/tasks", base_url)
    if not data or "tasks" not in data:
        console.print("[yellow]No tasks found or Slinker is unreachable.[/yellow]")
        return

    table = Table(title="Tasks")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Worker", style="yellow")
    table.add_column("Progress", style="dim")

    for task in data["tasks"]:
        table.add_row(
            task.get("name", task.get("id", "?")[:8]),
            task.get("status", "unknown"),
            task.get("worker", "—"),
            f"{task.get('progress', 0)}%",
        )

    console.print(table)


# ─── Config ──────────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration management."""
    pass


@config.command(name="list")
@click.option("--base-url", default=None, help="Base URL for Hider API")
def list_config(base_url: str | None):
    """List all configuration entries."""
    hider_url = base_url or cli_config.hider_url
    data = api_get("/api/config/all", hider_url)
    if not data or "config" not in data:
        console.print("[yellow]No config found or Hider is unreachable.[/yellow]")
        return

    table = Table(title="Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Version", style="yellow")

    for entry in data["config"]:
        table.add_row(
            entry.get("key", ""),
            str(entry.get("value", ""))[:60],
            str(entry.get("version", 1)),
        )

    console.print(table)


@config.command(name="set")
@click.argument("key")
@click.argument("value")
@click.option("--base-url", default=None, help="Base URL for Hider API")
def set_config(key: str, value: str, base_url: str | None):
    """Set a configuration value."""
    hider_url = base_url or cli_config.hider_url
    try:
        response = httpx.put(
            f"{hider_url}/api/config/{key}",
            json={"value": value},
            timeout=10,
        )
        response.raise_for_status()
        console.print(f"[green]✓[/green] Config '{key}' updated.")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@config.command(name="secrets-cmd")
def _config_secrets():
    """Manage secrets (alias for secrets command)."""
    console.print("[yellow]Use 'evershade secrets' for secret management.[/yellow]")


# ─── Secrets ─────────────────────────────────────────────────────────────────

@cli.group()
def secrets():
    """Secret management via Hider."""
    pass


@secrets.command(name="list")
@click.option("--base-url", default=None, help="Base URL for Hider API")
def list_secrets(base_url: str | None):
    """List all secrets."""
    hider_url = base_url or cli_config.hider_url
    data = api_get("/api/secrets", hider_url)
    if not data or "secrets" not in data:
        console.print("[yellow]No secrets found or Hider is unreachable.[/yellow]")
        return

    table = Table(title="Secrets")
    table.add_column("Key", style="cyan")
    table.add_column("Version", style="green")

    for secret in data["secrets"]:
        table.add_row(secret.get("key", ""), str(secret.get("version", 1)))

    console.print(table)


# ─── Capabilities ────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def capabilities(base_url: str | None):
    """Show service capabilities."""
    data = api_get("/api/capabilities", base_url)
    if not data:
        console.print("[yellow]Greenie is unreachable.[/yellow]")
        return

    caps = data.get("capabilities", [])
    if not caps:
        console.print("[yellow]No capabilities reported.[/yellow]")
        return

    tree = Tree("[bold cyan]Evershade Capabilities[/bold cyan]")
    for cap in caps:
        tree.add(f"[green]✓[/green] {cap}")

    console.print(tree)


# ─── Registry ────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def registry(base_url: str | None):
    """List discovered services from the registry."""
    data = api_get("/api/registry", base_url)
    if not data or "services" not in data:
        console.print("[yellow]No services in registry or Greenie is unreachable.[/yellow]")
        return

    table = Table(title="Service Registry")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Port", style="yellow")
    table.add_column("Last Heartbeat", style="dim")

    for svc in data["services"]:
        status = svc.get("status", "unknown")
        status_style = {"registered": "green", "unhealthy": "red", "unknown": "yellow"}.get(status, "yellow")
        table.add_row(
            svc.get("name", "Unknown"),
            f"[{status_style}]{status}[/{status_style}]",
            str(svc.get("port", "—")),
            svc.get("last_heartbeat", "—")[:19],
        )

    console.print(table)


# ─── Monitoring ──────────────────────────────────────────────────────────────

@cli.group()
def monitoring():
    """Monitoring stack management."""
    pass


@monitoring.command(name="status")
def _monitoring_status():
    """Show monitoring stack health."""
    table = Table(title="Monitoring Stack")
    table.add_column("Service", style="cyan")
    table.add_column("URL", style="green")
    table.add_column("Status", style="yellow")

    monitors = [
        ("Prometheus", "http://localhost:9090", "/"),
        ("Grafana", "http://localhost:3000", "/api/health"),
        ("cAdvisor", "http://localhost:8080", "/"),
        ("node-exporter", "http://localhost:9100", "/metrics"),
    ]

    for name, url, path in monitors:
        health = check_health(f"{url}{path}")
        status_style = {
            "healthy": "green",
            "unhealthy": "red",
            "unreachable": "yellow",
        }.get(health, "yellow")
        table.add_row(name, url, f"[{status_style}]{health}[/{status_style}]")

    console.print(table)


@monitoring.command()
def logs():
    """View recent platform logs."""
    sneaker_url = cli_config.sneaker_url
    data = api_get("/api/logs?limit=50", sneaker_url)
    if not data or "logs" not in data:
        console.print("[yellow]No logs found or Sneaker is unreachable.[/yellow]")
        return

    for log in data["logs"][:20]:
        level = log.get("level", "info").upper()
        service = log.get("service", "?")
        message = log.get("message", "")
        level_style = {
            "ERROR": "red",
            "CRITICAL": "red bold",
            "WARN": "yellow",
            "INFO": "green",
            "DEBUG": "dim",
        }.get(level, "white")
        console.print(
            f"[{level_style}]{level:<8}[/{level_style}] "
            f"[cyan]{service:<12}[/cyan] "
            f"{message}"
        )


# ─── Install ─────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--profile", default="full", help="Docker Compose profile")
def install(profile: str):
    """Install Evershade platform."""
    console.print(Panel("[bold]Evershade Installation[/bold]\n\nThis will set up all services using Docker Compose."))

    if not Path(cli_config.compose_file).exists():
        console.print(f"[red]Error: docker-compose.yml not found at {cli_config.compose_file}[/red]")
        sys.exit(1)

    console.print("[yellow]Pulling images...[/yellow]")
    if run_compose(["pull", "--profile", profile]) != 0:
        console.print("[red]Failed to pull images.[/red]")
        sys.exit(1)

    console.print("[green]✓ Images pulled successfully.[/green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Copy .env.example to .env and configure")
    console.print("  2. Run 'evershade start' to start services")


# ─── Start ───────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--profile", default="full", help="Docker Compose profile")
@click.option("--detach", is_flag=True, default=True, help="Run in background")
def start(profile: str, detach: bool):
    """Start all Evershade services."""
    console.print(f"[bold]Starting Evershade[/bold] (profile: {profile})")

    args = ["up"]
    if detach:
        args.append("-d")
    args.extend(["--profile", profile])

    rc = run_compose(args)
    if rc == 0:
        console.print("[green]✓ Services started.[/green]")
        console.print("\nAccess the dashboard at: http://localhost:5173")
    else:
        console.print("[red]Failed to start services.[/red]")
        sys.exit(1)


# ─── Stop ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--profile", default="full", help="Docker Compose profile")
@click.option("--volumes", is_flag=True, default=False, help="Remove volumes too")
def stop(profile: str, volumes: bool):
    """Stop all Evershade services."""
    console.print("[bold]Stopping Evershade[/bold]")

    args = ["down"]
    if volumes:
        args.append("--volumes")
    args.extend(["--profile", profile])

    rc = run_compose(args)
    if rc == 0:
        console.print("[green]✓ Services stopped.[/green]")
    else:
        console.print("[red]Failed to stop services.[/red]")
        sys.exit(1)


# ─── Validate ────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def validate(base_url: str | None):
    """Validate configuration and environment."""
    console.print(Panel("[bold]Configuration Validation[/bold]"))

    issues = []

    # Check docker-compose.yml
    compose_path = Path(cli_config.compose_file)
    if not compose_path.exists():
        issues.append(f"docker-compose.yml not found at {cli_config.compose_file}")
    else:
        console.print("[green]✓[/green] docker-compose.yml found")

    # Check .env file
    env_path = compose_path.parent / ".env"
    if not env_path.exists():
        env_example = compose_path.parent / ".env.example"
        if env_example.exists():
            console.print("[yellow]⚠[/yellow] .env not found — copy .env.example to .env")
        else:
            issues.append(".env and .env.example not found")
    else:
        console.print("[green]✓[/green] .env file found")

    # Check Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]✓[/green] Docker installed: {result.stdout.strip()}")
        else:
            issues.append("Docker not installed or not in PATH")
    except FileNotFoundError:
        issues.append("Docker not found — install Docker Desktop")

    # Check Greenie API
    base = (base_url or cli_config.base_url).rstrip("/")
    health = check_health(base)
    if health == "healthy":
        console.print(f"[green]✓[/green] Greenie API reachable at {base}")
    else:
        console.print(f"[yellow]⚠[/yellow] Greenie API {health} at {base}")

    # Check required env vars
    required_vars = ["EVERSHADE_ENVIRONMENT"]
    for var in required_vars:
        if os.getenv(var):
            console.print(f"[green]✓[/green] {var}={os.getenv(var)}")
        else:
            console.print(f"[yellow]⚠[/yellow] {var} not set (default: development)")

    if issues:
        console.print("\n[red]Validation failed:[/red]")
        for issue in issues:
            console.print(f"  ✗ {issue}")
        sys.exit(1)
    else:
        console.print("\n[green]✓ Configuration is valid.[/green]")


# ─── Diagnose ────────────────────────────────────────────────────────────────

@cli.command()
def diagnose():
    """Run full system diagnostics."""
    console.print(Panel("[bold]System Diagnostics[/bold]"))

    # Service health
    console.print("\n[cyan]Service Health:[/cyan]")
    table = Table(show_header=True, header_style="cyan")
    table.add_column("Service", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Latency", style="dim")

    for svc in services_list:
        start = __import__("time").perf_counter()
        health = check_health(f"http://localhost:{svc['port']}")
        latency = int((__import__("time").perf_counter() - start) * 1000)
        status_style = {
            "healthy": "green",
            "unhealthy": "red",
            "unreachable": "yellow",
        }.get(health, "yellow")
        table.add_row(
            svc["name"],
            f"[{status_style}]{health}[/{status_style}]",
            f"{latency}ms",
        )

    console.print(table)

    # Docker containers
    console.print("\n[cyan]Docker Containers:[/cyan]")
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=evershade", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True,
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                parts = line.split("\t")
                console.print(f"  [green]{parts[0]}[/green] — {parts[1] if len(parts) > 1 else ''}")
        else:
            console.print("  [yellow]No Evershade containers running[/yellow]")
    except Exception as e:
        console.print(f"  [red]Error: {e}[/red]")

    # Disk usage
    console.print("\n[cyan]Disk Usage:[/cyan]")
    try:
        result = subprocess.run(
            ["docker", "system", "df", "--format", "{{.Type}}\t{{.Size}}"],
            capture_output=True, text=True,
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                console.print(f"  {line}")
    except Exception as e:
        console.print(f"  [red]Error: {e}[/red]")


# ─── Version ─────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def version(base_url: str | None):
    """Check versions and compatibility."""
    console.print(Panel("[bold]Version Information[/bold]"))

    # CLI version
    console.print("[cyan]CLI Version:[/cyan] [green]2.0.0[/green]")

    # Docker version
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[cyan]Docker:[/cyan] {result.stdout.strip()}")
    except FileNotFoundError:
        console.print("[cyan]Docker:[/cyan] [red]Not found[/red]")

    # Docker Compose version
    try:
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[cyan]Docker Compose:[/cyan] {result.stdout.strip()}")
    except Exception:
        pass

    # Service versions
    base = (base_url or cli_config.base_url).rstrip("/")
    console.print("\n[cyan]Service Versions:[/cyan]")
    for svc in services_list[:8]:  # API services only
        try:
            response = httpx.get(f"http://localhost:{svc['port']}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                ver = data.get("version", "unknown")
                console.print(f"  [green]{svc['name']}[/green]: {ver}")
            else:
                console.print(f"  [yellow]{svc['name']}[/green]: unreachable")
        except Exception:
            console.print(f"  [yellow]{svc['name']}[/green]: unreachable")


# ─── Integrations ────────────────────────────────────────────────────────────

@cli.command()
def integrations():
    """List configured integrations."""
    console.print(Panel("[bold]Configured Integrations[/bold]"))

    integrations = [
        ("OpenTelemetry", "Telemetry", "All services", "Built-in"),
        ("Prometheus", "Monitoring", "docker-compose.yml", "Required"),
        ("Grafana", "Dashboards", "docker-compose.yml", "Required"),
        ("Opik", "AI Observability", "Shrewd", "Optional"),
        ("Langfuse", "AI Observability", "Shrewd", "Optional"),
        ("Loki", "Log Aggregation", "Monitoring", "Optional"),
        ("Tempo", "Distributed Tracing", "Monitoring", "Optional"),
        ("Browser Use", "Browser Backend", "Trapper", "Optional"),
        ("Playwright MCP", "Browser Backend", "Trapper", "Optional"),
    ]

    table = Table(title="Integrations")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Service", style="yellow")
    table.add_column("Status", style="dim")

    for name, itype, service, status in integrations:
        status_style = "green" if status == "Required" or status == "Built-in" else "yellow"
        table.add_row(
            name,
            itype,
            service,
            f"[{status_style}]{status}[/{status_style}]",
        )

    console.print(table)

    # Check running integrations
    console.print("\n[cyan]Running Integrations:[/cyan]")
    checks = [
        ("Prometheus", "http://localhost:9090"),
        ("Grafana", "http://localhost:3000/api/health"),
    ]
    for name, url in checks:
        health = check_health(url)
        status_style = {"healthy": "green", "unhealthy": "red", "unreachable": "yellow"}.get(health, "yellow")
        console.print(f"  [{status_style}]{name}[/{status_style}]: {health}")


# ─── Workflows ───────────────────────────────────────────────────────────────

@cli.group()
def workflows():
    """Workflow management via Greenie."""
    pass


@workflows.command(name="list")
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def list_workflows(base_url: str | None):
    """List all workflows."""
    greenie_url = base_url or cli_config.greenie_url
    data = api_get("/api/workflows", greenie_url)
    if not data or "workflows" not in data:
        console.print("[yellow]No workflows found or Greenie is unreachable.[/yellow]")
        return

    table = Table(title="Workflows")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Runs", style="yellow")
    table.add_column("Last Run", style="dim")

    for wf in data["workflows"]:
        status = wf.get("status", "unknown")
        status_style = {"active": "green", "disabled": "red", "paused": "yellow"}.get(status, "yellow")
        table.add_row(
            wf.get("name", "Unknown"),
            f"[{status_style}]{status}[/{status_style}]",
            str(wf.get("runs", 0)),
            wf.get("lastRun", "—")[:19] if wf.get("lastRun") else "—",
        )

    console.print(table)


@workflows.command()
@click.argument("workflow-id")
@click.option("--base-url", default=None, help="Base URL for Greenie API")
def run(workflow_id: str, base_url: str | None):
    """Execute a workflow."""
    greenie_url = base_url or cli_config.greenie_url
    try:
        response = httpx.post(
            f"{greenie_url}/api/workflows/{workflow_id}/execute",
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        run_id = result.get("run_id", "unknown")
        console.print(f"[green]✓[/green] Workflow started — run_id: {run_id}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


# ─── Knowledge ───────────────────────────────────────────────────────────────

@cli.group()
def knowledge():
    """Knowledge base management via Gobber."""
    pass


@knowledge.command()
@click.argument("query")
@click.option("--base-url", default=None, help="Base URL for Gobber API")
def search(query: str, base_url: str | None):
    """Search the knowledge base."""
    gobber_url = base_url or os.getenv("GOBBER_URL", "http://localhost:8085")
    try:
        response = httpx.get(
            f"{gobber_url}/api/embeddings/search",
            params={"q": query},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return

        console.print(f"\n[cyan]Search Results ({len(results)}):[/cyan]")
        for i, result in enumerate(results[:10], 1):
            title = result.get("title", "Untitled")
            content = result.get("content", "")[:100]
            score = result.get("score", "")
            console.print(f"\n  [green]{i}. {title}[/green] (score: {score})")
            console.print(f"  {content}...")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


# ─── Models ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--base-url", default=None, help="Base URL for Shrewd API")
def models(base_url: str | None):
    """List configured model providers and models."""
    shrewd_url = base_url or os.getenv("SHREWD_URL", "http://localhost:8089")

    # Providers
    data = api_get("/api/providers", shrewd_url)
    if data and "providers" in data:
        table = Table(title="Model Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Base URL", style="green")
        table.add_column("Models", style="yellow")
        table.add_column("Status", style="dim")

        for provider in data["providers"]:
            status = "enabled" if provider.get("enabled") else "disabled"
            status_style = "green" if status == "enabled" else "yellow"
            table.add_row(
                provider.get("name", "Unknown"),
                provider.get("baseUrl", "—"),
                str(len(provider.get("models", []))),
                f"[{status_style}]{status}[/{status_style}]",
            )
        console.print(table)

    # Models
    data = api_get("/api/models", shrewd_url)
    if data and "models" in data:
        table = Table(title="Models")
        table.add_column("Name", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Capabilities", style="yellow")

        for model in data["models"]:
            caps = ", ".join(model.get("capabilities", [])[:3])
            table.add_row(
                model.get("name", "Unknown"),
                model.get("provider", "—"),
                caps,
            )
        console.print(table)
    else:
        console.print("[yellow]Shrewd is unreachable.[/yellow]")


if __name__ == "__main__":
    cli()
