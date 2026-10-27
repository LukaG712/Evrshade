"""Backup command — backup Evershade databases."""

import subprocess
from datetime import UTC, datetime
from pathlib import Path

import click

from speedy.docker import check_docker_available, find_compose_file
from speedy.utils import print_error, print_info, print_success


@click.command(help="Backup all Evershade service databases.")
@click.option("--path", "-p", "backup_dir", help="Directory to store backups.")
def backup(backup_dir):
    """Backup all SQLite databases from Docker volumes."""
    if not check_docker_available():
        print_error("Docker is not available.")
        return

    compose = find_compose_file()
    if compose is None:
        print_error("docker-compose.yml not found.")
        return

    if not backup_dir:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        backup_dir = f"backups/{timestamp}"

    dest = Path(backup_dir)
    dest.mkdir(parents=True, exist_ok=True)

    # Services with SQLite databases
    services_dbs = {
        "Greenie": "greenie_data",
        "Slinker": "slinker_logs",
        "Gobber": "gobber_data",
        "Sneaker": "sneaker_data",
        "Hider": "hider_data",
        "Poltergeist": "poltergeist_data",
    }

    backed_up = 0
    for service in services_dbs:
        print_info(f"Backing up {service}...")
        # Use docker cp to extract database files
        container_name = f"evershade-{service.lower()}-1"
        db_path = f"/app/data/{service.lower()}.db"

        result = subprocess.run(
            [
                "docker",
                "cp",
                f"{container_name}:{db_path}",
                str(dest / f"{service.lower()}.db"),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print_success(f"Backed up {service}")
            backed_up += 1
        else:
            # Container might not be running
            print_error(f"Could not backup {service}: container may not be running")

    print_info(f"Backup complete: {backed_up}/{len(services_dbs)} services backed up to {dest}")
