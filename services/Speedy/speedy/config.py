"""Configuration loading for Speedy CLI.

Reads .env files and resolves service URLs and API keys.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Known services and their default ports
SERVICES = {
    "Greenie": {"port": 8080, "api_key_env": "EVERSHADE_GREENIE_API_KEY"},
    "Slinker": {"port": 8000, "api_key_env": "EVERSHADE_SLINKER_API_KEY"},
    "Trapper": {"port": 3000, "api_key_env": "EVERSHADE_TRAPPER_API_KEY"},
    "Gobber": {"port": 8085, "api_key_env": "EVERSHADE_GOBBER_API_KEY"},
    "Sneaker": {"port": 8086, "api_key_env": "EVERSHADE_SNEAKER_API_KEY"},
    "Hider": {"port": 8087, "api_key_env": "EVERSHADE_HIDER_API_KEY"},
    "Poltergeist": {"port": 8088, "api_key_env": "EVERSHADE_POLTERGEIST_API_KEY"},
    "Shrewd": {"port": 8089, "api_key_env": "EVERSHADE_SHREWD_API_KEY"},
}

# Monitoring services
MONITORING_SERVICES = {
    "Prometheus": {"port": 9090},
    "Grafana": {"port": 3000},
    "cAdvisor": {"port": 8081},
    "node-exporter": {"port": 9100},
}


def find_env_file() -> Path | None:
    """Find .env file by walking up from cwd to project root."""
    current = Path.cwd()
    for _ in range(10):  # Max 10 levels up
        env_file = current / ".env"
        if env_file.exists():
            return env_file
        compose_file = current / "docker-compose.yml"
        if compose_file.exists():
            return env_file  # May not exist, but this is the project root
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_config(greenie_url: str | None = None) -> dict:
    """Load configuration from .env and environment variables.

    Args:
        greenie_url: Optional override for Greenie API URL.

    Returns:
        Dict with 'greenie_url', 'api_keys', and 'services'.
    """
    env_file = find_env_file()
    if env_file and env_file.exists():
        load_dotenv(str(env_file))

    # Resolve Greenie URL
    if greenie_url:
        base_url = greenie_url
    else:
        base_url = os.getenv(
            "EVERSHADE_PUBLIC_URL",
            os.getenv("GREENIE_URL", "http://localhost:8080"),
        )

    # Ensure trailing slash is removed
    base_url = base_url.rstrip("/")

    # Collect API keys
    api_keys = {}
    for name, info in SERVICES.items():
        key = os.getenv(info["api_key_env"])
        if key:
            api_keys[name] = key

    # Build service list with URLs
    services = {}
    for name, info in SERVICES.items():
        # Use internal Docker URLs if available, otherwise construct from Greenie base
        internal_url = os.getenv(f"EVERSHADE_{name.upper()}_URL")
        if internal_url:
            url = internal_url
        else:
            # For local development, assume services are on localhost
            url = f"http://localhost:{info['port']}"
        services[name] = {
            "url": url,
            "port": info["port"],
            "api_key": api_keys.get(name),
        }

    return {
        "greenie_url": base_url,
        "api_keys": api_keys,
        "services": services,
    }
