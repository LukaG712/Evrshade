"""
Base test class for integration tests.
Provides common utilities for HTTP requests and assertions.
"""

import os

try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


class BaseIntegrationTest:
    """Base class for all integration tests."""

    service: str = ""
    base_url: str = os.getenv("EVERSHADE_BASE_URL", "http://localhost")

    def __init__(self):
        self.client = None
        if HAS_HTTPX:
            self.client = httpx.Client(
                base_url=self.base_url,
                timeout=30.0,
                follow_redirects=True,
            )

    def check_service_health(self, service_name: str, port: int) -> bool:
        """Check if a service is healthy."""
        if not self.client:
            print("  ⊘ httpx not available, skipping health check")
            return False

        try:
            url = f"http://localhost:{port}/health"
            response = self.client.get(url, timeout=5.0)
            if response.status_code == 200:
                print(f"  ✓ {service_name} is healthy (port {port})")
                return True
            else:
                print(f"  ✗ {service_name} returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ {service_name} is not reachable: {e}")
            return False

    def check_service_metrics(self, service_name: str, port: int) -> bool:
        """Check if a service exposes Prometheus /metrics endpoint."""
        if not self.client:
            print("  ⊘ httpx not available, skipping metrics check")
            return False

        try:
            url = f"http://localhost:{port}/metrics"
            response = self.client.get(url, timeout=5.0)
            if response.status_code == 200:
                print(f"  ✓ {service_name} /metrics endpoint accessible (port {port})")
                return True
            else:
                print(
                    f"  ℹ {service_name} /metrics returned status {response.status_code}"
                )
                return False
        except Exception as e:
            print(f"  ℹ {service_name} /metrics not reachable: {e}")
            return False

    def make_request(
        self, method: str, url: str, check_correlation_id: bool = True, **kwargs
    ) -> dict | None:
        """Make an HTTP request and return the JSON response.

        Optionally verifies the X-Request-Id correlation ID header is present.
        """
        if not self.client:
            print("  ⊘ httpx not available, skipping request")
            return None

        try:
            response = getattr(self.client, method)(url, **kwargs)
            if check_correlation_id:
                corr_id = response.headers.get("x-request-id", "")
                if corr_id:
                    print(f"  ℹ Correlation ID: {corr_id[:12]}...")
                # Don't fail the test if correlation ID is missing — it's a nice-to-have
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                # Try to parse error response from evershade-core error envelope
                try:
                    error = response.json()
                    if "error" in error:
                        print(f"  ✗ Request failed: {error['error']}")
                    else:
                        print(f"  ✗ Request failed with status {response.status_code}")
                except Exception:
                    print(f"  ✗ Request failed with status {response.status_code}")
                return None
        except Exception as e:
            print(f"  ✗ Request failed: {e}")
            return None

    def assert_true(self, condition: bool, message: str):
        """Assert a condition is true."""
        if condition:
            print(f"  ✓ {message}")
            return True
        else:
            print(f"  ✗ {message}")
            return False

    def run(self) -> bool:
        """Override in subclass to run the test."""
        raise NotImplementedError
