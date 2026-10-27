"""Logs command — view service logs."""

import click

from speedy.docker import check_docker_available, docker_compose_logs, find_compose_file
from speedy.utils import console, print_error


@click.command(help="View logs for a service.")
@click.argument("service", required=False)
@click.option("--tail", "-n", default=100, help="Number of lines to show.")
def logs(service, tail):
    """View logs for a specific service or all services."""
    if not check_docker_available():
        print_error("Docker is not available.")
        return

    compose = find_compose_file()
    if compose is None:
        print_error("docker-compose.yml not found.")
        return

    if service:
        output = docker_compose_logs(service, tail=tail, project_dir=compose.parent)
        if output:
            console.print(output)
    else:
        # Show logs for all core services
        services = [
            "Greenie",
            "Slinker",
            "Trapper-api",
            "Gobber",
            "Sneaker",
            "Hider",
            "Poltergeist",
            "Shrewd",
        ]
        for svc in services:
            output = docker_compose_logs(
                svc, tail=min(tail, 20), project_dir=compose.parent
            )
            if output:
                console.print(f"\n[bold cyan]=== {svc} ===[/]")
                console.print(output[:500])  # Limit output per service
