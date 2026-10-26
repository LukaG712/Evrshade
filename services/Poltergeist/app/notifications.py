"""Poltergeist — Notification rules and preferences management.

Provides:
- Event-driven notifications triggered by service events
- User preferences for notification delivery
- Notification rules with conditions and filters
- Delivery status tracking and retry management
- Integration with other services through documented contracts
"""

from __future__ import annotations

import json
import logging
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from evershade_db import Database

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manage notification rules, preferences, and event-driven delivery."""

    def __init__(self, db: Database, http_client: Any):
        self.db = db
        self.http_client = http_client
        self._notification_queue: asyncio.Queue = asyncio.Queue()
        self._processing = False

    async def start_processor(self) -> None:
        """Start the background notification processor."""
        self._processing = True
        asyncio.create_task(self._process_queue())

    async def stop_processor(self) -> None:
        """Stop the background notification processor."""
        self._processing = False

    async def _process_queue(self) -> None:
        """Process notifications from the queue."""
        while self._processing:
            try:
                notification = await asyncio.wait_for(
                    self._notification_queue.get(),
                    timeout=1.0,
                )
                await self._deliver_notification(notification)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Notification processing error: {e}")

    async def _deliver_notification(self, notification: Dict[str, Any]) -> None:
        """Deliver a single notification."""
        notification_id = notification["id"]
        channel_id = notification.get("channel_id")
        channel_type = notification.get("channel_type", "")
        recipient = notification.get("recipient", "")
        subject = notification.get("subject", "")
        body = notification.get("body", "")

        # Update status to sent
        await self.db.execute(
            "UPDATE pending_queue SET status = ? WHERE id = ?",
            ("sending", notification_id),
        )

        try:
            # Send via Poltergeist's own channels
            poltergeist_url = "http://localhost:8088"
            response = await self.http_client.post(
                f"{poltergeist_url}/api/notifications",
                json={
                    "channel": channel_id or channel_type,
                    "recipient": recipient,
                    "subject": subject,
                    "body": body,
                },
                timeout=30,
            )

            if response.status_code in (200, 201):
                await self.db.execute(
                    "UPDATE pending_queue SET status = ? WHERE id = ?",
                    ("sent", notification_id),
                )
            else:
                raise Exception(f"Delivery failed: {response.status_code}")

        except Exception as e:
            # Increment retry count
            retry_row = await self.db.fetchone(
                "SELECT retry_count, max_retries FROM pending_queue WHERE id = ?",
                (notification_id,),
            )
            if retry_row:
                retry_count = retry_row["retry_count"] + 1
                max_retries = retry_row["max_retries"]

                if retry_count < max_retries:
                    await self.db.execute(
                        "UPDATE pending_queue SET retry_count = ?, status = ? WHERE id = ?",
                        (retry_count, "retrying", notification_id),
                    )
                    # Re-queue for retry
                    await self._notification_queue.put(notification)
                else:
                    await self.db.execute(
                        "UPDATE pending_queue SET status = ?, error_message = ? WHERE id = ?",
                        ("failed", str(e), notification_id),
                    )
                    logger.error(f"Notification {notification_id} failed after {retry_count} retries: {e}")

    # ─── User Preferences ────────────────────────────────────────────────

    async def get_user_preferences(
        self, user_id: str
    ) -> Dict[str, Any]:
        """Get notification preferences for a user."""
        row = await self.db.fetchone(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            (user_id,),
        )
        if not row:
            return {
                "user_id": user_id,
                "enabled": True,
                "channels": [],
                "quiet_hours": None,
                "digest_frequency": "realtime",
                "event_filters": {},
            }

        return {
            **row,
            "channels": json.loads(row.get("channels", "[]")),
            "quiet_hours": json.loads(row.get("quiet_hours", "null")),
            "event_filters": json.loads(row.get("event_filters", "{}")),
        }

    async def set_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set notification preferences for a user."""
        channels = preferences.get("channels", [])
        quiet_hours = preferences.get("quiet_hours")
        digest_frequency = preferences.get("digest_frequency", "realtime")
        event_filters = preferences.get("event_filters", {})
        enabled = preferences.get("enabled", True)

        existing = await self.db.fetchone(
            "SELECT id FROM user_preferences WHERE user_id = ?",
            (user_id,),
        )

        if existing:
            await self.db.execute(
                """UPDATE user_preferences
                   SET channels = ?, quiet_hours = ?, digest_frequency = ?,
                       event_filters = ?, enabled = ?,
                       updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
                   WHERE user_id = ?""",
                (
                    json.dumps(channels),
                    json.dumps(quiet_hours),
                    digest_frequency,
                    json.dumps(event_filters),
                    1 if enabled else 0,
                    user_id,
                ),
            )
        else:
            await self.db.execute(
                """INSERT INTO user_preferences
                   (id, user_id, channels, quiet_hours, digest_frequency,
                    event_filters, enabled)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    user_id,
                    json.dumps(channels),
                    json.dumps(quiet_hours),
                    digest_frequency,
                    json.dumps(event_filters),
                    1 if enabled else 0,
                ),
            )

        return await self.get_user_preferences(user_id)

    # ─── Notification Rules ──────────────────────────────────────────────

    async def get_notification_rules(
        self,
        event_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get notification rules, optionally filtered by event type."""
        query = "SELECT * FROM notification_rules WHERE 1=1"
        params: List[Any] = []

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY priority DESC"
        rows = await self.db.fetchall(query, params)
        return [
            {
                **row,
                "conditions": json.loads(row.get("conditions", "{}")),
                "channels": json.loads(row.get("channels", "[]")),
                "enabled": bool(row["enabled"]),
            }
            for row in rows
        ]

    async def create_notification_rule(
        self, rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a notification rule."""
        rule_id = str(uuid.uuid4())
        event_type = rule.get("event_type", "")
        if not event_type:
            raise ValueError("event_type is required")

        name = rule.get("name", event_type)
        conditions = rule.get("conditions", {})
        channels = rule.get("channels", [])
        template = rule.get("template", "")
        priority = rule.get("priority", 5)
        enabled = rule.get("enabled", True)

        await self.db.execute(
            """INSERT INTO notification_rules
               (id, name, event_type, conditions, channels, template, priority, enabled)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                rule_id,
                name,
                event_type,
                json.dumps(conditions),
                json.dumps(channels),
                template,
                priority,
                1 if enabled else 0,
            ),
        )

        row = await self.db.fetchone("SELECT * FROM notification_rules WHERE id = ?", (rule_id,))
        return {
            **row,
            "conditions": json.loads(row.get("conditions", "{}")),
            "channels": json.loads(row.get("channels", "[]")),
            "enabled": bool(row["enabled"]),
        }

    async def delete_notification_rule(self, rule_id: str) -> bool:
        """Delete a notification rule."""
        existing = await self.db.fetchone(
            "SELECT id FROM notification_rules WHERE id = ?",
            (rule_id,),
        )
        if not existing:
            return False
        await self.db.execute("DELETE FROM notification_rules WHERE id = ?", (rule_id,))
        return True

    # ─── Event-Driven Notifications ──────────────────────────────────────

    async def handle_event(
        self, event: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle an incoming event and trigger matching notifications.

        This is the main entry point for event-driven notifications.
        Other services call this to trigger notifications based on events.
        """
        event_type = event.get("type", "")
        event_data = event.get("data", {})
        source_service = event.get("source", "")

        # Get matching rules
        rules = await self.get_notification_rules(event_type)

        triggered_notifications = []
        for rule in rules:
            # Check conditions
            if not self._evaluate_conditions(rule["conditions"], event_data):
                continue

            # Build notification
            notification = {
                "id": str(uuid.uuid4()),
                "event_type": event_type,
                "source_service": source_service,
                "rule_id": rule["id"],
                "channels": rule["channels"],
                "template": rule.get("template", ""),
                "data": event_data,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Queue for delivery
            await self.db.execute(
                """INSERT INTO event_notifications
                   (id, event_type, source_service, rule_id, channels,
                    template, data, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    notification["id"],
                    event_type,
                    source_service,
                    rule["id"],
                    json.dumps(rule["channels"]),
                    rule.get("template", ""),
                    json.dumps(event_data),
                    "pending",
                    notification["created_at"],
                ),
            )

            # Add to processing queue
            await self._notification_queue.put({
                "id": notification["id"],
                "channel_id": rule["channels"][0] if rule["channels"] else "",
                "channel_type": rule["channels"][0] if rule["channels"] else "",
                "recipient": event_data.get("recipient", ""),
                "subject": self._render_template(
                    rule.get("template", f"Event: {event_type}"),
                    event_data,
                ),
                "body": self._render_template(
                    rule.get("template", json.dumps(event_data, indent=2)),
                    event_data,
                ),
            })

            triggered_notifications.append(notification)

        return triggered_notifications

    def _evaluate_conditions(
        self, conditions: Dict[str, Any], event_data: Dict[str, Any]
    ) -> bool:
        """Evaluate notification rule conditions against event data."""
        if not conditions:
            return True

        for key, expected in conditions.items():
            actual = event_data.get(key)
            if actual != expected:
                return False

        return True

    def _render_template(
        self, template: str, data: Dict[str, Any]
    ) -> str:
        """Simple template rendering with {{key}} placeholders."""
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    # ─── Delivery Status ─────────────────────────────────────────────────

    async def get_delivery_status(
        self,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get delivery status of event-driven notifications."""
        query = "SELECT * FROM event_notifications WHERE 1=1"
        params: List[Any] = []

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = await self.db.fetchall(query, params)
        return [
            {
                **row,
                "channels": json.loads(row.get("channels", "[]")),
                "data": json.loads(row.get("data", "{}")),
            }
            for row in rows
        ]

    async def get_notification_summary(self) -> Dict[str, Any]:
        """Get summary of notification activity."""
        # Total pending
        pending = await self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM event_notifications WHERE status = 'pending'"
        )

        # Total sent
        sent = await self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM event_notifications WHERE status = 'sent'"
        )

        # Total failed
        failed = await self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM event_notifications WHERE status = 'failed'"
        )

        # By event type
        by_type = await self.db.fetchall(
            """SELECT event_type, COUNT(*) as cnt
            FROM event_notifications
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY event_type
            ORDER BY cnt DESC"""
        )

        # By channel
        by_channel = await self.db.fetchall(
            """SELECT channel_type, COUNT(*) as cnt
            FROM delivery_history
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY channel_type
            ORDER BY cnt DESC"""
        )

        return {
            "pending": pending["cnt"] if pending else 0,
            "sent": sent["cnt"] if sent else 0,
            "failed": failed["cnt"] if failed else 0,
            "by_event_type": by_type,
            "by_channel": by_channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
