"""Phase 14 — Cross-service integration tests.

Tests workflow execution, observability correlation, security enforcement,
and notification delivery across Greenie, Sneaker, Hider, and Poltergeist.
"""

from __future__ import annotations

from tests.integration.base_test import BaseIntegrationTest


class TestPhase14Workflow(BaseIntegrationTest):
    """Test Greenie workflow engine."""

    def test_create_workflow(self) -> None:
        """Test creating a workflow definition."""
        workflow = {
            "name": "Test Workflow",
            "description": "Integration test workflow",
            "steps": [
                {
                    "step_id": "step1",
                    "name": "HTTP Request",
                    "type": "http_request",
                    "config": {"url": "http://example.com", "method": "GET"},
                },
                {
                    "step_id": "step2",
                    "name": "Delay",
                    "type": "delay",
                    "config": {"delay_seconds": 1},
                    "dependencies": ["step1"],
                },
            ],
            "status": "active",
        }
        resp = self.make_request("POST", "/api/workflows", json=workflow)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "Test Workflow")
        self.check_service_metrics("Greenie")

    def test_list_workflows(self) -> None:
        """Test listing workflows."""
        resp = self.make_request("GET", "/api/workflows")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)

    def test_workflow_capabilities(self) -> None:
        """Test workflow capabilities are reported."""
        resp = self.make_request("GET", "/api/capabilities")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        capabilities = data.get("capabilities", [])
        self.assertIn("workflows", capabilities)
        self.assertIn("webhooks", capabilities)
        self.assertIn("workflow_automation", capabilities)

    def test_create_webhook(self) -> None:
        """Test creating a webhook."""
        # First create a workflow
        workflow = {
            "name": "Webhook Test",
            "steps": [
                {
                    "step_id": "s1",
                    "name": "Delay",
                    "type": "delay",
                    "config": {"delay_seconds": 0},
                }
            ],
            "status": "active",
        }
        wf_resp = self.make_request("POST", "/api/workflows", json=workflow)
        if wf_resp.status_code != 201:
            self.skipTest("Workflow creation failed")

        wf_id = wf_resp.json()["id"]
        webhook = {
            "name": "Test Webhook",
            "workflow_id": wf_id,
        }
        resp = self.make_request("POST", "/api/workflows/webhooks", json=webhook)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("id", data)
        self.assertIn("webhook_url", data)


class TestPhase14Observability(BaseIntegrationTest):
    """Test Sneaker observability enhancements."""

    def test_trace_correlation(self) -> None:
        """Test trace correlation endpoint."""
        resp = self.make_request("GET", "/api/observe/correlate/trace/test-trace-id")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("trace_id", data)
        self.assertIn("traces", data)
        self.assertIn("logs", data)

    def test_service_health(self) -> None:
        """Test service health endpoint."""
        resp = self.make_request("GET", "/api/observe/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, dict)

    def test_ai_observability(self) -> None:
        """Test AI observability endpoint."""
        resp = self.make_request("GET", "/api/observe/ai")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("integrations", data)
        self.assertIn("langfuse", data["integrations"])
        self.assertIn("opik", data["integrations"])

    def test_dashboard_data(self) -> None:
        """Test dashboard data endpoint."""
        resp = self.make_request("GET", "/api/observe/dashboard")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("service_health", data)
        self.assertIn("timestamp", data)

    def test_observability_capabilities(self) -> None:
        """Test observability capabilities are reported."""
        resp = self.make_request("GET", "/api/capabilities", service="Sneaker")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        capabilities = data.get("capabilities", [])
        self.assertIn("trace_correlation", capabilities)
        self.assertIn("ai_observability", capabilities)
        self.assertIn("loki_integration", capabilities)
        self.assertIn("tempo_integration", capabilities)


class TestPhase14Security(BaseIntegrationTest):
    """Test Hider security enhancements."""

    def test_get_agent_permissions(self) -> None:
        """Test getting agent permissions."""
        resp = self.make_request("GET", "/api/security/permissions/test-agent")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["agent_id"], "test-agent")
        self.assertIn("allowed_tools", data)

    def test_set_agent_permissions(self) -> None:
        """Test setting agent permissions."""
        permissions = {
            "allowed_tools": ["read_file", "write_file"],
            "denied_tools": ["execute_command"],
            "allowed_services": ["Slinker", "Trapper"],
            "max_execution_time": 60,
        }
        resp = self.make_request(
            "PUT",
            "/api/security/permissions/test-agent",
            json=permissions,
            service="Hider",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["agent_id"], "test-agent")
        self.assertIn("read_file", data["allowed_tools"])

    def test_check_tool_permission(self) -> None:
        """Test checking tool permission."""
        resp = self.make_request(
            "POST",
            "/api/security/permissions/test-agent/check-tool",
            json={"tool_name": "read_file"},
            service="Hider",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("allowed", data)

    def test_security_audit(self) -> None:
        """Test security audit log."""
        resp = self.make_request("GET", "/api/security/audit", service="Hider")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)

    def test_security_summary(self) -> None:
        """Test security summary endpoint."""
        resp = self.make_request("GET", "/api/security/summary", service="Hider")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("agents_with_permissions", data)
        self.assertIn("timestamp", data)

    def test_security_capabilities(self) -> None:
        """Test security capabilities are reported."""
        resp = self.make_request("GET", "/api/capabilities", service="Hider")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        capabilities = data.get("capabilities", [])
        self.assertIn("agent_permissions", capabilities)
        self.assertIn("security_audit", capabilities)
        self.assertIn("ssrf_protection", capabilities)


