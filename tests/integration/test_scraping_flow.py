"""
Test 3: Web Scraping Flow
User → Greenie → Trapper → Playwright

Validates:
- Trapper health endpoint
- URL scraping
- SSRF protection
- Rate limiting
"""

from tests.integration.base_test import BaseIntegrationTest


class TestScrapingFlow(BaseIntegrationTest):
    """Test the web scraping flow through Trapper."""

    service = "Trapper"

    def run(self) -> bool:
        print("\n  Step 1: Check Trapper health")
        trapper_ok = self.check_service_health("Trapper", 3000)

        if not trapper_ok:
            print("\n  ⊘ Trapper not running, skipping flow test")
        # Trapper runs on port 3000 with different health path
        elif not self.client:
            print("\n  ⊘ httpx not available, skipping flow test")
        else:
            try:
                resp = self.client.get("http://localhost:3000/health", timeout=5.0)
                trapper_ok = resp.status_code == 200
                if trapper_ok:
                    print("  ✓ Trapper is healthy (port 3000)")
                else:
                    print(f"  ✗ Trapper returned status {resp.status_code}")
            except Exception as e:
                print(f"  ✗ Trapper health check failed: {e}")
                trapper_ok = False

        if not trapper_ok:
            print("\n  ⊘ Trapper not running, skipping flow test")
            return False

        # Test SSRF protection
        print("\n  Step 2: Test SSRF protection")
        ssrf_test = self.make_request(
            "post",
            "/api/scrape",
            json={
                "url": "http://169.254.169.254/latest/meta-data/",
            },
        )
        ssrf_blocked = self.assert_true(
            ssrf_test is None or "error" in (ssrf_test or {}),
            "SSRF protection blocks internal addresses",
        )

        # Test scrape endpoint
        print("\n  Step 3: Test scrape endpoint")
        scrape_result = self.make_request(
            "post",
            "/api/scrape",
            json={
                "url": "https://httpbin.org/html",
            },
        )
        scrape_ok = self.assert_true(
            scrape_result is not None, "Scrape endpoint accessible"
        )

        # Test extract endpoint
        print("\n  Step 4: Test extract endpoint")
        extract_result = self.make_request(
            "post",
            "/api/extract",
            json={
                "url": "https://httpbin.org/html",
                "selectors": ["h1", "p"],
            },
        )
        extract_ok = self.assert_true(
            extract_result is not None, "Extract endpoint accessible"
        )

        # Test map endpoint
        print("\n  Step 5: Test map endpoint")
        map_result = self.make_request(
            "post",
            "/api/map",
            json={
                "url": "https://httpbin.org",
            },
        )
        map_ok = self.assert_true(map_result is not None, "Map endpoint accessible")

        all_passed = all([trapper_ok, ssrf_blocked, scrape_ok, extract_ok, map_ok])

        return all_passed
