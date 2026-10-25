"""
Security tests for .env.example configuration.

Verifies:
- No hardcoded default API keys (CWE-798)
- No hardcoded encryption key (CWE-798)
- Redis password is required
- Default isolation mode is container (CWE-693)

Run with: pytest tests/test_env_example_security.py -v
"""

import os
import re
import unittest

# Resolve the project root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_ENV_EXAMPLE_PATH = os.path.join(_PROJECT_ROOT, ".env.example")


class TestNoHardcodedKeys(unittest.TestCase):
    """Verify .env.example contains no hardcoded default keys (CWE-798 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_ENV_EXAMPLE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()
        with open(_ENV_EXAMPLE_PATH, "r", encoding="utf-8") as f:
            cls.lines = f.readlines()

    def _get_key_values(self):
        """Extract all KEY=value pairs from .env.example."""
        values = {}
        for line in self.lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
        return values

    def test_no_change_me_in_api_keys(self):
        """No API key should contain 'change-me' as a value."""
        values = self._get_key_values()
        api_key_vars = [
            "EVERSHADE_GREENIE_API_KEY",
            "EVERSHADE_SLINKER_API_KEY",
            "EVERSHADE_TRAPPER_API_KEY",
            "EVERSHADE_GOBBER_API_KEY",
            "EVERSHADE_SNEAKER_API_KEY",
            "EVERSHADE_HIDER_API_KEY",
            "EVERSHADE_POLTERGEIST_API_KEY",
            "EVERSHADE_SHREWD_API_KEY",
        ]
        for var in api_key_vars:
            if var in values:
                self.assertNotIn(
                    "change-me",
                    values[var].lower(),
                    f"{var} should not contain 'change-me' as a default value",
                )

    def test_no_dev_key_in_api_keys(self):
        """No API key should contain 'dev-key' as a value."""
        values = self._get_key_values()
        api_key_vars = [
            "EVERSHADE_GREENIE_API_KEY",
            "EVERSHADE_SLINKER_API_KEY",
            "EVERSHADE_TRAPPER_API_KEY",
            "EVERSHADE_GOBBER_API_KEY",
            "EVERSHADE_SNEAKER_API_KEY",
            "EVERSHADE_HIDER_API_KEY",
            "EVERSHADE_POLTERGEIST_API_KEY",
            "EVERSHADE_SHREWD_API_KEY",
        ]
        for var in api_key_vars:
            if var in values:
                self.assertNotIn(
                    "dev-key",
                    values[var].lower(),
                    f"{var} should not contain 'dev-key' as a default value",
                )

    def test_no_placeholder_in_api_keys(self):
        """
        API keys should use a clear placeholder indicating they need to be generated,
        not a value that could accidentally be used.
        """
        values = self._get_key_values()
        api_key_vars = [
            "EVERSHADE_GREENIE_API_KEY",
            "EVERSHADE_SLINKER_API_KEY",
            "EVERSHADE_TRAPPER_API_KEY",
            "EVERSHADE_GOBBER_API_KEY",
            "EVERSHADE_SNEAKER_API_KEY",
            "EVERSHADE_HIDER_API_KEY",
            "EVERSHADE_POLTERGEIST_API_KEY",
            "EVERSHADE_SHREWD_API_KEY",
        ]
        for var in api_key_vars:
            if var in values:
                val = values[var]
                # Value should be a placeholder, not a real-looking key
                # A real hex key would be 64 chars of hex
                if re.match(r"^[0-9a-f]{64}$", val):
                    self.fail(
                        f"{var} appears to have a real hex key as default — "
                        "use a placeholder instead",
                    )

    def test_encryption_key_not_hardcoded(self):
        """ENCRYPTION_KEY should not be a hardcoded value."""
        values = self._get_key_values()
        if "EVERSHADE_ENCRYPTION_KEY" in values:
            val = values["EVERSHADE_ENCRYPTION_KEY"]
            self.assertNotIn(
                "change-me",
                val.lower(),
                "ENCRYPTION_KEY should not contain 'change-me'",
            )
            # Should not be a real-looking hex key
            if re.match(r"^[0-9a-f]{64}$", val):
                self.fail(
                    "ENCRYPTION_KEY appears to have a real hex key as default",
                )

    def test_redis_password_not_empty(self):
        """
        Redis password should have a placeholder, not be empty.
        An empty default would mean Redis runs without auth.
        """
        values = self._get_key_values()
        if "EVERSHADE_REDIS_PASSWORD" in values:
            val = values["EVERSHADE_REDIS_PASSWORD"]
            self.assertNotEqual(
                val,
                "",
                "EVERSHADE_REDIS_PASSWORD should not be empty — Redis needs a password",
            )

    def test_no_real_secrets_in_file(self):
        """
        The file should not contain any values that look like real secrets.
        A real secret would be a 64-char hex string (openssl rand -hex 32).
        """
        real_secret_pattern = re.compile(r"=[0-9a-f]{64}$")
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if real_secret_pattern.search(stripped):
                key = stripped.split("=")[0]
                self.fail(
                    f"Line {i}: {key} appears to contain a real secret value — "
                    "use a placeholder instead",
                )


class TestIsolationMode(unittest.TestCase):
    """Verify default isolation mode is container (CWE-693 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_ENV_EXAMPLE_PATH, "r", encoding="utf-8") as f:
            cls.lines = f.readlines()

    def test_default_isolation_mode_is_container(self):
        """EVERSHADE_ISOLATION_MODE should default to 'container'."""
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith("EVERSHADE_ISOLATION_MODE="):
                _, _, value = stripped.partition("=")
                self.assertEqual(
                    value.strip(),
                    "container",
                    f"Default isolation mode should be 'container', not '{value.strip()}'",
                )
                return
        self.fail("EVERSHADE_ISOLATION_MODE not found in .env.example")


class TestEnvExampleDocumentation(unittest.TestCase):
    """Verify .env.example has proper security documentation."""

    @classmethod
    def setUpClass(cls):
        with open(_ENV_EXAMPLE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_api_key_generation_instruction(self):
        """Should instruct users to generate keys with openssl."""
        self.assertIn(
            "openssl rand -hex 32",
            self.content,
            ".env.example should instruct users to generate keys with openssl",
        )

    def test_encryption_key_warning(self):
        """Should warn about losing the encryption key."""
        self.assertIn(
            "lose",
            self.content.lower(),
            ".env.example should warn about losing the encryption key",
        )

    def test_required_key_comment(self):
        """Should mark API keys as required."""
        self.assertIn(
            "REQUIRED",
            self.content,
            ".env.example should mark API keys as REQUIRED",
        )


if __name__ == "__main__":
    unittest.main()