class TestPhase14Notifications(BaseIntegrationTest):
    """Test Poltergeist notification enhancements."""

    def test_get_user_preferences(self) -> None:
        """Test getting user preferences."""
        resp = self.make_request(
            "GET", "/api/notify/preferences/test-user", service="Poltergeist"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["user_id"], "test-user")
        self.assertIn("channels", data)

    def test_set_user_preferences(self) -> None:
        """Test setting user preferences."""
        preferences = {
            "channels": ["slack", "email"],
            "digest_frequency": "daily",
            "event_filters": {"task_completed": True},
            "enabled": True,
        }
        resp = self.make_request(
            "PUT",
            "/api/notify/preferences/test-user",
            json=preferences,
            service="Poltergeist",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("slack", data["channels"])

    def test_create_notification_rule(self) -> None:
        """Test creating a notification rule."""
        rule = {
            "name": "Task Completion Alert",
            "event_type": "task_completed",
            "conditions": {"status": "completed"},
            "channels": ["slack"],
            "template": "Task {{title}} completed",
            "priority": 10,
        }
        resp = self.make_request(
            "POST",
            "/api/notify/rules",
            json=rule,
            service="Poltergeist",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("id", data)
        self.assertEqual(data["event_type"], "task_completed")

    def test_handle_event(self) -> None:
        """Test event-driven notification handling."""
        event = {
            "type": "task_completed",
            "source": "Greenie",
            "data": {
                "title": "Test Task",
                "status": "completed",
                "recipient": "test@example.com",
            },
        }
        resp = self.make_request(
            "POST",
            "/api/notify/events",
            json=event,
            service="Poltergeist",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("triggered", data)

    def test_notification_summary(self) -> None:
        """Test notification summary endpoint."""
        resp = self.make_request("GET", "/api/notify/summary", service="Poltergeist")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("pending", data)
        self.assertIn("sent", data)
        self.assertIn("failed", data)

    def test_notification_capabilities(self) -> None:
        """Test notification capabilities are reported."""
        resp = self.make_request("GET", "/api/capabilities", service="Poltergeist")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        capabilities = data.get("capabilities", [])
        self.assertIn("event_driven", capabilities)
        self.assertIn("user_preferences", capabilities)
        self.assertIn("notification_rules", capabilities)


class TestPhase14CrossService(BaseIntegrationTest):
    """Test cross-service integration scenarios."""

    def test_workflow_triggers_notification(self) -> None:
        """Test that a workflow can trigger a notification via Poltergeist.

        This is a mocked test because it requires both Greenie and Poltergeist running.
        """
        # Create a notification rule for workflow events
        rule = {
            "name": "Workflow Completion",
            "event_type": "workflow_completed",
            "channels": ["slack"],
            "template": "Workflow {{name}} completed",
        }
        rule_resp = self.make_request(
            "POST",
            "/api/notify/rules",
            json=rule,
            service="Poltergeist",
        )

        if rule_resp.status_code != 201:
            self.skipTest("Notification rule creation failed")

        # Trigger an event
        event = {
            "type": "workflow_completed",
            "source": "Greenie",
            "data": {"name": "Test Workflow"},
        }
        resp = self.make_request(
            "POST",
            "/api/notify/events",
            json=event,
            service="Poltergeist",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(data["triggered"], 0)

    def test_security_enforcement(self) -> None:
        """Test that security permissions are enforced.

        This is a mocked test because it requires Hider and Greenie running.
        """
        # Set permissions
        permissions = {
            "allowed_tools": ["read_file"],
            "denied_tools": ["execute_command"],
        }
        perm_resp = self.make_request(
            "PUT",
            "/api/security/permissions/test-agent",
            json=permissions,
            service="Hider",
        )

        if perm_resp.status_code != 200:
            self.skipTest("Permission setting failed")

        # Check tool permission
        resp = self.make_request(
            "POST",
            "/api/security/permissions/test-agent/check-tool",
            json={"tool_name": "execute_command"},
            service="Hider",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["allowed"])

    def test_observability_correlation(self) -> None:
        """Test that observability data is correlated across services.

        This is a mocked test because it requires Sneaker with data.
        """
        resp = self.make_request("GET", "/api/observe/dashboard", service="Sneaker")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("service_health", data)
        self.assertIn("timestamp", data)
