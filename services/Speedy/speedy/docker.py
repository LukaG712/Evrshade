"""Docker Compose operations for Speedy CLI.

Wraps docker compose commands for install, start, stop, and status.
"""

import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def find_compose_file() -> Path | None:
    """Find docker-compose.yml by walking up from cwd.

    Returns:
        Path to docker-compose.yml or None.
    """
    current = Path.cwd()
    for _ in range(10):
        compose_file = current / "docker-compose.yml"
        if compose_file.exists():
            return compose_file
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _run_compose(args: list[str], project_dir: Path | None = None) -> subprocess.CompletedProcess:
    """Run a docker compose command.

    Args:
        args: Arguments to pass to docker compose.
        project_dir: Optional project directory.

    Returns:
        CompletedProcess result.
    """
    cmd = ["docker", "compose"]
    if project_dir:
        cmd.extend(["-f", str(project_dir / "docker-compose.yml")])
    cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result
    except FileNotFoundError:
        print("Error: 'docker' command not found. Is Docker installed?")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: Docker Compose command timed out.")
        sys.exit(1)


def docker_compose_up(profiles: list[str] | None = None, project_dir: Path | None = None) -> bool:
    """Start services with docker compose up -d.

    Args:
        profiles: Optional list of Docker Compose profiles.
        project_dir: Optional project directory.

    Returns:
        True if successful.
    """
    args = ["up", "-d"]
    if profiles:
        for profile in profiles:
            args.extend(["--profile", profile])

    result = _run_compose(args, project_dir)
    if result.returncode == 0:
        return True
    else:
        print(f"Error: {result.stderr.strip()}")
        return False


def docker_compose_down(project_dir: Path | None = None) -> bool:
    """Stop services with docker compose down.

    Args:
        project_dir: Optional project directory.

    Returns:
        True if successful.
    """
    result = _run_compose(["down"], project_dir)
    if result.returncode == 0:
        return True
    else:
        print(f"Error: {result.stderr.strip()}")
        return False


def docker_compose_ps(project_dir: Path | None = None) -> list[dict] | None:
    """List running containers.

    Args:
        project_dir: Optional project directory.

    Returns:
        List of container info dicts or None on failure.
    """
    result = _run_compose(["ps", "--format", "json"], project_dir)
    if result.returncode == 0 and result.stdout.strip():
        import json

        try:
            containers = json.loads(result.stdout)
            if isinstance(containers, list):
                return containers
            elif isinstance(containers, dict):
                return [containers]
        except json.JSONDecodeError:
            # Fallback: parse text output
            return None
    return None


def docker_compose_logs(service: str, tail: int = 100, project_dir: Path | None = None) -> str | None:
    """Get logs for a service.

    Args:
        service: Service name.
        tail: Number of lines to retrieve.
        project_dir: Optional project directory.

    Returns:
        Log output or None on failure.
    """
    result = _run_compose(["logs", "--tail", str(tail), service], project_dir)
    if result.returncode == 0:
        return result.stdout
    else:
        print(f"Error getting logs: {result.stderr.strip()}")
        return None


def check_docker_available() -> bool:
    """Check if Docker is available.

    Returns:
        True if Docker is running.
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
