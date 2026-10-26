"""
Test 1: Chat Flow
User → Slammer → Greenie → Shrewd → External LLM

Validates:
- Greenie health endpoint
- Agent creation in Greenie
- Chat session creation
- Chat message sending
- Shrewd provider delegation
"""

from tests.integration.base_test import BaseIntegrationTest


class TestChatFlow(BaseIntegrationTest):
    """Test the chat completion flow through Greenie and Shrewd."""

    service = "Greenie/Shrewd"

    def run(self) -> bool:
        print("\n  Step 1: Check Greenie health")
        greenie_ok = self.check_service_health("Greenie", 8080)

        print("\n  Step 2: Check Shrewd health")
        shrewd_ok = self.check_service_health("Shrewd", 8089)

        if not greenie_ok or not shrewd_ok:
            print("\n  ⊘ Services not running, skipping flow test")
            return False

        # Create an agent
        print("\n  Step 3: Create test agent")
        agent_data = {
            "name": "Test Chat Agent",
            "description": "Integration test agent",
            "status": "active",
        }
        agent = self.make_request("post", "/api/agents", json=agent_data)
        agent_created = self.assert_true(
            agent is not None and "id" in agent, "Agent created successfully"
        )
        agent_id = agent.get("id", "") if agent else ""

        # Create a chat session
        print("\n  Step 4: Create chat session")
        session_data = {
            "name": "Test Session",
            "agent_id": agent_id,
        }
        session = self.make_request("post", "/api/chat/sessions", json=session_data)
        session_created = self.assert_true(
            session is not None and "id" in session, "Chat session created successfully"
        )
        session_id = session.get("id", "") if session else ""

        # Send a chat message
        print("\n  Step 5: Send chat message")
        if session_id:
            message_data = {
                "role": "user",
                "content": "Hello, this is an integration test.",
            }
            message = self.make_request(
                "post", f"/api/chat/sessions/{session_id}/messages", json=message_data
            )
            message_sent = self.assert_true(
                message is not None, "Chat message sent successfully"
            )
        else:
            message_sent = False
            print("  ✗ No session ID, skipping message send")

        # Check Shrewd providers
        print("\n  Step 6: Check Shrewd providers")
        providers = self.make_request("get", "/api/providers")
        providers_ok = self.assert_true(
            providers is not None, "Shrewd providers endpoint accessible"
        )

        # Check Shrewd models
        print("\n  Step 7: Check Shrewd models")
        models = self.make_request("get", "/api/models")
        models_ok = self.assert_true(
            models is not None, "Shrewd models endpoint accessible"
        )

        # Cleanup
        print("\n  Step 8: Cleanup")
        if agent_id:
            self.make_request("delete", f"/api/agents/{agent_id}")
            print("  ✓ Test agent deleted")

        all_passed = all(
            [
                greenie_ok,
                shrewd_ok,
                agent_created,
                session_created,
                message_sent,
                providers_ok,
                models_ok,
            ]
        )

        return all_passed
