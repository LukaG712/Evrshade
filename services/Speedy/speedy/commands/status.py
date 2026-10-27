"""Status command — check health of all Evershade services."""

import click

from speedy.client import ServiceClient
from speedy.config import load_config
from speedy.utils import console, create_status_table


@click.command(help="Check health status of all Evershade services.")
@click.option("--url", "greenie_url", help="Override Greenie API URL.")
def status(greenie_url):
    """Display health status of all services."""
    config = load_config(greenie_url=greenie_url)
    services = config["services"]

    table = create_status_table("Evershade Service Status")

    for name, info in services.items():
        client = ServiceClient(info["url"], info.get("api_key"))
        result = client.check_health()

        healthy = result["healthy"]
        version = ""
        details = ""

        if healthy and result["data"]:
            version = result["data"].get("version", "")
            svc_status = result["data"].get("status", "ok")
            details = f"status={svc_status}"
        elif not healthy:
            details = "unreachable"

        status_str = "●" if healthy else "○"
        table.add_row(name, status_str, version or "-", details)

    console.print(table)
