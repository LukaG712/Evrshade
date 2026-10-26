"""Greenie — Task orchestration routes.

Provides endpoints for:
- Task creation with auto-decomposition
- Task status tracking
- Task cancellation
- Task retry
- Agent capability discovery
- Task result retrieval
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query

from evershade.errors import EvershadeError
from app.orchestrator import TaskOrchestrator
from app.models_task import (
    AgentCapabilityResponse,
    TaskCancelResponse,
    TaskCreate,
    TaskResponse,
    TaskResultResponse,
    TaskRetryResponse,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_orchestrator(app_state) -> TaskOrchestrator:
    """Get or create the task orchestrator from app state."""
    if not hasattr(app_state, "orchestrator"):
        slinker_url = getattr(app_state, "slinker_url", "http://Slinker:8081")
        http_client = getattr(app_state, "http_client", None)
        app_state.orchestrator = TaskOrchestrator(
            slinker_url=slinker_url,
            http_client=http_client,
        )
    return app_state.orchestrator


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, app_state: object = None):
    """Create a new task with automatic decomposition."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    task_id = await orchestrator.create_task(
        title=data.title,
        description=data.description,
        agent_id=data.agent_id,
        required_capabilities=data.required_capabilities if data.required_capabilities else None,
        priority=data.priority,
        project_id=data.project_id,
        mission_id=data.mission_id,
        metadata=data.metadata if data.metadata else None,
    )

    task = await orchestrator.get_task(task_id)
    if not task:
        raise EvershadeError.internal_error("Task creation failed")
    return task


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    agent_id: Optional[str] = Query(None, description="Filter by agent"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    app_state: object = None,
):
    """List tasks with optional filtering."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    tasks = await orchestrator.list_tasks(
        status=status,
        agent_id=agent_id,
        limit=limit,
        offset=offset,
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, app_state: object = None):
    """Get task details with subtasks."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    task = await orchestrator.get_task(task_id)
    if not task:
        raise EvershadeError.not_found("Task not found")
    return task


@router.post("/{task_id}/execute", response_model=TaskResponse)
async def execute_task(task_id: str, app_state: object = None):
    """Start executing a task."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    task = await orchestrator.get_task(task_id)
    if not task:
        raise EvershadeError.not_found("Task not found")

    if task["status"] not in ("pending", "failed", "cancelled", "partial"):
        raise EvershadeError.bad_request(
            f"Cannot execute task in status: {task['status']}"
        )

    await orchestrator.execute_task(task_id)
    task = await orchestrator.get_task(task_id)
    return task


@router.post("/{task_id}/cancel", response_model=TaskCancelResponse)
async def cancel_task(task_id: str, app_state: object = None):
    """Cancel a running or pending task."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    cancelled = await orchestrator.cancel_task(task_id)

    return TaskCancelResponse(
        task_id=task_id,
        cancelled=cancelled,
        message="Task cancelled" if cancelled else "Task could not be cancelled",
    )


@router.post("/{task_id}/retry", response_model=TaskRetryResponse)
async def retry_task(task_id: str, app_state: object = None):
    """Retry a failed task from the last failed subtask."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    task = await orchestrator.get_task(task_id)
    if not task:
        raise EvershadeError.not_found("Task not found")

    if task["status"] not in ("failed", "partial", "cancelled"):
        raise EvershadeError.bad_request(
            f"Cannot retry task in status: {task['status']}"
        )

    await orchestrator.retry_task(task_id)
    return TaskRetryResponse(
        task_id=task_id,
        status="pending",
        message="Task retry initiated",
    )


@router.get("/{task_id}/results", response_model=List[TaskResultResponse])
async def get_task_results(task_id: str, app_state: object = None):
    """Get all results for a task."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    task = await orchestrator.get_task(task_id)
    if not task:
        raise EvershadeError.not_found("Task not found")

    results = await orchestrator.get_task_results(task_id)
    return results


@router.get("/agents", response_model=List[AgentCapabilityResponse])
async def discover_agents(
    required_capabilities: Optional[str] = Query(
        None, description="Comma-separated capabilities to filter by"
    ),
    app_state: object = None,
):
    """Discover agents matching the required capabilities."""
    if not app_state:
        raise EvershadeError.bad_request("Application state not available")

    orchestrator = get_orchestrator(app_state)
    caps = None
    if required_capabilities:
        caps = [c.strip() for c in required_capabilities.split(",") if c.strip()]

    agents = await orchestrator.discover_agents(caps)
    return [AgentCapabilityResponse(**agent.to_dict()) for agent in agents]
