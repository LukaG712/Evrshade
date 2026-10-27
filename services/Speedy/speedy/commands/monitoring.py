"""Monitoring command — check monitoring stack health."""

import click

from speedy.client import ServiceClient
from speedy.config import MONITORING_SERVICES
from speedy.utils import console, create_status_table, print_info


@click.group(help="Monitoring stack diagnostics.")
def monitoring():
    """Monitoring stack commands."""


@monitoring.command(name="status", help="Check monitoring stack health.")
def monitoring_status():
    """Check health of Prometheus, Grafana, cAdvisor, and node-exporter."""
    table = create_status_table("Monitoring Stack Status")

    for name, info in MONITORING_SERVICES.items():
        client = ServiceClient(f"http://localhost:{info['port']}", timeout=5.0)
        result = client.check_health()

        healthy = result["healthy"]
        status_str = "●" if healthy else "○"
        details = "ok" if healthy else "unreachable"
        table.add_row(name, status_str, "-", details)

    console.print(table)


@monitoring.command(name="url", help="Print monitoring dashboard URLs.")
def monitoring_url():
    """Print URLs for monitoring dashboards."""
    print_info("Monitoring URLs:")
    console.print("  Prometheus: http://localhost:9090")
    console.print("  Grafana:    http://localhost:3000")
    console.print("  cAdvisor:   http://localhost:8081")
