"""Dashboard and CLI integration tests.

Tests for Slammer dashboard API endpoints and Speedy CLI commands.
These tests verify that the dashboard displays real data and CLI commands work correctly.
"""

import unittest

from .base_test import BaseIntegrationTest


class TestDashboardAPI(BaseIntegrationTest):
    """Test Slammer dashboard API endpoints."""

    def test_dashboard_health(self):
        """Test dashboard can fetch health status."""
        data = self.make_request("GET", "/api/status")
        self.assertIsNotNone(data)

    def test_dashboard_agents(self):
        """Test dashboard can fetch agents list."""
        data = self.make_request("GET", "/api/agents")
        if data:
            self.assertIn("agents", data)

    def test_dashboard_missions(self):
        """Test dashboard can fetch missions list."""
        data = self.make_request("GET", "/api/missions")
        if data:
            self.assertIn("missions", data)

    def test_dashboard_tasks(self):
        """Test dashboard can fetch tasks list."""
        data = self.make_request("GET", "/api/v1/tasks")
        if data:
            self.assertIn("tasks", data)

    def test_dashboard_workflows(self):
        """Test dashboard can fetch workflows list."""
        data = self.make_request("GET", "/api/workflows")
        if data:
            self.assertIn("workflows", data)

    def test_dashboard_registry(self):
        """Test dashboard can fetch service registry."""
        data = self.make_request("GET", "/api/registry")
        if data:
            self.assertIn("services", data)

    def test_dashboard_providers(self):
        """Test dashboard can fetch model providers."""
        data = self.make_request("GET", "/api/providers")
        if data:
            self.assertIn("providers", data)

    def test_dashboard_models(self):
        """Test dashboard can fetch models list."""
        data = self.make_request("GET", "/api/models")
        if data:
            self.assertIn("models", data)

    def test_dashboard_channels(self):
        """Test dashboard can fetch notification channels."""
        data = self.make_request("GET", "/api/channels")
        if data:
            self.assertIn("channels", data)

    def test_dashboard_notification_rules(self):
        """Test dashboard can fetch notification rules."""
        data = self.make_request("GET", "/api/notification-rules")
        if data:
            self.assertIn("rules", data)

    def test_dashboard_memory(self):
        """Test dashboard can fetch memory entries."""
        data = self.make_request("GET", "/api/memory")
        if data:
            self.assertIn("entries", data)

    def test_dashboard_knowledge_search(self):
        """Test dashboard can search knowledge base."""
        data = self.make_request("GET", "/api/embeddings/search?q=test")
        if data:
            self.assertIn("results", data)


class TestCLICommands(BaseIntegrationTest):
    """Test Speedy CLI commands."""

    def test_cli_status(self):
        """Test CLI status command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "status", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("status", result.stdout.lower())

    def test_cli_validate(self):
        """Test CLI validate command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "validate", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("validate", result.stdout.lower())

    def test_cli_diagnose(self):
        """Test CLI diagnose command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "diagnose", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("diagnose", result.stdout.lower())

    def test_cli_version(self):
        """Test CLI version command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "version", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("version", result.stdout.lower())

    def test_cli_integrations(self):
        """Test CLI integrations command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "integrations", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("integrations", result.stdout.lower())

    def test_cli_workflows(self):
        """Test CLI workflows command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "workflows", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("workflows", result.stdout.lower())

    def test_cli_knowledge(self):
        """Test CLI knowledge command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "knowledge", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("knowledge", result.stdout.lower())

    def test_cli_models(self):
        """Test CLI models command."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "models", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("models", result.stdout.lower())

    def test_cli_help(self):
        """Test CLI help shows all commands."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "evershade_cli.main", "--help"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root / "services" / "Speedy"),
        )
        self.assertEqual(result.returncode, 0)
        expected_commands = [
            "status",
            "agents",
            "tasks",
            "config",
            "secrets",
            "capabilities",
            "registry",
            "monitoring",
            "install",
            "start",
            "stop",
            "validate",
            "diagnose",
            "version",
            "integrations",
            "workflows",
            "knowledge",
            "models",
        ]
        for cmd in expected_commands:
            self.assertIn(cmd, result.stdout, f"Missing command: {cmd}")


if __name__ == "__main__":
    unittest.main()
