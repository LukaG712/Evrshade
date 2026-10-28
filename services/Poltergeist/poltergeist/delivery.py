"""Delivery implementations for Poltergeist notification service.

Each delivery class handles formatting and sending notifications to a specific
channel: Slack (webhooks), Discord (webhooks), Email (SMTP), and Telegram (bot API).
"""

import asyncio
import html
import os
import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

import httpx

from poltergeist.models import Notification


# Allowed webhook URL schemes
_ALLOWED_WEBHOOK_SCHEMES = {"https", "http"}

# Known legitimate webhook host patterns
_KNOWN_WEBHOOK_HOSTS = {
    "hooks.slack.com",
    "discord.com",
    "discordapp.com",
    "discordapp.net",
}


class BaseDelivery:
    """Abstract base for notification delivery."""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create a reusable AsyncClient instance."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._get_timeout())
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    async def send(self, notification: Notification) -> None:
        """Send a notification and update its status."""
        raise NotImplementedError

    def _get_timeout(self) -> float:
        return float(os.getenv("POLTERGEIST_REQUEST_TIMEOUT", "30"))


def _validate_webhook_url(url: str, configured_url: str) -> str:
    """Validate that a webhook URL is safe to use.

    Only allows the configured webhook URL to prevent SSRF and data exfiltration.
    Rejects arbitrary URLs that could redirect notifications to attacker-controlled servers.

    Args:
        url: The URL to validate.
        configured_url: The configured webhook URL from environment variables.

    Returns:
        The validated URL.

    Raises:
        ValueError: If the URL is not the configured webhook URL.
    """
    if not url:
        return configured_url
    # Only allow the configured webhook URL — never override with user-provided URLs
    if url != configured_url:
        raise ValueError(
            f"Webhook URL override is not allowed. Use the configured webhook URL."
        )
    return url


class SlackDelivery(BaseDelivery):
    """Deliver notifications via Slack Incoming Webhooks."""

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")

    async def send(self, notification: Notification) -> None:
        if not self.webhook_url:
            raise RuntimeError("SLACK_WEBHOOK_URL is not configured")

        # Slack block kit format — use plain_text to prevent injection
        payload = {
            "text": f"{notification.title}\n{notification.message}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": (notification.title or "Notification")[:150],  # Slack limit
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": notification.message},
                },
            ],
        }
        # Never allow recipient to override the configured webhook URL
        url = _validate_webhook_url(notification.recipient, self.webhook_url)

        client = await self._get_client()
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise ConnectionError(f"Slack returned {response.status_code}")


class DiscordDelivery(BaseDelivery):
    """Deliver notifications via Discord Webhooks."""

    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

    async def send(self, notification: Notification) -> None:
        if not self.webhook_url:
            raise RuntimeError("DISCORD_WEBHOOK_URL is not configured")

        payload = {
            "content": None,
            "embeds": [
                {
                    "title": notification.title or "Notification",
                    "description": notification.message[:2048],  # Discord limit
                    "color": 5814783,  # Blue
                }
            ],
        }
        # Never allow recipient to override the configured webhook URL
        url = _validate_webhook_url(notification.recipient, self.webhook_url)

        client = await self._get_client()
        response = await client.post(url, json=payload)
        if response.status_code not in (200, 204):
            raise ConnectionError(f"Discord returned {response.status_code}")


class EmailDelivery(BaseDelivery):
    """Deliver notifications via SMTP."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "noreply@evershade.local")
        self.use_tls = os.getenv("SMTP_TLS", "true").lower() in ("true", "1", "yes")

    async def send(self, notification: Notification) -> None:
        if not self.smtp_user:
            raise RuntimeError("SMTP_USER is not configured")

        # Validate email recipient to prevent header injection
        recipient = notification.recipient
        if not recipient or "\n" in recipient or "\r" in recipient:
            raise ValueError("Invalid email recipient")
        if "@" not in recipient:
            raise ValueError("Email recipient must contain '@'")

        msg = MIMEMultipart()
        msg["From"] = self.smtp_from
        msg["To"] = recipient
        msg["Subject"] = notification.title or "Evershade Notification"
        msg.attach(MIMEText(notification.message, "html"))

        context = ssl.create_default_context() if self.use_tls else None

        # Run blocking SMTP operations in a thread to avoid blocking the event loop
        def _send_sync():
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.use_tls:
                    server.starttls(context=context)
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(
                    self.smtp_from,
                    notification.recipient,
                    msg.as_string(),
                )

        await asyncio.to_thread(_send_sync)


def _escape_html(text: str) -> str:
    """Escape HTML entities to prevent HTML injection in Telegram messages.

    Args:
        text: The text to escape.

    Returns:
        HTML-escaped text safe for use in Telegram HTML parse mode.
    """
    return html.escape(text, quote=True)


class TelegramDelivery(BaseDelivery):
    """Deliver notifications via Telegram Bot API."""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.base_url = "https://api.telegram.org/bot"

    async def send(self, notification: Notification) -> None:
        if not self.bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

        # Recipient is the chat_id
        chat_id = notification.recipient
        if not chat_id:
            raise ValueError("Telegram chat_id (recipient) is required")

        # Validate chat_id is numeric to prevent injection
        if not re.match(r'^-?\d+$', chat_id):
            raise ValueError("Telegram chat_id must be numeric")

        url = f"{self.base_url}{self.bot_token}/sendMessage"
        # Escape HTML entities to prevent injection attacks
        safe_title = _escape_html(notification.title or "")
        safe_message = _escape_html(notification.message or "")
        payload = {
            "chat_id": chat_id,
            "text": f"{safe_title}\n\n{safe_message}",
            "parse_mode": "HTML",
        }

        client = await self._get_client()
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise ConnectionError(f"Telegram returned {response.status_code}")


class WebhookDelivery(BaseDelivery):
    """Deliver notifications via generic HTTP webhooks."""

    async def send(self, notification: Notification) -> None:
        url = notification.recipient
        if not url:
            raise ValueError("Webhook URL (recipient) is required")

        payload = {
            "title": notification.title,
            "message": notification.message,
            "metadata": notification.metadata,
        }

        client = await self._get_client()
        response = await client.post(url, json=payload)
        if response.status_code >= 400:
            raise ConnectionError(f"Webhook returned {response.status_code}")


# Module-level cached delivery instances
_delivery_cache: dict[str, BaseDelivery] = {}


def get_delivery(channel_str: str) -> BaseDelivery:
    """Get the delivery instance for a given channel, caching instances for reuse."""
    if channel_str not in _delivery_cache:
        delivery_map = {
            "slack": SlackDelivery(),
            "discord": DiscordDelivery(),
            "email": EmailDelivery(),
            "telegram": TelegramDelivery(),
            "webhook": WebhookDelivery(),
        }
        if channel_str not in delivery_map:
            raise ValueError(f"Unknown channel: {channel_str}")
        _delivery_cache[channel_str] = delivery_map[channel_str]
    return _delivery_cache[channel_str]
