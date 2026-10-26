"""Greenie — Workflow Engine for event-driven automation.

Provides:
- Workflow definitions with DAG-based step execution
- Event-driven triggers (webhooks, schedule, manual)
- Execution history and status tracking
- Retry policies with exponential backoff
- Conditional execution based on step results
- Webhook handling for external event triggers

Both n8n and Temporal were evaluated and rejected:
- n8n: SPL-1.0 license conflicts, operational overhead not justified
- Temporal: Requires Go cluster, overkill for current workloads

Native workflow engine handles all current requirements.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TriggerType(str, Enum):
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    EVENT = "event"


class StepType(str, Enum):
    HTTP_REQUEST = "http_request"
    SERVICE_CALL = "service_call"
    CONDITION = "condition"
    DELAY = "delay"
    NOTIFICATION = "notification"
    TASK = "task"
    SCRIPT = "script"


class WorkflowStep:
    """Represents a single step in a workflow."""

    def __init__(
        self,
        step_id: str,
        name: str,
        step_type: str,
        config: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        condition: Optional[str] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
    ):
        self.step_id = step_id
        self.name = name
        self.step_type = step_type
        self.config = config
        self.dependencies = dependencies or []
        self.condition = condition
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.timeout = timeout

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "type": self.step_type,
            "config": self.config,
            "dependencies": self.dependencies,
            "condition": self.condition,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowStep":
        return cls(
            step_id=data["step_id"],
            name=data["name"],
            step_type=data["type"],
            config=data.get("config", {}),
            dependencies=data.get("dependencies", []),
            condition=data.get("condition"),
            retry_count=data.get("retry_count", 0),
            retry_delay=data.get("retry_delay", 1.0),
            timeout=data.get("timeout"),
        )


class WorkflowDefinition:
    """Represents a workflow definition."""

    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str = "",
        steps: Optional[List[Dict[str, Any]]] = None,
        triggers: Optional[List[Dict[str, Any]]] = None,
        max_concurrent_runs: int = 5,
        timeout: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps = [WorkflowStep.from_dict(s) for s in (steps or [])]
        self.triggers = triggers or []
        self.max_concurrent_runs = max_concurrent_runs
        self.timeout = timeout
        self.metadata = metadata or {}
        self.status = WorkflowStatus.DRAFT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "triggers": self.triggers,
            "max_concurrent_runs": self.max_concurrent_runs,
            "timeout": self.timeout,
            "metadata": self.metadata,
            "status": self.status.value,
        }


class WorkflowRun:
    """Represents a single execution of a workflow."""

    def __init__(
        self,
        run_id: str,
        workflow_id: str,
        trigger_type: str,
        trigger_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.run_id = run_id
        self.workflow_id = workflow_id
        self.trigger_type = trigger_type
        self.trigger_data = trigger_data or {}
        self.context = context or {}
        self.status = RunStatus.PENDING
        self.step_results: Dict[str, Dict[str, Any]] = {}
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "workflow_id": self.workflow_id,
            "trigger_type": self.trigger_type,
            "trigger_data": self.trigger_data,
            "context": self.context,
            "status": self.status.value,
            "step_results": self.step_results,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }


class WorkflowEngine:
    """Core workflow execution engine.

    Executes workflows defined as DAGs of steps with retry policies,
    conditional execution, and timeout handling.
    """

    def __init__(self, db: Any, http_client: Any):
        self.db = db
        self.http_client = http_client
        self._active_runs: Dict[str, asyncio.Task] = {}

    async def execute_workflow(
        self,
        workflow_id: str,
        trigger_type: str = "manual",
        trigger_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Start a workflow execution asynchronously.

        Returns the run_id for tracking progress.
        """
        # Fetch workflow definition
        row = await self.db.fetchone(
            "SELECT * FROM workflows WHERE id = ? AND status = ?",
            (workflow_id, WorkflowStatus.ACTIVE.value),
        )
        if not row:
            raise ValueError(f"Workflow {workflow_id} not found or not active")

        workflow = WorkflowDefinition(
            workflow_id=row["id"],
            name=row["name"],
            description=row.get("description", ""),
            steps=json.loads(row.get("steps", "[]")),
            triggers=json.loads(row.get("triggers", "[]")),
            max_concurrent_runs=row.get("max_concurrent_runs", 5),
            timeout=row.get("timeout"),
            metadata=json.loads(row.get("metadata", "{}")),
        )

        # Check concurrent run limit
        active_count = await self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM workflow_runs "
            "WHERE workflow_id = ? AND status IN (?, ?)",
            (workflow_id, RunStatus.RUNNING.value, RunStatus.PENDING.value),
        )
        if active_count and active_count["cnt"] >= workflow.max_concurrent_runs:
            raise ValueError(
                f"Workflow {workflow_id} has reached max concurrent runs"
            )

        # Create run record
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        run = WorkflowRun(
            run_id=run_id,
            workflow_id=workflow_id,
            trigger_type=trigger_type,
            trigger_data=trigger_data,
            context=context,
        )
        run.status = RunStatus.RUNNING
        run.started_at = now

        await self.db.execute(
            """INSERT INTO workflow_runs
               (id, workflow_id, trigger_type, trigger_data, context, status, started_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                workflow_id,
                trigger_type,
                json.dumps(trigger_data or {}),
                json.dumps(context or {}),
                run.status.value,
                now,
            ),
        )

        # Create step records
        for step in workflow.steps:
            step_id = step.step_id
            await self.db.execute(
                """INSERT INTO workflow_steps
                   (id, run_id, step_id, name, step_type, status, order_index)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    run_id,
                    step_id,
                    step.name,
                    step.step_type,
                    StepStatus.PENDING.value,
                    workflow.steps.index(step),
                ),
            )

        # Start async execution
        task = asyncio.create_task(
            self._run_workflow(run, workflow),
            name=f"workflow-{run_id}",
        )
        self._active_runs[run_id] = task

        return run_id

    async def _run_workflow(
        self,
        run: WorkflowRun,
        workflow: WorkflowDefinition,
    ) -> None:
        """Execute all steps in a workflow in DAG order."""
        try:
            # Topological sort of steps
            execution_order = self._topological_sort(workflow.steps)

            for step in execution_order:
                if run.status != RunStatus.RUNNING:
                    # Workflow was cancelled
                    await self._update_step_status(
                        run.run_id, step.step_id, StepStatus.SKIPPED
                    )
                    continue

                # Check condition
                if step.condition:
                    should_run = self._evaluate_condition(
                        step.condition, run.context, run.step_results
                    )
                    if not should_run:
                        await self._update_step_status(
                            run.run_id, step.step_id, StepStatus.SKIPPED
                        )
                        continue

                # Check dependencies
                deps_met = all(
                    run.step_results.get(dep, {}).get("status") == StepStatus.COMPLETED.value
                    for dep in step.dependencies
                )
                if not deps_met:
                    await self._update_step_status(
                        run.run_id, step.step_id, StepStatus.SKIPPED
                    )
                    continue

                # Execute step with retry
                result = await self._execute_step(step, run)

                # Update step status
                if result.get("success"):
                    await self._update_step_status(
                        run.run_id, step.step_id, StepStatus.COMPLETED,
                        output=json.dumps(result.get("output", {})),
                    )
                    run.step_results[step.step_id] = {
                        "status": StepStatus.COMPLETED.value,
                        "output": result.get("output", {}),
                    }
                    # Update context with step output for downstream steps
                    run.context[step.step_id] = result.get("output", {})
                else:
                    await self._update_step_status(
                        run.run_id, step.step_id, StepStatus.FAILED,
                        error=result.get("error", "Unknown error"),
                    )
                    run.step_results[step.step_id] = {
                        "status": StepStatus.FAILED.value,
                        "error": result.get("error"),
                    }
                    # On step failure, mark remaining steps as skipped
                    run.status = RunStatus.FAILED
                    run.error = result.get("error")
                    break

            if run.status == RunStatus.RUNNING:
                run.status = RunStatus.COMPLETED

        except Exception as e:
            run.status = RunStatus.FAILED
            run.error = str(e)
            logger.error(f"Workflow run {run.run_id} failed: {e}")

        finally:
            now = datetime.now(timezone.utc).isoformat()
            run.completed_at = now
            await self.db.execute(
                "UPDATE workflow_runs SET status = ?, completed_at = ?, error = ? WHERE id = ?",
                (run.status.value, now, run.error, run.run_id),
            )
            self._active_runs.pop(run.run_id, None)

    async def _execute_step(
        self,
        step: WorkflowStep,
        run: WorkflowRun,
    ) -> Dict[str, Any]:
        """Execute a single step with retry logic."""
        max_attempts = step.retry_count + 1
        last_error = None

        for attempt in range(max_attempts):
            try:
                await self._update_step_status(
                    run.run_id, step.step_id, StepStatus.RUNNING
                )

                result = await self._execute_step_type(step, run)

                if step.timeout:
                    result = await asyncio.wait_for(
                        self._execute_step_type(step, run),
                        timeout=step.timeout,
                    )

                return {"success": True, "output": result}

            except asyncio.TimeoutError:
                last_error = f"Step {step.step_id} timed out"
                logger.warning(last_error)
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Step {step.step_id} attempt {attempt + 1} failed: {e}")

            if attempt < max_attempts - 1:
                delay = step.retry_delay * (2 ** attempt)  # Exponential backoff
                await asyncio.sleep(delay)

        return {"success": False, "error": last_error}

    async def _execute_step_type(
        self,
        step: WorkflowStep,
        run: WorkflowRun,
    ) -> Dict[str, Any]:
        """Execute a step based on its type."""
        step_type = step.step_type
        config = step.config

        if step_type == StepType.HTTP_REQUEST.value:
            return await self._execute_http_request(config)

        elif step_type == StepType.SERVICE_CALL.value:
            return await self._execute_service_call(config)

        elif step_type == StepType.CONDITION.value:
            return self._execute_condition(config, run)

        elif step_type == StepType.DELAY.value:
            delay = config.get("delay_seconds", 0)
            await asyncio.sleep(delay)
            return {"delayed": delay}

        elif step_type == StepType.NOTIFICATION.value:
            return await self._execute_notification(config)

        elif step_type == StepType.TASK.value:
            return await self._execute_task(config)

        elif step_type == StepType.SCRIPT.value:
            return await self._execute_script(config)

        else:
            raise ValueError(f"Unknown step type: {step_type}")

    async def _execute_http_request(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an HTTP request step."""
        url = config.get("url", "")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body")

        try:
            kwargs: Dict[str, Any] = {"url": url, "headers": headers}
            if body:
                kwargs["json"] = body

            response = await self.http_client.request(method, **kwargs)
            return {
                "status_code": response.status_code,
                "body": response.text,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _execute_service_call(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a service-to-service call."""
        service = config.get("service", "")
        endpoint = config.get("endpoint", "")
        method = config.get("method", "POST").upper()
        body = config.get("body", {})

        service_url = config.get("service_url", f"http://{service}:8080")
        url = f"{service_url}{endpoint}"

        try:
            kwargs: Dict[str, Any] = {"url": url}
            if body:
                kwargs["json"] = body

            response = await self.http_client.request(method, **kwargs)
            return {
                "service": service,
                "status_code": response.status_code,
                "body": response.json() if response.status_code == 200 else response.text,
            }
        except Exception as e:
            return {"error": str(e)}

    def _execute_condition(
        self,
        config: Dict[str, Any],
        run: WorkflowRun,
    ) -> Dict[str, Any]:
        """Evaluate a condition step."""
        condition = config.get("condition", "true")
        result = self._evaluate_condition(condition, run.context, run.step_results)
        return {"condition": condition, "result": result}

    async def _execute_notification(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a notification via Poltergeist."""
        poltergeist_url = config.get("poltergeist_url", "http://Poltergeist:8088")
        channel = config.get("channel", "")
        subject = config.get("subject", "")
        body = config.get("body", "")

        try:
            response = await self.http_client.post(
                f"{poltergeist_url}/api/notifications",
                json={
                    "channel": channel,
                    "subject": subject,
                    "body": body,
                },
            )
            return {
                "status_code": response.status_code,
                "body": response.text,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _execute_task(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create and execute a task via Slinker."""
        slinker_url = config.get("slinker_url", "http://Slinker:8081")
        task_data = config.get("task", {})

        try:
            response = await self.http_client.post(
                f"{slinker_url}/api/v1/tasks",
                json=task_data,
            )
            return {
                "status_code": response.status_code,
                "body": response.json() if response.status_code == 201 else response.text,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _execute_script(
        self, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a script step (placeholder for future implementation)."""
        script = config.get("script", "")
        return {"script": script, "result": "Script execution not yet implemented"}

    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any],
        step_results: Dict[str, Dict[str, Any]],
    ) -> bool:
        """Evaluate a simple condition expression.

        Supports basic comparisons:
        - "step_id == value"
        - "step_id != value"
        - "step_id > value"
        - "step_id < value"
        - "context.key == value"
        - "true" / "false"
        """
        condition = condition.strip().lower()

        if condition in ("true", "yes", "1"):
            return True
        if condition in ("false", "no", "0"):
            return False

        # Parse simple conditions
        operators = ["==", "!=", ">=", "<=", ">", "<"]
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip().strip("'\"")

                    # Resolve left side
                    left_val = self._resolve_value(left, context, step_results)
                    if left_val is None:
                        return False

                    # Compare
                    if op == "==":
                        return str(left_val) == right
                    elif op == "!=":
                        return str(left_val) != right
                    elif op == ">":
                        try:
                            return float(left_val) > float(right)
                        except (ValueError, TypeError):
                            return False
                    elif op == "<":
                        try:
                            return float(left_val) < float(right)
                        except (ValueError, TypeError):
                            return False
                    elif op == ">=":
                        try:
                            return float(left_val) >= float(right)
                        except (ValueError, TypeError):
                            return False
                    elif op == "<=":
                        try:
                            return float(left_val) <= float(right)
                        except (ValueError, TypeError):
                            return False

        return True

    def _resolve_value(
        self,
        key: str,
        context: Dict[str, Any],
        step_results: Dict[str, Dict[str, Any]],
    ) -> Any:
        """Resolve a value from context or step results."""
        # Check context first
        if key in context:
            return context[key]

        # Check step results
        if key in step_results:
            result = step_results[key]
            if isinstance(result, dict):
                return result.get("output", result.get("status"))
            return result

        # Check nested context keys (context.key)
        if "." in key:
            parts = key.split(".", 1)
            if parts[0] in context:
                nested = context[parts[0]]
                if isinstance(nested, dict):
                    return nested.get(parts[1])

        return None

    def _topological_sort(
        self, steps: List[WorkflowStep]
    ) -> List[WorkflowStep]:
        """Sort steps in topological order based on dependencies."""
        step_map = {s.step_id: s for s in steps}
        visited = set()
        result = []

        def visit(step_id: str):
            if step_id in visited:
                return
            visited.add(step_id)
            step = step_map.get(step_id)
            if not step:
                return
            for dep in step.dependencies:
                visit(dep)
            result.append(step)

        for step in steps:
            visit(step.step_id)

        return result

    async def _update_step_status(
        self,
        run_id: str,
        step_id: str,
        status: StepStatus,
        output: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update step status in database."""
        now = datetime.now(timezone.utc).isoformat()
        updates = ["status = ?", "updated_at = ?"]
        values = [status.value, now]

        if output is not None:
            updates.append("output = ?")
            values.append(output)
        if error is not None:
            updates.append("error = ?")
            values.append(error)

        values.extend([run_id, step_id])

        await self.db.execute(
            f"UPDATE workflow_steps SET {', '.join(updates)} "
            "WHERE run_id = ? AND step_id = ?",
            values,
        )

    async def cancel_run(self, run_id: str) -> bool:
        """Cancel a running workflow."""
        row = await self.db.fetchone(
            "SELECT * FROM workflow_runs WHERE id = ? AND status = ?",
            (run_id, RunStatus.RUNNING.value),
        )
        if not row:
            return False

        now = datetime.now(timezone.utc).isoformat()
        await self.db.execute(
            "UPDATE workflow_runs SET status = ?, completed_at = ? WHERE id = ?",
            (RunStatus.CANCELLED.value, now, run_id),
        )

        # Cancel the async task
        task = self._active_runs.pop(run_id, None)
        if task and not task.done():
            task.cancel()

        return True

    async def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow run."""
        row = await self.db.fetchone(
            "SELECT * FROM workflow_runs WHERE id = ?",
            (run_id,),
        )
        if not row:
            return None

        steps = await self.db.fetchall(
            "SELECT * FROM workflow_steps WHERE run_id = ? ORDER BY order_index",
            (run_id,),
        )

        return {
            **row,
            "trigger_data": json.loads(row.get("trigger_data", "{}")),
            "context": json.loads(row.get("context", "{}")),
            "steps": steps,
        }

    async def list_runs(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List workflow runs with optional filtering."""
        query = "SELECT * FROM workflow_runs WHERE 1=1"
        params = []

        if workflow_id:
            query += " AND workflow_id = ?"
            params.append(workflow_id)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        rows = await self.db.fetchall(query, params)
        return [
            {**row, "trigger_data": json.loads(row.get("trigger_data", "{}"))}
            for row in rows
        ]

    async def handle_webhook(
        self, webhook_id: str, payload: Dict[str, Any]
    ) -> Optional[str]:
        """Handle an incoming webhook and trigger the associated workflow.

        Returns the run_id if a workflow was triggered, None otherwise.
        """
        row = await self.db.fetchone(
            "SELECT * FROM webhooks WHERE id = ? AND enabled = 1",
            (webhook_id,),
        )
        if not row:
            return None

        workflow_id = row["workflow_id"]
        trigger_data = {
            "webhook_id": webhook_id,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Log the webhook event
        await self.db.execute(
            """INSERT INTO webhook_events
               (id, webhook_id, payload, status, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                webhook_id,
                json.dumps(payload),
                "triggered",
                trigger_data["timestamp"],
            ),
        )

        # Trigger the workflow
        try:
            run_id = await self.execute_workflow(
                workflow_id=workflow_id,
                trigger_type=TriggerType.WEBHOOK.value,
                trigger_data=trigger_data,
                context=payload,
            )
            return run_id
        except Exception as e:
            logger.error(f"Webhook {webhook_id} failed to trigger workflow: {e}")
            return None
