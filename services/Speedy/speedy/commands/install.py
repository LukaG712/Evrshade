"""Install command — validate environment and prepare Evershade."""

import click

from speedy.docker import check_docker_available, find_compose_file
from speedy.utils import print_error, print_success, print_warning


@click.command(help="Validate environment and prepare Evershade for first use.")
@click.option(
    "--profile", "profiles", multiple=True, help="Docker Compose profiles to enable."
)
def install(profiles):
    """Validate the environment and prepare for installation."""
    # Check Docker
    if not check_docker_available():
        print_error(
            "Docker is not available. Install Docker Desktop or Docker Engine first."
        )
        return

    print_success("Docker is available")

    # Check compose file
    compose = find_compose_file()
    if compose is None:
        print_error(
            "docker-compose.yml not found. Run this command from the Evershade project root."
        )
        return

    print_success(f"Found docker-compose.yml at {compose}")

    # Check .env file
    env_file = compose.parent / ".env"
    if not env_file.exists():
        env_example = compose.parent / ".env.example"
        if env_example.exists():
            print_warning(
                ".env file not found. Copy .env.example to .env and configure your keys."
            )
        else:
            print_warning(
                "No .env or .env.example found. Create .env with required environment variables."
            )

    print_success(
        "Environment validation complete. Run 'evershade start' to launch services."
    )
