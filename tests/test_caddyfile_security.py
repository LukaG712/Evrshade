"""
Security tests for Caddyfile configuration.

Verifies:
- trusted_proxies is restricted to internal Docker ranges (CWE-942 fix)
- Security headers are present

Run with: pytest tests/test_caddyfile_security.py -v
"""

import os
import re
import unittest

# Resolve the project root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CADDYFILE_PATH = os.path.join(_PROJECT_ROOT, "Caddyfile")


class TestTrustedProxies(unittest.TestCase):
    """Verify trusted_proxies is restricted to internal ranges (CWE-942 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_CADDYFILE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_no_trust_all_proxies(self):
        """
        Caddyfile must NOT trust all proxies (0.0.0.0/0).
        This was the CWE-942 vulnerability — IP spoofing via X-Forwarded-For.
        """
        self.assertNotIn(
            "0.0.0.0/0",
            self.content,
            "Caddyfile must not trust all proxies (0.0.0.0/0) — restrict to internal ranges",
        )

    def test_trusted_proxy_172_range(self):
        """Should trust 172.16.0.0/12 (Docker default bridge range)."""
        self.assertIn(
            "172.16.0.0/12",
            self.content,
            "Caddyfile should trust 172.16.0.0/12 for Docker internal network",
        )

    def test_trusted_proxy_10_range(self):
        """Should trust 10.0.0.0/8 (private network range)."""
        self.assertIn(
            "10.0.0.0/8",
            self.content,
            "Caddyfile should trust 10.0.0.0/8 for private network",
        )

    def test_trusted_proxy_192_range(self):
        """Should trust 192.168.0.0/16 (private network range)."""
        self.assertIn(
            "192.168.0.0/16",
            self.content,
            "Caddyfile should trust 192.168.0.0/16 for private network",
        )

    def test_trusted_proxies_only_internal(self):
        """
        All trusted_proxies entries should be RFC 1918 private ranges only.
        No public IP ranges should be trusted.
        """
        proxy_pattern = re.compile(r"trusted_proxies\s+range\s+(\S+)")
        ranges = proxy_pattern.findall(self.content)

        allowed_ranges = {
            "172.16.0.0/12",
            "10.0.0.0/8",
            "192.168.0.0/16",
        }

        for r in ranges:
            self.assertIn(
                r,
                allowed_ranges,
                f"Untrusted proxy range '{r}' found — only RFC 1918 ranges allowed",
            )

    def test_trusted_proxies_not_empty(self):
        """At least one trusted_proxies directive should exist."""
        proxy_pattern = re.compile(r"trusted_proxies")
        matches = proxy_pattern.findall(self.content)
        self.assertGreater(
            len(matches),
            0,
            "No trusted_proxies directives found — should restrict proxy trust",
        )


class TestSecurityHeaders(unittest.TestCase):
    """Verify security headers are configured in Caddyfile."""

    @classmethod
    def setUpClass(cls):
        with open(_CADDYFILE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_hsts_header(self):
        """Strict-Transport-Security header should be set."""
        self.assertIn(
            "Strict-Transport-Security",
            self.content,
            "HSTS header should be configured",
        )

    def test_x_content_type_options(self):
        """X-Content-Type-Options header should be set to nosniff."""
        self.assertIn(
            "X-Content-Type-Options",
            self.content,
            "X-Content-Type-Options header should be configured",
        )

    def test_x_frame_options(self):
        """X-Frame-Options header should be set."""
        self.assertIn(
            "X-Frame-Options",
            self.content,
            "X-Frame-Options header should be configured",
        )

    def test_remove_x_powered_by(self):
        """X-Powered-By header should be removed."""
        self.assertIn(
            "-X-Powered-By",
            self.content,
            "X-Powered-By header should be removed to avoid information leakage",
        )


class TestTLSConfiguration(unittest.TestCase):
    """Verify TLS is configured in Caddyfile."""

    @classmethod
    def setUpClass(cls):
        with open(_CADDYFILE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_tls_enabled(self):
        """TLS should be enabled."""
        self.assertIn(
            "tls",
            self.content,
            "TLS should be enabled in Caddyfile",
        )

    def test_http_redirect_to_https(self):
        """HTTP should redirect to HTTPS."""
        self.assertIn(
            "redir https://",
            self.content,
            "HTTP should redirect to HTTPS",
        )


if __name__ == "__main__":
    unittest.main()
