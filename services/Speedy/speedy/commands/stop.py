"""Stop command — stop Evershade services."""

import click

from speedy.docker import check_docker_available, docker_compose_down, find_compose_file
from speedy.utils import print_error, print_info, print_success


@click.command(help="Stop Evershade services.")
def stop():
    """Stop all Evershade services."""
    if not check_docker_available():
        print_error("Docker is not available.")
        return

    compose = find_compose_file()
    if compose is None:
        print_error(
            "docker-compose.yml not found. Run from the Evershade project root."
        )
        return

    print_info("Stopping services...")
    if docker_compose_down(project_dir=compose.parent):
        print_success("Services stopped.")
    else:
        print_error("Failed to stop services.")
