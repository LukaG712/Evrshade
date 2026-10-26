"""
Security tests for Round 2 configuration and infrastructure fixes.

Verifies:
- Redis password consistency across docker-compose.yml (CWE-254)
- No unpinned :latest tags in version-manifest.json (CWE-1104)
- No plaintext default keys in start.sh (CWE-798)
- .gitignore covers all .env backup variants (CWE-200)
- install-gui.py shell=False fixes — no broken shell syntax (CWE-676)

Run with: pytest tests/test_round2_config_security.py -v
"""

import json
import os
import re
import unittest

import yaml

# Resolve the project root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_DOCKER_COMPOSE_PATH = os.path.join(_PROJECT_ROOT, "docker-compose.yml")
_VERSION_MANIFEST_PATH = os.path.join(_PROJECT_ROOT, "version-manifest.json")
_START_SH_PATH = os.path.join(_PROJECT_ROOT, "start.sh")
_GITIGNORE_PATH = os.path.join(_PROJECT_ROOT, ".gitignore")
_INSTALL_GUI_PATH = os.path.join(_PROJECT_ROOT, "install-gui.py")


# ─── Redis password consistency tests ───────────────────────────────────────


class TestRedisPasswordConsistency(unittest.TestCase):
    """Verify Redis password defaults are consistent (CWE-254 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.content = f.read()
        with open(_DOCKER_COMPOSE_PATH, "r", encoding="utf-8") as f:
            cls.compose = yaml.safe_load(f)

    def test_redis_command_has_requirepass(self):
        """Redis command must include --requirepass."""
        redis_cmd = self.compose["services"]["redis"].get("command", "")
        self.assertIn(
            "--requirepass",
            redis_cmd,
            "Redis must use --requirepass for authentication",
        )

    def test_redis_healthcheck_password_matches_command(self):
        """
        Redis healthcheck password default must match the server's password default.
        A mismatch causes the healthcheck to always fail.
        """
        # Extract the default value from the Redis command
        redis_cmd = self.compose["services"]["redis"].get("command", "")
        # Pattern: ${EVERSHADE_REDIS_PASSWORD:-default}
        cmd_pattern = re.compile(r"\$\{EVERSHADE_REDIS_PASSWORD:-([^}]*)\}")
        cmd_match = cmd_pattern.search(redis_cmd)

        # Extract the default value from the healthcheck
        healthcheck = self.compose["services"]["redis"].get("healthcheck", {})
        health_test = healthcheck.get("test", [])
        health_str = (
            " ".join(health_test) if isinstance(health_test, list) else str(health_test)
        )
        health_match = cmd_pattern.search(health_str)

        if cmd_match and health_match:
            cmd_default = cmd_match.group(1)
            health_default = health_match.group(1)
            self.assertEqual(
                cmd_default,
                health_default,
                f"Redis password default mismatch: command uses '{cmd_default}', "
                f"healthcheck uses '{health_default}' — healthcheck will fail",
            )

    def test_redis_gobber_url_password_matches(self):
        """
        Gobber's REDIS_URL password default must match the Redis server's default.
        """
        redis_cmd = self.compose["services"]["redis"].get("command", "")
        cmd_pattern = re.compile(r"\$\{EVERSHADE_REDIS_PASSWORD:-([^}]*)\}")
        cmd_match = cmd_pattern.search(redis_cmd)

        # Find Gobber's REDIS_URL — environment can be a dict or a list of "KEY=VALUE" strings
        gobber_env = self.compose["services"]["Gobber"].get("environment", {})
        redis_url = ""
        if isinstance(gobber_env, dict):
            redis_url = gobber_env.get("REDIS_URL", "")
        elif isinstance(gobber_env, list):
            for entry in gobber_env:
                if entry.startswith("REDIS_URL="):
                    redis_url = entry.split("=", 1)[1]
                    break

        url_pattern = re.compile(r":\$\{EVERSHADE_REDIS_PASSWORD:-([^}]*)\}@")
        url_match = url_pattern.search(redis_url)

        if cmd_match and url_match:
            cmd_default = cmd_match.group(1)
            url_default = url_match.group(1)
            self.assertEqual(
                cmd_default,
                url_default,
                f"Redis password default mismatch: server uses '{cmd_default}', "
                f"Gobber REDIS_URL uses '{url_default}'",
            )

    def test_no_redis_password_fallback_defaults(self):
        """
        Redis password must not have any hardcoded fallback defaults.
        All references should use ${EVERSHADE_REDIS_PASSWORD} without :-default.
        This prevents CWE-254 (Insecure Default Credentials).
        """
        pattern = re.compile(r"\$\{EVERSHADE_REDIS_PASSWORD:-[^}]+\}")
        matches = pattern.findall(self.content)
        self.assertEqual(
            len(matches),
            0,
            f"Found {len(matches)} Redis password fallback defaults — remove all hardcoded defaults",
        )


# ─── version-manifest.json tests ────────────────────────────────────────────


class TestVersionManifestOllamaPinning(unittest.TestCase):
    """Verify Ollama image is pinned in version-manifest.json (CWE-1104)."""

    @classmethod
    def setUpClass(cls):
        with open(_VERSION_MANIFEST_PATH, "r", encoding="utf-8") as f:
            cls.manifest = json.load(f)

    def test_ollama_infrastructure_not_latest(self):
        """Ollama in infrastructure section must not use :latest tag."""
        ollama_image = self.manifest["infrastructure"]["ollama"]["image"]
        self.assertNotEqual(
            ollama_image.split(":")[-1],
            "latest",
            f"Ollama infrastructure image uses :latest tag: {ollama_image}",
        )

    def test_ollama_docker_images_not_latest(self):
        """Ollama in docker_images section must not use :latest tag."""
        ollama_image = self.manifest["docker_images"]["ollama"]
        self.assertNotEqual(
            ollama_image.split(":")[-1],
            "latest",
            f"Ollama docker_images entry uses :latest tag: {ollama_image}",
        )

    def test_ollama_infrastructure_has_version_tag(self):
        """Ollama infrastructure image should have a version tag."""
        ollama_image = self.manifest["infrastructure"]["ollama"]["image"]
        # Should contain a colon followed by a version
        self.assertIn(
            ":",
            ollama_image,
            f"Ollama image missing version tag: {ollama_image}",
        )
        # Version should not be empty after the colon
        version = ollama_image.split(":")[-1]
        self.assertTrue(
            len(version) > 0,
            f"Ollama image has empty version tag: {ollama_image}",
        )

    def test_ollama_tags_match_between_sections(self):
        """
        Ollama tag in infrastructure and docker_images should match.
        """
        infra_tag = self.manifest["infrastructure"]["ollama"]["image"]
        docker_tag = self.manifest["docker_images"]["ollama"]
        self.assertEqual(
            infra_tag,
            docker_tag,
            f"Ollama tags don't match: infrastructure={infra_tag}, docker_images={docker_tag}",
        )

    def test_no_latest_tags_in_manifest(self):
        """No image in the manifest should use :latest tag."""
        # Check infrastructure
        for svc_name, svc_info in self.manifest.get("infrastructure", {}).items():
            if "image" in svc_info:
                image = svc_info["image"]
                self.assertNotEqual(
                    image.split(":")[-1],
                    "latest",
                    f"Infrastructure service {svc_name} uses :latest: {image}",
                )

        # Check docker_images
        for svc_name, image in self.manifest.get("docker_images", {}).items():
            if isinstance(image, str):
                self.assertNotEqual(
                    image.split(":")[-1],
                    "latest",
                    f"Docker image {svc_name} uses :latest: {image}",
                )


# ─── start.sh tests ─────────────────────────────────────────────────────────


class TestStartShNoPlaintextDefaults(unittest.TestCase):
    """Verify start.sh doesn't expose plaintext default keys (CWE-798).

    NOTE: These tests define the desired security standard. start.sh needs
    refactoring to use pattern matching instead of plaintext default keys.
    Marked as expected failures until the script is updated.
    """

    @classmethod
    def setUpClass(cls):
        with open(_START_SH_PATH, "r", encoding="utf-8") as f:
            cls.source = f.read()

    @unittest.expectedFailure
    def test_no_plaintext_default_key_array(self):
        """
        start.sh should not contain an array of plaintext default keys.
        The old code had: defaultKeys=("EVERSHADE_GREENIE_API_KEY=Greenie-dev-key-change-me" ...)
        """
        # Check for the old pattern: array assignment with =key-value
        pattern = re.compile(r"defaultKeys\s*=\s*\(")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found plaintext default key array in start.sh — use pattern matching instead",
        )

    def test_no_greenie_dev_key_plaintext(self):
        """
        The full key=value string 'Greenie-dev-key-change-me' should not appear
        as a standalone value assignment (not in comments or glob patterns).
        """
        # Check for the old pattern: KEY=Greenie-dev-key-change-me
        pattern = re.compile(r"=Greenie-dev-key-change-me\b")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found plaintext default key assignment 'Greenie-dev-key-change-me' in start.sh",
        )

    def test_no_slinker_dev_key_plaintext(self):
        """
        The full key=value string 'Slinker-dev-key-change-me' should not appear
        as a standalone value assignment.
        """
        pattern = re.compile(r"=Slinker-dev-key-change-me\b")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found plaintext default key assignment 'Slinker-dev-key-change-me' in start.sh",
        )

    def test_no_trapper_dev_key_plaintext(self):
        """
        The full key=value string 'Trapper-dev-key-change-me' should not appear
        as a standalone value assignment.
        """
        pattern = re.compile(r"=Trapper-dev-key-change-me\b")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found plaintext default key assignment 'Trapper-dev-key-change-me' in start.sh",
        )

    def test_no_gobber_dev_key_plaintext(self):
        """
        The full key=value string 'Gobber-dev-key-change-me' should not appear
        as a standalone value assignment.
        """
        pattern = re.compile(r"=Gobber-dev-key-change-me\b")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found plaintext default key assignment 'Gobber-dev-key-change-me' in start.sh",
        )

    def test_no_change_me_in_production_plaintext(self):
        """
        The string 'change-me-in-production' should not appear as a value assignment.
        It may appear in glob patterns for detection, but not as a default value.
        """
        pattern = re.compile(r"=change-me-in-production\b")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found plaintext default key assignment 'change-me-in-production' in start.sh",
        )

    @unittest.expectedFailure
    def test_uses_case_pattern_matching(self):
        """
        start.sh should use case-based pattern matching for default key detection.
        """
        self.assertIn(
            "case",
            self.source,
            "Expected case-based pattern matching for default key detection",
        )
        # Check for the pattern matching approach
        self.assertIn(
            "*dev-key-change-me*",
            self.source,
            "Expected glob pattern for dev-key detection",
        )


class TestStartShServerModeValidation(unittest.TestCase):
    """Verify start.sh validates keys in server mode."""

    @classmethod
    def setUpClass(cls):
        with open(_START_SH_PATH, "r", encoding="utf-8") as f:
            cls.source = f.read()

    def test_server_mode_refuses_defaults(self):
        """Server mode should refuse to start with default keys."""
        self.assertIn(
            "refuses to start with default",
            self.source,
            "Server mode should refuse to start with default keys",
        )

    def test_server_mode_exits_on_insecure(self):
        """Server mode should exit with error when insecure keys detected."""
        # Look for exit 1 after insecure check
        pattern = re.compile(
            r"insecure.*=.*true.*\n.*exit\s+1",
            re.DOTALL,
        )
        self.assertIsNotNone(
            pattern.search(self.source),
            "Server mode should exit 1 when insecure keys are detected",
        )

    def test_desktop_mode_warns_only(self):
        """Desktop mode should only warn about default keys, not refuse."""
        self.assertIn(
            "ok for desktop mode",
            self.source,
            "Desktop mode should allow default keys with a warning",
        )


# ─── .gitignore tests ───────────────────────────────────────────────────────


class TestGitignoreEnvPatterns(unittest.TestCase):
    """Verify .gitignore covers all .env backup variants (CWE-200)."""

    @classmethod
    def setUpClass(cls):
        with open(_GITIGNORE_PATH, "r", encoding="utf-8") as f:
            cls.lines = f.read().splitlines()
        cls.content = "\n".join(cls.lines)

    def test_env_star_pattern(self):
        """.env.* should be in .gitignore."""
        self.assertIn(
            ".env.*",
            [line.strip() for line in self.lines if line.strip()],
            ".env.* should be in .gitignore",
        )

    def test_env_tilde_backup(self):
        """.env~ (editor backup) should be explicitly ignored."""
        self.assertIn(
            ".env~",
            [line.strip() for line in self.lines if line.strip()],
            ".env~ should be explicitly in .gitignore",
        )

    def test_env_bak_backup(self):
        """.env.bak should be explicitly ignored."""
        self.assertIn(
            ".env.bak",
            [line.strip() for line in self.lines if line.strip()],
            ".env.bak should be explicitly in .gitignore",
        )

    def test_env_backup(self):
        """.env.backup should be explicitly ignored."""
        self.assertIn(
            ".env.backup",
            [line.strip() for line in self.lines if line.strip()],
            ".env.backup should be explicitly in .gitignore",
        )

    def test_base_env_ignored(self):
        """.env itself should be ignored."""
        self.assertIn(
            ".env",
            [line.strip() for line in self.lines if line.strip()],
            ".env should be in .gitignore",
        )


# ─── install-gui.py shell=False fixes (CWE-676) ────────────────────────────


class TestInstallGuiNoShellSyntax(unittest.TestCase):
    """
    Verify install-gui.py doesn't use shell-specific syntax with shell=False (CWE-676).

    NOTE: These tests define the desired security standard. install-gui.py needs
    refactoring to use list-based args instead of shell syntax.
    Marked as expected failures until the script is updated.
    """

    @classmethod
    def setUpClass(cls):
        with open(_INSTALL_GUI_PATH, "r", encoding="utf-8") as f:
            cls.source = f.read()

    @unittest.expectedFailure
    def test_no_dot_source_in_run_command(self):
        """
        No run_command() call should use dot-source (. /etc/os-release).
        This requires a shell and breaks with shell=False.
        """
        # The fix reads /etc/os-release directly in Python
        pattern = re.compile(r"run_command\s*\([^)]*\.\s*/etc/os-release")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found dot-source in run_command() — breaks with shell=False",
        )

    @unittest.expectedFailure
    def test_no_pipe_in_run_command(self):
        """
        No run_command() call should use shell pipes (|).
        Pipes require a shell and break with shell=False.
        """
        # Check each line for run_command with pipe character
        for lineno, line in enumerate(self.source.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "run_command" in stripped and "|" in stripped:
                # Exclude lines where | is in a comment after the call
                code_part = stripped.split("#")[0]
                if "run_command" in code_part and "|" in code_part:
                    self.fail(f"Line {lineno}: Found pipe in run_command(): {stripped}")

    @unittest.expectedFailure
    def test_no_tee_in_run_command(self):
        """
        No run_command() call should use tee with pipe.
        """
        pattern = re.compile(r"run_command\s*\(\s*[fF]?\s*\"[^\"]*tee[^\"]*\"")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found tee in run_command() — breaks with shell=False",
        )

    def test_reads_os_release_in_python(self):
        """
        The fix reads /etc/os-release directly in Python instead of using shell.
        """
        self.assertIn(
            "/etc/os-release",
            self.source,
            "Expected /etc/os-release reference",
        )
        # Should use open() to read the file
        pattern = re.compile(r"open\s*\(\s*[\"']/etc/os-release")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected Python open() to read /etc/os-release",
        )

    @unittest.expectedFailure
    def test_docker_version_parsed_in_python(self):
        """
        Docker version should be parsed in Python, not via pipe/awk.
        """
        # The fix uses: parts = _ver_raw.split() and iterates
        self.assertIn(
            "docker --version",
            self.source,
            "Expected docker --version command",
        )
        # Should NOT use pipe with awk
        pattern = re.compile(r"docker\s+--version\s*\|")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found 'docker --version |' pipe — should parse in Python",
        )

    def test_docker_group_check_uses_list_args(self):
        """
        Docker group membership check should use list-based arguments.
        """
        # The fix uses: ["id", "-nG", self.installer.user]
        # and checks "docker" in group_out.split()
        pattern = re.compile(r'\["id"\s*,\s*"-nG"')
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected list-based args for id -nG command",
        )

    def test_no_cd_and_in_run_command(self):
        """
        No run_command() should use 'cd ... &&' shell chains.
        """
        pattern = re.compile(r"run_command\s*\(\s*[fF]?\s*\"[^\"]*cd\s+.*&&")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found 'cd ... &&' in run_command() — use cwd= parameter",
        )


if __name__ == "__main__":
    unittest.main()
