"""
Security tests for docker-compose.yml configuration.

Verifies:
- No hardcoded default API keys (CWE-798)
- Redis requires authentication (CWE-306)
- No unpinned :latest image tags (CWE-1104)
- Default isolation mode is container (CWE-693)
- No default encryption key fallback (CWE-798)
- No insecure default credentials for monitoring services (CWE-798)
- cAdvisor does not use privileged mode (CWE-250)

Run with: pytest tests/test_docker_compose_security.py -v
"""

import os
import re
import unittest

import yaml

# Resolve the project root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DOCKER_COMPOSE_PATH = os.path.join(_PROJECT_ROOT, "docker-compose.yml")


class TestNoHardcodedSecrets(unittest.TestCase):
    """Verify no hardcoded default secrets in docker-compose.yml (CWE-798 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_no_change_me_defaults(self):
        """No 'change-me' default values should exist."""
        self.assertNotIn(
            "change-me",
            self.content,
            "Found 'change-me' default in docker-compose.yml — secrets must not have defaults",
        )

    def test_no_dev_key_defaults(self):
        """No 'dev-key' default values should exist."""
        self.assertNotIn(
            "dev-key",
            self.content,
            "Found 'dev-key' default in docker-compose.yml — secrets must not have defaults",
        )

    def test_no_hardcoded_api_key_fallbacks(self):
        """
        No API key environment variable should have a hardcoded fallback value.
        Pattern: ${VAR:-hardcoded-value} is forbidden for API keys.
        """
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
            # Look for patterns like ${VAR:-some-default}
            pattern = re.compile(r"\$\{" + re.escape(var) + r":-[^}]+\}")
            match = pattern.search(self.content)
            if match is not None:
                self.fail(
                    f"API key {var} has a hardcoded default fallback: {match.group()}",
                )

    def test_no_hardcoded_encryption_key_fallback(self):
        """ENCRYPTION_KEY must not have a default fallback."""
        pattern = re.compile(r"\$\{EVERSHADE_ENCRYPTION_KEY:-[^}]+\}")
        match = pattern.search(self.content)
        if match is not None:
            self.fail(
                f"ENCRYPTION_KEY has a hardcoded default fallback: {match.group()}",
            )

    def test_api_keys_use_variable_only(self):
        """
        API key env vars should reference the variable without a fallback,
        e.g. ${EVERSHADE_GREENIE_API_KEY} not ${EVERSHADE_GREENIE_API_KEY:-default}.
        """
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
            # Find all occurrences of the variable reference
            pattern = re.compile(r"\$\{" + re.escape(var) + r"(?::-[^}]*)?\}")
            matches = pattern.findall(self.content)
            for match in matches:
                self.assertNotIn(
                    ":-",
                    match,
                    f"API key {var} has a fallback default: {match}",
                )


class TestRedisAuthentication(unittest.TestCase):
    """Verify Redis requires authentication (CWE-306 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_redis_requirepass_flag(self):
        """Redis command must include --requirepass flag."""
        self.assertIn(
            "--requirepass",
            self.content,
            "Redis must use --requirepass to require authentication",
        )

    def test_redis_password_variable(self):
        """Redis password should reference EVERSHADE_REDIS_PASSWORD variable."""
        self.assertIn(
            "EVERSHADE_REDIS_PASSWORD",
            self.content,
            "Redis should use EVERSHADE_REDIS_PASSWORD variable",
        )

    def test_redis_healthcheck_uses_password(self):
        """
        Redis healthcheck should authenticate with the password.
        Without -a flag, healthcheck will fail on authenticated Redis.
        """
        # Find the redis service section
        pattern = re.compile(
            r"redis:.*?healthcheck:.*?test:.*?(?=\n\s{4}\w|\n\n|\Z)",
            re.DOTALL,
        )
        match = pattern.search(self.content)
        self.assertIsNotNone(match, "Could not find Redis healthcheck")
        healthcheck_section = match.group()
        self.assertIn(
            "-a",
            healthcheck_section,
            "Redis healthcheck must use -a flag to authenticate",
        )


class TestPinnedImageTags(unittest.TestCase):
    """Verify all Docker images use pinned version tags (CWE-1104 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_no_latest_tags(self):
        """No image should use :latest tag."""
        latest_pattern = re.compile(r"image:\s*\S+:latest")
        matches = latest_pattern.findall(self.content)
        self.assertEqual(
            len(matches),
            0,
            f"Found :latest image tags: {matches} — all images must use pinned tags",
        )

    def test_all_images_have_version_tags(self):
        """All images should have explicit version tags."""
        image_pattern = re.compile(r"image:\s*(\S+)")
        images = image_pattern.findall(self.content)
        for image in images:
            self.assertIn(
                ":",
                image,
                f"Image '{image}' has no version tag — pin to a specific version",
            )
            # Verify it's not :latest
            self.assertFalse(
                image.endswith(":latest"),
                f"Image '{image}' uses :latest tag",
            )

    def test_ollama_image_pinned(self):
        """Ollama image must use a pinned version, not :latest."""
        ollama_pattern = re.compile(r"image:\s*ollama/ollama:(\S+)")
        match = ollama_pattern.search(self.content)
        self.assertIsNotNone(match, "Ollama image not found")
        tag = match.group(1)
        self.assertNotEqual(
            tag,
            "latest",
            "Ollama image must not use :latest tag",
        )


class TestIsolationMode(unittest.TestCase):
    """Verify default isolation mode is container (CWE-693 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_default_isolation_mode_is_container(self):
        """
        Slinker's default ISOLATION_MODE should be 'container', not 'worktree'.
        Worktree mode shares the host filesystem with no sandboxing.
        """
        pattern = re.compile(r"ISOLATION_MODE=\$\{EVERSHADE_ISOLATION_MODE:-(\w+)\}")
        match = pattern.search(self.content)
        self.assertIsNotNone(match, "ISOLATION_MODE not found in Slinker config")
        default_mode = match.group(1)
        self.assertEqual(
            default_mode,
            "container",
            f"Default isolation mode is '{default_mode}' — should be 'container' for security",
        )


class TestDockerComposeStructure(unittest.TestCase):
    """Verify docker-compose.yml structure and security settings."""

    @classmethod
    def setUpClass(cls):
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.data = yaml.safe_load(f)

    def test_redis_service_exists(self):
        """Redis service must exist."""
        self.assertIn("redis", self.data["services"])

    def test_redis_read_only(self):
        """Redis should run with read_only filesystem."""
        redis = self.data["services"]["redis"]
        self.assertTrue(
            redis.get("read_only", False),
            "Redis should run with read_only filesystem",
        )

    def test_redis_no_new_privileges(self):
        """Redis should have no-new-privileges security option."""
        redis = self.data["services"]["redis"]
        security_opts = redis.get("security_opt", [])
        self.assertIn(
            "no-new-privileges:true",
            security_opts,
            "Redis should have no-new-privileges security option",
        )

    def test_services_have_no_new_privileges(self):
        """All services should have no-new-privileges security option."""
        services = self.data["services"]
        # Skip services that may not need it (like ollama)
        for name, config in services.items():
            if name == "ollama":
                continue
            security_opts = config.get("security_opt", [])
            self.assertIn(
                "no-new-privileges:true",
                security_opts,
                f"Service '{name}' should have no-new-privileges security option",
            )

    def test_services_drop_all_capabilities(self):
        """Services should drop all Linux capabilities."""
        services = self.data["services"]
        for name, config in services.items():
            if name in ("ollama", "caddy", "redis"):
                # caddy needs NET_BIND_SERVICE, redis uses read_only + tmpfs instead
                continue
            cap_drop = config.get("cap_drop", [])
            self.assertIn(
                "ALL",
                cap_drop,
                f"Service '{name}' should drop ALL capabilities",
            )

    def test_cadvisor_not_privileged(self):
        """cAdvisor must not run in privileged mode (CWE-250)."""
        cadvisor = self.data["services"].get("cadvisor", {})
        self.assertFalse(
            cadvisor.get("privileged", False),
            "cAdvisor must not use privileged: true — use cap_add instead",
        )

    def test_cadvisor_has_cap_drop(self):
        """cAdvisor should drop all capabilities and add only what's needed."""
        cadvisor = self.data["services"].get("cadvisor", {})
        cap_drop = cadvisor.get("cap_drop", [])
        self.assertIn(
            "ALL",
            cap_drop,
            "cAdvisor should drop ALL capabilities",
        )


class TestNoInsecureFallbacks(unittest.TestCase):
    """Verify no insecure default credential fallbacks (CWE-798)."""

    @classmethod
    def setUpClass(cls):
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_no_redis_password_fallback(self):
        """Redis password must not have a hardcoded fallback default."""
        # Check for patterns like ${EVERSHADE_REDIS_PASSWORD:-some-default}
        pattern = re.compile(r"\$\{EVERSHADE_REDIS_PASSWORD:-[^}]+\}")
        match = pattern.search(self.content)
        if match is not None:
            self.fail(
                f"Redis password has a hardcoded fallback: {match.group()} — remove it"
            )

    def test_no_grafana_admin_password_fallback(self):
        """Grafana admin password must not default to 'admin'."""
        pattern = re.compile(r"\$\{GRAFANA_ADMIN_PASSWORD:-admin\}")
        match = pattern.search(self.content)
        self.assertIsNone(
            match,
            "Grafana admin password defaults to 'admin' — remove the fallback",
        )

    def test_no_grafana_admin_user_fallback(self):
        """Grafana admin user must not default to 'admin'."""
        pattern = re.compile(r"\$\{GRAFANA_ADMIN_USER:-admin\}")
        match = pattern.search(self.content)
        self.assertIsNone(
            match,
            "Grafana admin user defaults to 'admin' — remove the fallback",
        )

    def test_env_example_no_grafana_admin_default(self):
        """.env.example must not set Grafana password to 'admin'."""
        env_example = os.path.join(_PROJECT_ROOT, ".env.example")
        if not os.path.exists(env_example):
            self.skipTest(".env.example not found")
        with open(env_example, "r", encoding="utf-8") as f:
            content = f.read()
        # Check that GRAFANA_ADMIN_PASSWORD is not set to 'admin'
        pattern = re.compile(r"^GRAFANA_ADMIN_PASSWORD\s*=\s*admin\s*$", re.MULTILINE)
        match = pattern.search(content)
        self.assertIsNone(
            match,
            ".env.example sets GRAFANA_ADMIN_PASSWORD to 'admin' — use a placeholder",
        )


if __name__ == "__main__":
    unittest.main()
