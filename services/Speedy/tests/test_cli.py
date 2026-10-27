"""Tests for Speedy CLI — CLI parsing, client, and commands."""

import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner


class TestCLIParsing(unittest.TestCase):
    """Test that all CLI commands are registered and parseable."""

    def setUp(self):
        self.runner = CliRunner()

    def test_main_help(self):
        """Test that main CLI displays help."""
        from speedy.cli import main

        result = self.runner.invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("install", result.output)
        self.assertIn("start", result.output)
        self.assertIn("stop", result.output)
        self.assertIn("status", result.output)
        self.assertIn("doctor", result.output)
        self.assertIn("logs", result.output)
        self.assertIn("capabilities", result.output)
        self.assertIn("backup", result.output)
        self.assertIn("restore", result.output)
        self.assertIn("monitoring", result.output)

    def test_version(self):
        """Test that version flag works."""
        from speedy.cli import main

        result = self.runner.invoke(main, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("1.0.0", result.output)

    def test_install_help(self):
        """Test install command help."""
        from speedy.cli import main

        result = self.runner.invoke(main, ["install", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_status_help(self):
        """Test status command help."""
        from speedy.cli import main

        result = self.runner.invoke(main, ["status", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_doctor_help(self):
        """Test doctor command help."""
        from speedy.cli import main

        result = self.runner.invoke(main, ["doctor", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_capabilities_help(self):
        """Test capabilities command help."""
        from speedy.cli import main

        result = self.runner.invoke(main, ["capabilities", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_monitoring_help(self):
        """Test monitoring group help."""
        from speedy.cli import main

        result = self.runner.invoke(main, ["monitoring", "--help"])
        self.assertEqual(result.exit_code, 0)


class TestServiceClient(unittest.TestCase):
    """Test the HTTP client."""

    def setUp(self):
        from speedy.client import ServiceClient

        self.client = ServiceClient("http://localhost:9999", api_key="test-key")

    def test_headers_without_key(self):
        """Test headers without API key."""
        from speedy.client import ServiceClient

        client = ServiceClient("http://localhost:9999")
        headers = client._headers()
        self.assertIn("Accept", headers)
        self.assertNotIn("Authorization", headers)

    def test_headers_with_key(self):
        """Test headers with API key."""
        headers = self.client._headers()
        self.assertEqual(headers["Authorization"], "Bearer test-key")

    @patch("speedy.client.httpx.Client")
    def test_get_success(self, mock_client_class):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = self.client.get("/health")
        self.assertEqual(result, {"status": "ok"})

    @patch("speedy.client.httpx.Client")
    def test_get_unauthorized(self, mock_client_class):
        """Test 401 response returns None."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = self.client.get("/health")
        self.assertIsNone(result)

    @patch("speedy.client.httpx.Client")
    def test_get_connection_error(self, mock_client_class):
        """Test connection error returns None."""
        import httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")
        mock_client_class.return_value = mock_client

        result = self.client.get("/health")
        self.assertIsNone(result)

    @patch("speedy.client.httpx.Client")
    def test_check_health(self, mock_client_class):
        """Test health check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "service": "Test"}

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = self.client.check_health()
        self.assertTrue(result["healthy"])
        self.assertEqual(result["data"]["service"], "Test")


class TestConfig(unittest.TestCase):
    """Test configuration loading."""

    def test_load_config_defaults(self):
        """Test default config loading."""
        from speedy.config import load_config

        config = load_config()
        self.assertIn("greenie_url", config)
        self.assertIn("services", config)
        self.assertIn("api_keys", config)

    def test_load_config_with_url(self):
        """Test config with custom URL."""
        from speedy.config import load_config

        config = load_config(greenie_url="http://custom:9999")
        self.assertEqual(config["greenie_url"], "http://custom:9999")

    def test_services_defined(self):
        """Test that all expected services are defined."""
        from speedy.config import SERVICES

        expected = {
            "Greenie",
            "Slinker",
            "Trapper",
            "Gobber",
            "Sneaker",
            "Hider",
            "Poltergeist",
            "Shrewd",
        }
        self.assertEqual(set(SERVICES.keys()), expected)


if __name__ == "__main__":
    unittest.main()
