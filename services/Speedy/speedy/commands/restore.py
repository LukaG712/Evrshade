"""Restore command — restore Evershade databases from backup."""

import subprocess
from pathlib import Path

import click

from speedy.docker import check_docker_available
from speedy.utils import print_error, print_info, print_success


@click.command(help="Restore Evershade databases from backup.")
@click.argument("backup_dir", type=click.Path(exists=True, file_okay=False))
def restore(backup_dir):
    """Restore databases from a backup directory."""
    if not check_docker_available():
        print_error("Docker is not available.")
        return

    src = Path(backup_dir)
    if not src.is_dir():
        print_error(f"Not a directory: {backup_dir}")
        return

    # Find database files
    db_files = list(src.glob("*.db"))
    if not db_files:
        print_error(f"No .db files found in {backup_dir}")
        return

    restored = 0
    for db_file in db_files:
        service = db_file.stem
        container_name = f"evershade-{service}-1"
        db_path = f"/app/data/{service}.db"

        print_info(f"Restoring {service} from {db_file.name}...")

        # Stop the container first
        subprocess.run(["docker", "stop", container_name], capture_output=True)

        # Remove existing db in container
        subprocess.run(
            ["docker", "exec", container_name, "rm", "-f", db_path],
            capture_output=True,
        )

        # Copy backup into container
        result = subprocess.run(
            ["docker", "cp", str(db_file), f"{container_name}:{db_path}"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Restart the container
            subprocess.run(["docker", "start", container_name], capture_output=True)
            print_success(f"Restored {service}")
            restored += 1
        else:
            print_error(f"Failed to restore {service}: {result.stderr.strip()}")

    print_info(f"Restore complete: {restored}/{len(db_files)} services restored.")
