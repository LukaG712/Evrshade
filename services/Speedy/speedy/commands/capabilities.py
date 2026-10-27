"""Capabilities command — query service capabilities."""

import click

from speedy.client import ServiceClient
from speedy.config import load_config
from speedy.utils import console, create_capabilities_table, feature_list


@click.command(help="Query and display capabilities of all Evershade services.")
@click.option("--url", "greenie_url", help="Override Greenie API URL.")
def capabilities(greenie_url):
    """Display capabilities of all services."""
    config = load_config(greenie_url=greenie_url)
    services = config["services"]

    table = create_capabilities_table("Evershade Service Capabilities")

    for name, info in services.items():
        client = ServiceClient(info["url"], info.get("api_key"), timeout=5.0)
        result = client.check_capabilities()

        if result["available"] and result["data"]:
            version = result["data"].get("version", "-")
            features = result["data"].get("features", [])
            table.add_row(name, version, feature_list(features))
        else:
            table.add_row(name, "-", "unreachable")

    console.print(table)
