"""Poltergeist — Notification channel implementations.

Provides async send functions for Slack, Discord, Email, and Telegram.
"""

from __future__ import annotations

import json
import logging

import aiohttp

logger = logging.getLogger(__name__)


async def send_slack(config: dict, recipient: str, subject: str, body: str) -> None:
    """Send a notification via Slack webhook."""
    webhook_url = config.get("webhook_url", "")
    if not webhook_url:
        raise ValueError("Slack webhook_url is required")

    payload = {
        "text": f"{subject}\n{body}" if subject else body,
    }
    if recipient:
        payload["channel"] = recipient

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status not in (200, 201):
                text = await resp.text()
                raise RuntimeError(f"Slack returned {resp.status}: {text}")


async def send_discord(config: dict, recipient: str, subject: str, body: str) -> None:
    """Send a notification via Discord webhook."""
    webhook_url = config.get("webhook_url", "")
    if not webhook_url:
        raise ValueError("Discord webhook_url is required")

    payload = {
        "content": f"**{subject}**\n{body}" if subject else body,
    }
    if recipient:
        payload["username"] = recipient

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status not in (200, 201, 204):
                text = await resp.text()
                raise RuntimeError(f"Discord returned {resp.status}: {text}")


async def send_email(config: dict, recipient: str, subject: str, body: str) -> None:
    """Send a notification via SMTP email."""
    import aiosmtplib

    smtp_host = config.get("smtp_host", "localhost")
    smtp_port = config.get("smtp_port", 587)
    smtp_user = config.get("smtp_user", "")
    smtp_password = config.get("smtp_password", "")
    sender = config.get("sender", "noreply@evershade.local")

    message = f"From: {sender}\nTo: {recipient}\nSubject: {subject}\n\n{body}"

    try:
        smtp = aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port)
        if smtp_user and smtp_password:
            await smtp.login(smtp_user, smtp_password)
        await smtp.send_message(message)
        await smtp.quit()
    except Exception as e:
        raise RuntimeError(f"Email delivery failed: {e}")


async def send_telegram(config: dict, recipient: str, subject: str, body: str) -> None:
    """Send a notification via Telegram Bot API."""
    bot_token = config.get("bot_token", "")
    if not bot_token:
        raise ValueError("Telegram bot_token is required")

    chat_id = recipient
    text = f"{subject}\n{body}" if subject else body

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status not in (200, 201):
                text_resp = await resp.text()
                raise RuntimeError(f"Telegram returned {resp.status}: {text_resp}")


# Map channel types to their send functions
CHANNEL_SENDERS = {
    "slack": send_slack,
    "discord": send_discord,
    "email": send_email,
    "telegram": send_telegram,
}


async def send_notification(channel_type: str, config: dict, recipient: str, subject: str, body: str) -> None:
    """Dispatch a notification to the appropriate channel."""
    sender = CHANNEL_SENDERS.get(channel_type)
    if not sender:
        raise ValueError(f"Unknown channel type: {channel_type}")
    await sender(config, recipient, subject, body)
