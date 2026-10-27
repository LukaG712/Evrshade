"""Slinker — Coding Agent Adapter Factory.

Selects and creates the appropriate adapter based on configuration.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from . import CodingAgentAdapter
from .subprocess_adapter import SubprocessAdapter

logger = logging.getLogger(__name__)


# Registry of available adapters
ADAPTER_REGISTRY: dict[str, Any] = {}


def register_adapter(name: str, adapter_class: type) -> None:
    """Register an adapter class by name."""
    ADAPTER_REGISTRY[name] = adapter_class


# Register built-in adapters
register_adapter("subprocess", SubprocessAdapter)

# Try to register Junie adapter (may not be available)
try:
    from .junie_adapter import JunieAdapter

    register_adapter("junie", JunieAdapter)
    logger.info("Junie adapter registered")
except ImportError:
    logger.warning("Junie adapter not available — Junie CLI not installed")


def create_adapter(
    adapter_name: str = "subprocess",
    config: dict[str, Any] | None = None,
) -> CodingAgentAdapter:
    """
    Create a coding agent adapter by name.

    Args:
        adapter_name: Name of the adapter ("junie", "subprocess", etc.)
        config: Optional configuration dictionary

    Returns:
        CodingAgentAdapter instance

    Raises:
        ValueError: If adapter name is not registered
    """
    adapter_class = ADAPTER_REGISTRY.get(adapter_name)
    if not adapter_class:
        available = ", ".join(ADAPTER_REGISTRY.keys())
        logger.warning(
            f"Adapter '{adapter_name}' not found, falling back to 'subprocess'. "
            f"Available: {available}"
        )
        adapter_class = ADAPTER_REGISTRY["subprocess"]

    # Merge default config
    merged_config = config or {}
    if adapter_name == "junie":
        merged_config.setdefault("junie_path", os.getenv("JUNIE_PATH", "junie"))
        merged_config.setdefault("junie_args", [])

    adapter = adapter_class(merged_config)
    logger.info(f"Created adapter: {adapter_name}")
    return adapter


def list_adapters() -> dict[str, dict[str, Any]]:
    """List all registered adapters with their status."""
    result = {}
    for name, cls in ADAPTER_REGISTRY.items():
        result[name] = {
            "name": name,
            "class": cls.__name__,
            "available": True,
        }
    return result
