"""Poltergeist — Notification rules and event-driven routes.

Endpoints for user preferences, notification rules, event handling,
and delivery status tracking.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request

from evershade.errors import EvershadeError

from app.notifications import NotificationManager

router = APIRouter(prefix="/api/notify", tags=["notifications"])


# ─── User Preferences ───────────────────────────────────────────────────────

@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str, request: Request) -> Dict[str, Any]:
    """Get notification preferences for a user."""
    manager: NotificationManager = request.app.state.notification_manager
    return await manager.get_user_preferences(user_id)


@router.put("/preferences/{user_id}")
async def set_user_preferences(
    user_id: str,
    request: Request,
) -> Dict[str, Any]:
    """Set notification preferences for a user."""
    manager: NotificationManager = request.app.state.notification_manager
    preferences = await request.json()
    return await manager.set_user_preferences(user_id, preferences)


# ─── Notification Rules ─────────────────────────────────────────────────────

@router.get("/rules")
async def get_notification_rules(
    request: Request,
    event_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get notification rules."""
    manager: NotificationManager = request.app.state.notification_manager
    return await manager.get_notification_rules(event_type)


@router.post("/rules", status_code=201)
async def create_notification_rule(request: Request) -> Dict[str, Any]:
    """Create a notification rule."""
    manager: NotificationManager = request.app.state.notification_manager
    rule = await request.json()
    try:
        return await manager.create_notification_rule(rule)
    except ValueError as e:
        raise EvershadeError.validation_error(str(e))


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_notification_rule(rule_id: str, request: Request):
    """Delete a notification rule."""
    manager: NotificationManager = request.app.state.notification_manager
    deleted = await manager.delete_notification_rule(rule_id)
    if not deleted:
        raise EvershadeError.not_found(f"Rule {rule_id} not found")


# ─── Event Handling ─────────────────────────────────────────────────────────

@router.post("/events")
async def handle_event(request: Request) -> Dict[str, Any]:
    """Handle an incoming event and trigger matching notifications.

    This is the main entry point for event-driven notifications.
    Other services call this to trigger notifications based on events.
    """
    manager: NotificationManager = request.app.state.notification_manager
    event = await request.json()
    notifications = await manager.handle_event(event)
    return {
        "triggered": len(notifications),
        "notifications": notifications,
    }


# ─── Delivery Status ────────────────────────────────────────────────────────

@router.get("/delivery")
async def get_delivery_status(
    request: Request,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Get delivery status of event-driven notifications."""
    manager: NotificationManager = request.app.state.notification_manager
    return await manager.get_delivery_status(event_type, status, limit)


@router.get("/summary")
async def get_notification_summary(request: Request) -> Dict[str, Any]:
    """Get summary of notification activity."""
    manager: NotificationManager = request.app.state.notification_manager
    return await manager.get_notification_summary()
