"""Service registry for discovery and health aggregation.

Provides a central registry where services register on startup and
report their status. Other services can query the registry to discover
available services and their endpoints.

Usage:
    from evershade.registry import ServiceRegistry, register_service_routes

    # Server side (Greenie acts as registry)
    registry = ServiceRegistry()
    register_service_routes(app, registry)

    # Client side
    from evershade.registry import ServiceDiscoveryClient
    client = ServiceDiscoveryClient(registry_url="http://Greenie:8080")
    await client.register("Slinker", "http://Slinker:8000", "2.0.0")
    services = await client.list_services()
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

logger = logging.getLogger("evershade.registry")


class ServiceStatus(str, Enum):
    """Service health status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class ServiceInfo:
    """Information about a registered service."""

    name: str
    url: str
    version: str
    status: ServiceStatus = ServiceStatus.HEALTHY
    capabilities: list[str] = field(default_factory=list)
    registered_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "url": self.url,
            "version": self.version,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "registeredAt": self.registered_at,
            "lastHeartbeat": self.last_heartbeat,
        }


class ServiceRegistry:
    """In-memory service registry.

    Stores service information and provides lookup by name.
    In production, this would be backed by Redis or a database.
    """

    def __init__(self):
        self._services: dict[str, ServiceInfo] = {}

    def register(self, name: str, url: str, version: str, capabilities: list[str] | None = None) -> ServiceInfo:
        """Register or update a service."""
        info = ServiceInfo(
            name=name,
            url=url,
            version=version,
            capabilities=capabilities or [],
        )
        self._services[name] = info
        logger.info("Registered service: %s at %s", name, url)
        return info

    def deregister(self, name: str) -> bool:
        """Remove a service from the registry."""
        if name in self._services:
            del self._services[name]
            logger.info("Deregistered service: %s", name)
            return True
        return False

    def get(self, name: str) -> ServiceInfo | None:
        """Get service info by name."""
        return self._services.get(name)

    def list_services(self, status: ServiceStatus | None = None) -> list[ServiceInfo]:
        """List all registered services, optionally filtered by status."""
        services = list(self._services.values())
        if status:
            services = [s for s in services if s.status == status]
        return services

    def update_heartbeat(self, name: str) -> bool:
        """Update the heartbeat timestamp for a service."""
        if name in self._services:
            self._services[name].last_heartbeat = time.time()
            return True
        return False

    def update_status(self, name: str, status: ServiceStatus) -> bool:
        """Update the status of a service."""
        if name in self._services:
            self._services[name].status = status
            return True
        return False

    def all_healthy(self) -> bool:
        """Check if all registered services are healthy."""
        return all(s.status == ServiceStatus.HEALTHY for s in self._services.values())

    def summary(self) -> dict[str, Any]:
        """Return a summary of the registry."""
        total = len(self._services)
        healthy = sum(1 for s in self._services.values() if s.status == ServiceStatus.HEALTHY)
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": total - healthy,
            "services": [s.to_dict() for s in self._services.values()],
        }


def register_service_routes(app, registry: ServiceRegistry) -> None:
    """Register service registry endpoints on a FastAPI app.

    Args:
        app: FastAPI application instance.
        registry: ServiceRegistry instance.
    """
    router = APIRouter(prefix="/api/registry", tags=["registry"])

    @router.get("/")
    async def list_services():
        """List all registered services."""
        return registry.summary()

    @router.get("/{name}")
    async def get_service(name: str):
        """Get a specific service by name."""
        info = registry.get(name)
        if not info:
            raise HTTPException(status_code=404, detail=f"Service '{name}' not found")
        return info.to_dict()

    @router.post("/{name}")
    async def register_service(name: str, data: dict[str, Any]):
        """Register or update a service."""
        url = data.get("url", "")
        version = data.get("version", "unknown")
        capabilities = data.get("capabilities", [])
        info = registry.register(name, url, version, capabilities)
        return info.to_dict()

    @router.delete("/{name}")
    async def deregister_service(name: str):
        """Remove a service from the registry."""
        if not registry.deregister(name):
            raise HTTPException(status_code=404, detail=f"Service '{name}' not found")
        return {"status": "ok", "message": f"Service '{name}' deregistered"}

    @router.post("/{name}/heartbeat")
    async def heartbeat(name: str):
        """Update heartbeat for a service."""
        if not registry.update_heartbeat(name):
            raise HTTPException(status_code=404, detail=f"Service '{name}' not found")
        return {"status": "ok"}

    @router.post("/{name}/status")
    async def update_status(name: str, data: dict[str, str]):
        """Update the status of a service."""
        status = ServiceStatus(data.get("status", "healthy"))
        if not registry.update_status(name, status):
            raise HTTPException(status_code=404, detail=f"Service '{name}' not found")
        return {"status": "ok"}

    app.include_router(router)


class ServiceDiscoveryClient:
    """Client for interacting with the service registry.

    Usage:
        client = ServiceDiscoveryClient(registry_url="http://Greenie:8080")
        await client.register("Slinker", "http://Slinker:8000", "2.0.0")
    """

    def __init__(self, registry_url: str, timeout: float = 10.0):
        self.registry_url = registry_url.rstrip("/")
        self.timeout = timeout

    async def register(
        self,
        name: str,
        url: str,
        version: str,
        capabilities: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register this service with the registry."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.registry_url}/api/registry/{name}",
                json={
                    "url": url,
                    "version": version,
                    "capabilities": capabilities or [],
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def deregister(self, name: str) -> dict[str, Any]:
        """Remove this service from the registry."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.delete(f"{self.registry_url}/api/registry/{name}")
            resp.raise_for_status()
            return resp.json()

    async def heartbeat(self, name: str) -> dict[str, Any]:
        """Send a heartbeat to the registry."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.registry_url}/api/registry/{name}/heartbeat")
            resp.raise_for_status()
            return resp.json()

    async def get_service(self, name: str) -> dict[str, Any] | None:
        """Get service info by name."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.registry_url}/api/registry/{name}")
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise

    async def list_services(self) -> dict[str, Any]:
        """List all registered services."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.registry_url}/api/registry/")
            resp.raise_for_status()
            return resp.json()
