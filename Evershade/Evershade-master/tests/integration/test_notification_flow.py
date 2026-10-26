"""
Test 4: Notification Flow
Greenie → Poltergeist → External channels

Validates:
- Poltergeist health endpoint
- Channel creation
- Template creation
- Notification sending
- Delivery history
"""

from tests.integration.base_test import BaseIntegrationTest


class TestNotificationFlow(BaseIntegrationTest):
    """Test the notification flow through Poltergeist."""
    
    service = "Poltergeist"
    
    def run(self) -> bool:
        print("\n  Step 1: Check Poltergeist health")
        poltergeist_ok = self.check_service_health("Poltergeist", 8088)
        
        if not poltergeist_ok:
            print("\n  ⊘ Poltergeist not running, skipping flow test")
            return False
        
        # Create a notification channel
        print("\n  Step 2: Create test channel")
        channel_data = {
            "type": "slack",
            "name": "Test Channel",
            "enabled": True,
            "config": {
                "webhook_url": "https://hooks.slack.com/services/test",
            },
        }
        channel = self.make_request("post", "/api/channels", json=channel_data)
        channel_created = self.assert_true(
            channel is not None and "id" in channel,
            "Channel created successfully"
        )
        channel_id = channel.get("id", "") if channel else ""
        
        # Create a notification template
        print("\n  Step 3: Create test template")
        template_data = {
            "name": "Test Template",
            "subject": "Test Notification",
            "body": "This is a test notification from {{sender}}.",
        }
        template = self.make_request("post", "/api/templates", json=template_data)
        template_created = self.assert_true(
            template is not None and "id" in template,
            "Template created successfully"
        )
        
        # Send a notification
        print("\n  Step 4: Send test notification")
        if channel_id:
            notification_data = {
                "channel_id": channel_id,
                "subject": "Integration Test",
                "message": "This is a test notification.",
            }
            notification = self.make_request(
                "post",
                "/api/notifications",
                json=notification_data
            )
            notification_sent = self.assert_true(
                notification is not None,
                "Notification queued successfully"
            )
        else:
            notification_sent = False
            print("  ✗ No channel ID, skipping notification send")
        
        # Check delivery history
        print("\n  Step 5: Check delivery history")
        history = self.make_request("get", "/api/history")
        history_ok = self.assert_true(
            history is not None,
            "Delivery history accessible"
        )
        
        # List channels
        print("\n  Step 6: List channels")
        channels = self.make_request("get", "/api/channels")
        channels_ok = self.assert_true(
            channels is not None and "channels" in channels,
            "Channel list retrieved"
        )
        
        # Cleanup
        print("\n  Step 7: Cleanup")
        if channel_id:
            self.make_request("delete", f"/api/channels/{channel_id}")
            print("  ✓ Test channel deleted")
        
        all_passed = all([
            poltergeist_ok, channel_created, template_created,
            notification_sent, history_ok, channels_ok
        ])
        
        return all_passed

