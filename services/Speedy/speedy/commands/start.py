"""Start command — launch Evershade services."""

import click

from speedy.docker import check_docker_available, docker_compose_up, find_compose_file
from speedy.utils import print_error, print_info, print_success


@click.command(help="Start Evershade services.")
@click.option(
    "--profile",
    "profiles",
    multiple=True,
    help="Docker Compose profiles to enable (e.g., full, monitoring).",
)
def start(profiles):
    """Start Evershade services with Docker Compose."""
    if not check_docker_available():
        print_error("Docker is not available.")
        return

    compose = find_compose_file()
    if compose is None:
        print_error("docker-compose.yml not found. Run from the Evershade project root.")
        return

    profile_list = list(profiles) if profiles else ["standard"]
    print_info(f"Starting services with profiles: {', '.join(profile_list)}")

    if docker_compose_up(profiles=profile_list, project_dir=compose.parent):
        print_success("Services started successfully.")
    else:
        print_error("Failed to start services. Check the error output above.")
