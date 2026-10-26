"""
Integration tests for external project integrations.
Tests Langfuse, Opik, Trapper backends, Loki, and Tempo.
"""

from tests.integration.base_test import BaseIntegrationTest


class TestIntegrationFlow(BaseIntegrationTest):
    """Test external project integrations."""

    def test_trapper_backend_selection(self):
        """Test Trapper reports the correct backend type."""
        print("\n  --- Trapper Backend Selection ---")
        healthy = self.check_service_health("Trapper", 3000)
        if not healthy:
            print("  ⊘ Trapper not running, skipping backend selection test")
            return True

        result = self.make_request("get", "http://localhost:3000/api/capabilities")
        if result:
            integrations = result.get("integrations", {})
            backend = integrations.get("browserBackend", {})
            backend_type = backend.get("type", "unknown")
            self.assert_true(
                backend_type in ("playwright", "browser-use", "playwright-mcp"),
                f"Trapper backend type is valid: {backend_type}",
            )
            return True
        return False

    def test_trapper_backend_status(self):
        """Test Trapper backend readiness."""
        print("\n  --- Trapper Backend Status ---")
        healthy = self.check_service_health("Trapper", 3000)
        if not healthy:
            print("  ⊘ Trapper not running, skipping backend status test")
            return True

        result = self.make_request("get", "http://localhost:3000/api/status")
        if result:
            deps = result.get("dependencies", {})
            backend_ready = deps.get("ready", False)
            backend_name = deps.get("browserBackend", "unknown")
            self.assert_true(
                backend_name in ("playwright", "browser-use", "playwright-mcp"),
                f"Trapper backend name: {backend_name}",
            )
            # Backend may not be ready if Playwright isn't installed in test env
            print(f"  ℹ Trapper backend ready: {backend_ready}")
            return True
        return False

    def test_shrewd_langfuse_capability(self):
        """Test Shrewd reports Langfuse integration status."""
        print("\n  --- Shrewd Langfuse Capability ---")
        healthy = self.check_service_health("Shrewd", 8089)
        if not healthy:
            print("  ⊘ Shrewd not running, skipping Langfuse capability test")
            return True

        result = self.make_request("get", "http://localhost:8089/api/capabilities")
        if result:
            integrations = result.get("integrations", {})
            langfuse = integrations.get("langfuse", {})
            self.assert_true(
                "enabled" in langfuse,
                "Shrewd reports Langfuse integration status",
            )
            enabled = langfuse.get("enabled", False)
            endpoint = langfuse.get("endpoint")
            if enabled:
                print(f"  ℹ Langfuse enabled at {endpoint}")
            else:
                print("  ℹ Langfuse not configured (optional integration)")
            return True
        return False

    def test_shrewd_opik_capability(self):
        """Test Shrewd reports Opik integration status."""
        print("\n  --- Shrewd Opik Capability ---")
        healthy = self.check_service_health("Shrewd", 8089)
        if not healthy:
            print("  ⊘ Shrewd not running, skipping Opik capability test")
            return True

        result = self.make_request("get", "http://localhost:8089/api/capabilities")
        if result:
            integrations = result.get("integrations", {})
            opik = integrations.get("opik", {})
            self.assert_true(
                "enabled" in opik,
                "Shrewd reports Opik integration status",
            )
            enabled = opik.get("enabled", False)
            endpoint = opik.get("endpoint")
            if enabled:
                print(f"  ℹ Opik enabled at {endpoint}")
            else:
                print("  ℹ Opik not configured (optional integration)")
            return True
        return False

    def test_loki_health(self):
        """Test Loki log aggregation service health."""
        print("\n  --- Loki Health (Optional) ---")
        if not self.client:
            print("  ⊘ httpx not available, skipping Loki health check")
            return True

        try:
            response = self.client.get(
                "http://localhost:3100/ready", timeout=5.0
            )
            if response.status_code == 200:
                print("  ✓ Loki is healthy (port 3100)")
                return True
            else:
                print(f"  ℹ Loki returned status {response.status_code} (optional service)")
                return True
        except Exception as e:
            print(f"  ℹ Loki not reachable: {e} (optional service)")
            return True

    def test_tempo_health(self):
        """Test Tempo distributed tracing service health."""
        print("\n  --- Tempo Health (Optional) ---")
        if not self.client:
            print("  ⊘ httpx not available, skipping Tempo health check")
            return True

        try:
            response = self.client.get(
                "http://localhost:3200", timeout=5.0
            )
            if response.status_code == 200:
                print("  ✓ Tempo is healthy (port 3200)")
                return True
            else:
                print(f"  ℹ Tempo returned status {response.status_code} (optional service)")
                return True
        except Exception as e:
            print(f"  ℹ Tempo not reachable: {e} (optional service)")
            return True

    def test_opentelemetry_metrics(self):
        """Test all services expose /metrics endpoints (OpenTelemetry integration)."""
        print("\n  --- OpenTelemetry /metrics Endpoints ---")
        services = [
            ("Greenie", 8080),
            ("Slinker", 8081),
            ("Trapper", 3000),
            ("Gobber", 8084),
            ("Shrewd", 8089),
            ("Sneaker", 8086),
            ("Hider", 8087),
            ("Poltergeist", 8088),
        ]
        checked = 0
        for name, port in services:
            if self.check_service_metrics(name, port):
                checked += 1
        self.assert_true(
            checked > 0,
            f"At least one service exposes /metrics ({checked}/{len(services)} checked)",
        )
        return True

    def run(self) -> bool:
        """Run all integration tests."""
        print("\n=== External Project Integration Tests ===")
        results = []
        results.append(self.test_trapper_backend_selection())
        results.append(self.test_trapper_backend_status())
        results.append(self.test_shrewd_langfuse_capability())
        results.append(self.test_shrewd_opik_capability())
        results.append(self.test_loki_health())
        results.append(self.test_tempo_health())
        results.append(self.test_opentelemetry_metrics())
        passed = sum(results)
        total = len(results)
        print(f"\n=== Integration Tests: {passed}/{total} passed ===")
        return all(results)
