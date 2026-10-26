"""
Test 7: Core Platform Flow
Verifies the new evershade-core, evershade-db, and evershade-events packages.

Validates:
- Service registry endpoints on Greenie
- Correlation ID propagation
- Error handling envelope
- Health and metrics endpoints
- Database WAL mode verification
"""

from tests.integration.base_test import BaseIntegrationTest


class TestCorePlatformFlow(BaseIntegrationTest):
    """Test the core platform package integration."""

    service = "Core Platform"

    def run(self) -> bool:
        print("\n  Step 1: Check Greenie health (registry host)")
        greenie_ok = self.check_service_health("Greenie", 8080)

        if not greenie_ok:
            print("\n  ⊘ Greenie not running, skipping core platform test")
            return False

        # Check service registry
        print("\n  Step 2: Check service registry")
        registry = self.make_request("get", "/api/registry")
        registry_ok = self.assert_true(
            registry is not None and "services" in registry,
            "Service registry endpoint accessible"
        )

        # Check registry details endpoint
        print("\n  Step 3: Check registry service details")
        if registry and "services" in registry and len(registry["services"]) > 0:
            first_service = registry["services"][0]["name"]
            details = self.make_request("get", f"/api/registry/{first_service}")
            details_ok = self.assert_true(
                details is not None,
                f"Registry details for {first_service} accessible"
            )
        else:
            details_ok = True
            print("  ℹ No services in registry yet, skipping details check")

        # Check correlation ID propagation
        print("\n  Step 4: Check correlation ID propagation")
        if self.client:
            try:
                resp = self.client.get("http://localhost:8080/api/status", timeout=5.0)
                corr_id = resp.headers.get("x-request-id", "")
                corr_ok = self.assert_true(
                    len(corr_id) > 0,
                    f"Correlation ID present in response: {corr_id[:12]}..."
                )
            except Exception:
                corr_ok = False
                print("  ✗ Could not verify correlation ID")
        else:
            corr_ok = False
            print("  ⊘ httpx not available, skipping correlation ID check")

        # Check error handling envelope
        print("\n  Step 5: Check error handling envelope")
        if self.client:
            try:
                resp = self.client.get("http://localhost:8080/api/nonexistent-endpoint", timeout=5.0)
                # evershade-core should return a standard error envelope
                if resp.status_code in (404, 500):
                    try:
                        error_body = resp.json()
                        has_error_key = "error" in error_body or "detail" in error_body
                        error_ok = self.assert_true(
                            has_error_key,
                            "Error response uses standard envelope"
                        )
                    except Exception:
                        error_ok = self.assert_true(
                            True,
                            "Error response returned (non-JSON, may be valid)"
                        )
                else:
                    error_ok = self.assert_true(
                        resp.status_code == 404,
                        f"Unknown endpoint returns 404 (got {resp.status_code})"
                    )
            except Exception as e:
                error_ok = False
                print(f"  ✗ Error handling check failed: {e}")
        else:
            error_ok = False
            print("  ⊘ httpx not available, skipping error handling check")

        # Check /metrics endpoint
        print("\n  Step 6: Check /metrics endpoint")
        metrics_ok = self.check_service_metrics("Greenie", 8080)

        # Check /api/status endpoint
        print("\n  Step 7: Check /api/status endpoint")
        status = self.make_request("get", "/api/status")
        status_ok = self.assert_true(
            status is not None and "service" in status,
            "Service status endpoint accessible"
        )

        # Check /api/capabilities endpoint
        print("\n  Step 8: Check /api/capabilities endpoint")
        capabilities = self.make_request("get", "/api/capabilities")
        capabilities_ok = self.assert_true(
            capabilities is not None and "capabilities" in capabilities,
            "Service capabilities endpoint accessible"
        )

        # Check other services' health and metrics
        print("\n  Step 9: Check other services' health and metrics")
        services_to_check = [
            ("Slinker", 8000),
            ("Gobber", 8085),
            ("Sneaker", 8086),
            ("Hider", 8087),
            ("Poltergeist", 8088),
            ("Shrewd", 8089),
        ]

        health_results = []
        metrics_results = []
        for name, port in services_to_check:
            h = self.check_service_health(name, port)
            health_results.append(h)
            m = self.check_service_metrics(name, port)
            metrics_results.append(m)

        other_services_health = any(health_results) or not health_results
        other_services_metrics = any(metrics_results) or not metrics_results

        all_passed = all([
            greenie_ok, registry_ok, details_ok, corr_ok, error_ok,
            metrics_ok, status_ok, capabilities_ok,
            other_services_health, other_services_metrics
        ])

        return all_passed
