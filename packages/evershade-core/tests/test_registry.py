"""Tests for evershade.registry — Service registry."""

from evershade.registry import (
    ServiceInfo,
    ServiceRegistry,
    ServiceStatus,
    register_service_routes,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestServiceRegistry:
    """Test in-memory service registry."""

    def test_register(self):
        registry = ServiceRegistry()
        info = registry.register("Greenie", "http://localhost:8080", "2.0.0")
        assert info.name == "Greenie"
        assert info.url == "http://localhost:8080"
        assert info.version == "2.0.0"
        assert info.status == ServiceStatus.HEALTHY

    def test_get(self):
        registry = ServiceRegistry()
        registry.register("Slinker", "http://localhost:8000", "2.0.0")
        info = registry.get("Slinker")
        assert info is not None
        assert info.name == "Slinker"

    def test_get_missing(self):
        registry = ServiceRegistry()
        assert registry.get("Missing") is None

    def test_deregister(self):
        registry = ServiceRegistry()
        registry.register("Greenie", "http://localhost:8080", "2.0.0")
        assert registry.deregister("Greenie") is True
        assert registry.get("Greenie") is None

    def test_deregister_missing(self):
        registry = ServiceRegistry()
        assert registry.deregister("Missing") is False

    def test_list_services(self):
        registry = ServiceRegistry()
        registry.register("Greenie", "http://localhost:8080", "2.0.0")
        registry.register("Slinker", "http://localhost:8000", "2.0.0")
        services = registry.list_services()
        assert len(services) == 2

    def test_list_services_filtered(self):
        registry = ServiceRegistry()
        registry.register("Greenie", "http://localhost:8080", "2.0.0")
        registry.update_status("Greenie", ServiceStatus.UNHEALTHY)
        registry.register("Slinker", "http://localhost:8000", "2.0.0")
        healthy = registry.list_services(status=ServiceStatus.HEALTHY)
        assert len(healthy) == 1
        assert healthy[0].name == "Slinker"

    def test_update_heartbeat(self):
        registry = ServiceRegistry()
        registry.register("Greenie", "http://localhost:8080", "2.0.0")
        assert registry.update_heartbeat("Greenie") is True
        assert registry.update_heartbeat("Missing") is False

    def test_update_status(self):
        registry = ServiceRegistry()
        registry.register("Greenie", "http://localhost:8080", "2.0.0")
        registry.update_status("Greenie", ServiceStatus.UNHEALTHY)
        info = registry.get("Greenie")
        assert info.status == ServiceStatus.UNHEALTHY

    def test_all_healthy(self):
        registry = ServiceRegistry()
        registry.register("Greenie", "http://localhost:8080", "2.0.0")
        assert registry.all_healthy() is True
        registry.update_status("Greenie", ServiceStatus.UNHEALTHY)
        assert registry.all_healthy() is False

    def test_summary(self):
        registry = ServiceRegistry()
        registry.register("Greenie", "http://localhost:8080", "2.0.0")
        registry.register("Slinker", "http://localhost:8000", "2.0.0")
        summary = registry.summary()
        assert summary["total"] == 2
        assert summary["healthy"] == 2
        assert len(summary["services"]) == 2

    def test_capabilities(self):
        registry = ServiceRegistry()
        registry.register(
            "Greenie", "http://localhost:8080", "2.0.0", capabilities=["agents", "chat"]
        )
        info = registry.get("Greenie")
        assert "agents" in info.capabilities


class TestServiceInfo:
    """Test ServiceInfo dataclass."""

    def test_to_dict(self):
        info = ServiceInfo(name="Greenie", url="http://localhost:8080", version="2.0.0")
        d = info.to_dict()
        assert d["name"] == "Greenie"
        assert d["status"] == "healthy"
        assert "registeredAt" in d


class TestRegistryRoutes:
    """Test registry API endpoints."""

    def setup_app(self):
        self.registry = ServiceRegistry()
        app = FastAPI()
        register_service_routes(app, self.registry)
        return app

    def test_list_empty(self):
        app = self.setup_app()
        with TestClient(app) as client:
            resp = client.get("/api/registry/")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] == 0

    def test_register_via_api(self):
        app = self.setup_app()
        with TestClient(app) as client:
            resp = client.post(
                "/api/registry/Greenie",
                json={
                    "url": "http://localhost:8080",
                    "version": "2.0.0",
                    "capabilities": ["agents"],
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["name"] == "Greenie"

    def test_get_service(self):
        app = self.setup_app()
        with TestClient(app) as client:
            client.post(
                "/api/registry/Greenie",
                json={
                    "url": "http://localhost:8080",
                    "version": "2.0.0",
                },
            )
            resp = client.get("/api/registry/Greenie")
            assert resp.status_code == 200
            assert resp.json()["name"] == "Greenie"

    def test_get_missing_service(self):
        app = self.setup_app()
        with TestClient(app) as client:
            resp = client.get("/api/registry/Missing")
            assert resp.status_code == 404

    def test_deregister_via_api(self):
        app = self.setup_app()
        with TestClient(app) as client:
            client.post(
                "/api/registry/Greenie",
                json={
                    "url": "http://localhost:8080",
                    "version": "2.0.0",
                },
            )
            resp = client.delete("/api/registry/Greenie")
            assert resp.status_code == 200

    def test_heartbeat(self):
        app = self.setup_app()
        with TestClient(app) as client:
            client.post(
                "/api/registry/Greenie",
                json={
                    "url": "http://localhost:8080",
                    "version": "2.0.0",
                },
            )
            resp = client.post("/api/registry/Greenie/heartbeat")
            assert resp.status_code == 200

    def test_update_status(self):
        app = self.setup_app()
        with TestClient(app) as client:
            client.post(
                "/api/registry/Greenie",
                json={
                    "url": "http://localhost:8080",
                    "version": "2.0.0",
                },
            )
            resp = client.post(
                "/api/registry/Greenie/status", json={"status": "unhealthy"}
            )
            assert resp.status_code == 200
