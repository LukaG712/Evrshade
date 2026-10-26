"""Greenie — Task Orchestration Engine.

Provides task decomposition, agent capability discovery, task delegation,
multi-agent coordination, retry policies, cancellation, and failure recovery.

Usage:

    from app.orchestrator import TaskOrchestrator

    orchestrator = TaskOrchestrator(slinker_url="http://Slinker:8081")
    task_id = await orchestrator.create_task(...)
    await orchestrator.execute_task(task_id)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from evershade.errors import EvershadeError
from app.database import get_db_instance

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Configurable retry policy with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        retryable_errors: Optional[List[str]] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.retryable_errors = retryable_errors or [
            "timeout",
            "service_unavailable",
            "gateway_timeout",
            "internal_error",
        ]

    def should_retry(self, attempt: int, error: Optional[str] = None) -> bool:
        if attempt >= self.max_retries:
            return False
        if error and self.retryable_errors:
            return error.lower() in self.retryable_errors
        return True

    def delay_for_attempt(self, attempt: int) -> float:
        delay = self.base_delay * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay)


class AgentCapability:
    """Represents an agent's capabilities for task selection."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str],
        model: str,
        autonomy_level: str = "supervised",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.model = model
        self.autonomy_level = autonomy_level
        self.metadata = metadata or {}

    def matches_requirements(self, required_capabilities: List[str]) -> bool:
        """Check if agent has all required capabilities."""
        return all(cap in self.capabilities for cap in required_capabilities)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "model": self.model,
            "autonomy_level": self.autonomy_level,
            "metadata": self.metadata,
        }


class TaskOrchestrator:
    """
    Central task orchestration engine.

    Handles:
    - Task decomposition into subtasks
    - Agent capability discovery and selection
    - Task delegation to Slinker
    - Multi-agent coordination
    - Retry policies with exponential backoff
    - Cancellation support
    - Failure recovery with checkpoint resume
    - Shared project context
    """

    def __init__(
        self,
        slinker_url: str = "http://Slinker:8081",
        retry_policy: Optional[RetryPolicy] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.slinker_url = slinker_url.rstrip("/")
        self.retry_policy = retry_policy or RetryPolicy()
        self._http_client = http_client
        self._cancel_events: Dict[str, asyncio.Event] = {}
        self._active_tasks: Dict[str, asyncio.Task] = {}

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=300.0)
        return self._http_client

    # ── Task Creation & Decomposition ──────────────────────────────────

    async def create_task(
        self,
        title: str,
        description: str,
        agent_id: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        priority: int = 5,
        project_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new task and decompose it into subtasks."""
        task_id = str(uuid.uuid4())
        db = await get_db_instance()

        # Select best agent if not specified
        selected_agent_id = agent_id
        if not selected_agent_id and required_capabilities:
            selected_agent_id = await self._select_agent(required_capabilities)

        # Insert main task
        await db.execute(
            """INSERT INTO tasks (id, title, description, agent_id, required_capabilities,
                                 priority, project_id, mission_id, status, metadata,
                                 created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)""",
            (
                task_id,
                title,
                description,
                selected_agent_id,
                json.dumps(required_capabilities or []),
                priority,
                project_id,
                mission_id,
                json.dumps(metadata or {}),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        # Decompose into subtasks
        subtasks = await self._decompose_task(
            task_id, title, description, required_capabilities or []
        )
        for i, subtask in enumerate(subtasks):
            subtask_id = str(uuid.uuid4())
            await db.execute(
                """INSERT INTO subtasks (id, task_id, title, description, required_capabilities,
                                        dependency_ids, order_index, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
                (
                    subtask_id,
                    task_id,
                    subtask["title"],
                    subtask["description"],
                    json.dumps(subtask.get("required_capabilities", [])),
                    json.dumps(subtask.get("dependency_ids", [])),
                    i,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

        return task_id

    async def _decompose_task(
        self,
        task_id: str,
        title: str,
        description: str,
        required_capabilities: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Decompose a task into executable subtasks.

        Uses rule-based decomposition based on capabilities and task description.
        In production, this would delegate to an LLM for intelligent decomposition.
        """
        subtasks = []

        has_coding = "coding" in required_capabilities
        has_testing = "testing" in required_capabilities
        has_browser = "browser" in required_capabilities
        has_analysis = "analysis" in required_capabilities

        if has_analysis:
            subtasks.append({
                "title": f"Analyze: {title}",
                "description": f"Analyze requirements for: {description}",
                "required_capabilities": ["analysis"],
                "dependency_ids": [],
            })

        if has_coding:
            coding_deps = [subtasks[0]["title"]] if subtasks else []
            subtasks.append({
                "title": f"Implement: {title}",
                "description": f"Implement solution for: {description}",
                "required_capabilities": ["coding"],
                "dependency_ids": coding_deps,
            })

        if has_testing:
            test_deps = [s["title"] for s in subtasks if "Implement" in s["title"]]
            subtasks.append({
                "title": f"Test: {title}",
                "description": f"Write and run tests for: {description}",
                "required_capabilities": ["testing"],
                "dependency_ids": test_deps,
            })

        if has_browser:
            browser_deps = [s["title"] for s in subtasks if "Implement" in s["title"]]
            subtasks.append({
                "title": f"Browser verification: {title}",
                "description": f"Verify in browser: {description}",
                "required_capabilities": ["browser"],
                "dependency_ids": browser_deps,
            })

        # If no specific capabilities, create a single generic subtask
        if not subtasks:
            subtasks.append({
                "title": title,
                "description": description,
                "required_capabilities": required_capabilities,
                "dependency_ids": [],
            })

        return subtasks

    # ── Agent Selection ────────────────────────────────────────────────

    async def _select_agent(self, required_capabilities: List[str]) -> Optional[str]:
        """Select the best agent for the required capabilities."""
        db = await get_db_instance()
        agents = await db.fetchall(
            "SELECT * FROM agents WHERE status = 'active' ORDER BY created_at DESC"
        )

        if not agents:
            return None

        for agent in agents:
            capabilities = json.loads(agent.get("capabilities", "[]"))
            if all(cap in capabilities for cap in required_capabilities):
                return agent["id"]

        return agents[0]["id"] if agents else None

    async def discover_agents(
        self,
        required_capabilities: Optional[List[str]] = None,
    ) -> List[AgentCapability]:
        """Discover agents matching the required capabilities."""
        db = await get_db_instance()
        agents = await db.fetchall(
            "SELECT * FROM agents WHERE status = 'active'"
        )

        result = []
        for agent in agents:
            caps = json.loads(agent.get("capabilities", "[]"))
            if required_capabilities:
                if not all(cap in caps for cap in required_capabilities):
                    continue
            result.append(AgentCapability(
                agent_id=agent["id"],
                name=agent["name"],
                capabilities=caps,
                model=agent.get("model", "unknown"),
                autonomy_level=agent.get("autonomy_level", "supervised"),
                metadata=json.loads(agent.get("metadata", "{}")),
            ))
        return result

    # ── Task Execution ─────────────────────────────────────────────────

    async def execute_task(self, task_id: str) -> str:
        """Start executing a task and its subtasks."""
        db = await get_db_instance()
        await db.execute(
            """UPDATE tasks SET status = 'running', updated_at = ? WHERE id = ?""",
            (datetime.now(timezone.utc).isoformat(), task_id),
        )

        self._cancel_events[task_id] = asyncio.Event()
        task = asyncio.create_task(self._execute_task_loop(task_id))
        self._active_tasks[task_id] = task

        return task_id

    async def _execute_task_loop(self, task_id: str) -> None:
        """Execute all subtasks in dependency order with retry logic."""
        db = await get_db_instance()
        subtasks = await db.fetchall(
            "SELECT * FROM subtasks WHERE task_id = ? ORDER BY order_index",
            (task_id,),
        )

        completed = set()
        failed_subtasks = []

        for subtask in subtasks:
            cancel_event = self._cancel_events.get(task_id)
            if cancel_event and cancel_event.is_set():
                await self._cancel_task(task_id)
                return

            subtask_id = subtask["id"]
            deps = json.loads(subtask.get("dependency_ids", "[]"))
            if not all(dep in completed for dep in deps):
                logger.warning(f"Subtask {subtask_id} has unmet dependencies, skipping")
                await db.execute(
                    """UPDATE subtasks SET status = 'skipped', completed_at = ?
                       WHERE id = ?""",
                    (datetime.now(timezone.utc).isoformat(), subtask_id),
                )
                continue

            success = await self._execute_subtask_with_retry(task_id, subtask)
            if success:
                completed.add(subtask_id)
            else:
                failed_subtasks.append(subtask)

        if failed_subtasks:
            await db.execute(
                """UPDATE tasks SET status = 'partial', updated_at = ? WHERE id = ?""",
                (datetime.now(timezone.utc).isoformat(), task_id),
            )
        else:
            await db.execute(
                """UPDATE tasks SET status = 'completed', completed_at = ?, updated_at = ?
                   WHERE id = ?""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    task_id,
                ),
            )

        self._cancel_events.pop(task_id, None)
        self._active_tasks.pop(task_id, None)

    async def _execute_subtask_with_retry(
        self,
        task_id: str,
        subtask: Dict[str, Any],
    ) -> bool:
        """Execute a subtask with retry policy."""
        subtask_id = subtask["id"]
        attempt = 0
        last_error = None

        while True:
            cancel_event = self._cancel_events.get(task_id)
            if cancel_event and cancel_event.is_set():
                return False

            db = await get_db_instance()
            await db.execute(
                """UPDATE subtasks SET status = 'running', attempt = ?,
                   updated_at = ? WHERE id = ?""",
                (attempt + 1, datetime.now(timezone.utc).isoformat(), subtask_id),
            )

            try:
                result = await self._delegate_to_slinker(task_id, subtask)
                await db.execute(
                    """UPDATE subtasks SET status = 'completed', result_data = ?,
                       completed_at = ?, updated_at = ? WHERE id = ?""",
                    (
                        json.dumps(result),
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                        subtask_id,
                    ),
                )

                result_id = str(uuid.uuid4())
                await db.execute(
                    """INSERT INTO task_results (id, task_id, subtask_id, status, output,
                                                error, exit_code, created_at)
                       VALUES (?, ?, ?, 'success', ?, ?, ?, ?)""",
                    (
                        result_id,
                        task_id,
                        subtask_id,
                        json.dumps(result.get("output", "")),
                        None,
                        result.get("exit_code", 0),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )

                return True

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Subtask {subtask_id} attempt {attempt + 1} failed: {last_error}"
                )

                if not self.retry_policy.should_retry(attempt, last_error):
                    break

                delay = self.retry_policy.delay_for_attempt(attempt)
                logger.info(f"Retrying subtask {subtask_id} in {delay}s...")
                await asyncio.sleep(delay)
                attempt += 1

        await db.execute(
            """UPDATE subtasks SET status = 'failed', error = ?,
               completed_at = ?, updated_at = ? WHERE id = ?""",
            (
                last_error,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
                subtask_id,
            ),
        )

        result_id = str(uuid.uuid4())
        await db.execute(
            """INSERT INTO task_results (id, task_id, subtask_id, status, output,
                                        error, exit_code, created_at)
               VALUES (?, ?, ?, 'error', ?, ?, ?, ?)""",
            (
                result_id,
                task_id,
                subtask_id,
                None,
                last_error,
                -1,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        return False

    async def _delegate_to_slinker(
        self,
        task_id: str,
        subtask: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delegate a subtask to Slinker for execution."""
        required_caps = json.loads(subtask.get("required_capabilities", "[]"))
        adapter = "junie" if "coding" in required_caps else "subprocess"

        payload = {
            "title": subtask["title"],
            "description": subtask["description"],
            "adapter": adapter,
            "timeout": 300,
            "metadata": {
                "task_id": task_id,
                "subtask_id": subtask["id"],
            },
        }

        response = await self.http_client.post(
            f"{self.slinker_url}/api/v1/tasks",
            json=payload,
            timeout=300.0,
        )

        if response.status_code not in (200, 201):
            raise EvershadeError.service_unavailable(
                f"Slinker failed: {response.text}"
            )

        result = response.json()
        task_ref = result.get("id", "")
        return await self._poll_slinker_task(task_ref)

    async def _poll_slinker_task(
        self, task_ref: str, timeout: float = 300.0
    ) -> Dict[str, Any]:
        """Poll Slinker for task completion."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                response = await self.http_client.get(
                    f"{self.slinker_url}/api/v1/tasks/{task_ref}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status", "")
                    if status in ("completed", "failed", "error"):
                        return {
                            "output": result.get("output", ""),
                            "error": result.get("error"),
                            "exit_code": result.get("exit_code", 0),
                            "file_changes": result.get("file_changes", []),
                        }
                await asyncio.sleep(2)
            except Exception:
                await asyncio.sleep(2)

        raise EvershadeError.gateway_timeout("Slinker task timed out")

    # ── Cancellation ───────────────────────────────────────────────────

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        cancel_event = self._cancel_events.get(task_id)
        if cancel_event:
            cancel_event.set()
            return True

        db = await get_db_instance()
        task = await db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if task and task["status"] in ("pending", "running"):
            await db.execute(
                """UPDATE tasks SET status = 'cancelled',
                   completed_at = ?, updated_at = ? WHERE id = ?""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    task_id,
                ),
            )
            await db.execute(
                """UPDATE subtasks SET status = 'cancelled',
                   completed_at = ?, updated_at = ?
                   WHERE task_id = ? AND status IN ('pending', 'running')""",
                (
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    task_id,
                ),
            )
            return True

        return False

    async def _cancel_task(self, task_id: str) -> None:
        """Internal cancellation handler."""
        db = await get_db_instance()
        await db.execute(
            """UPDATE tasks SET status = 'cancelled',
               completed_at = ?, updated_at = ? WHERE id = ?""",
            (
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
                task_id,
            ),
        )
        await db.execute(
            """UPDATE subtasks SET status = 'cancelled',
               completed_at = ?, updated_at = ?
               WHERE task_id = ? AND status IN ('pending', 'running')""",
            (
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
                task_id,
            ),
        )

    # ── Retry & Recovery ───────────────────────────────────────────────

    async def retry_task(self, task_id: str) -> str:
        """Retry a failed task from the last failed subtask."""
        db = await get_db_instance()
        await db.execute(
            """UPDATE tasks SET status = 'pending', completed_at = NULL,
               updated_at = ? WHERE id = ?""",
            (datetime.now(timezone.utc).isoformat(), task_id),
        )
        await db.execute(
            """UPDATE subtasks SET status = 'pending', error = NULL,
               attempt = 0, completed_at = NULL, result_data = NULL,
               updated_at = ? WHERE task_id = ? AND status = 'failed'""",
            (datetime.now(timezone.utc).isoformat(), task_id),
        )
        return await self.execute_task(task_id)

    # ── Query ──────────────────────────────────────────────────────────

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task details with subtasks."""
        db = await get_db_instance()
        task = await db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
        if not task:
            return None

        task = dict(task)
        task["required_capabilities"] = json.loads(
            task.get("required_capabilities", "[]")
        )
        task["metadata"] = json.loads(task.get("metadata", "{}"))

        subtasks = await db.fetchall(
            "SELECT * FROM subtasks WHERE task_id = ? ORDER BY order_index",
            (task_id,),
        )
        for st in subtasks:
            st["required_capabilities"] = json.loads(
                st.get("required_capabilities", "[]")
            )
            st["dependency_ids"] = json.loads(st.get("dependency_ids", "[]"))
            st["result_data"] = (
                json.loads(st["result_data"]) if st.get("result_data") else None
            )

        task["subtasks"] = subtasks
        return task

    async def list_tasks(
        self,
        status: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering."""
        db = await get_db_instance()
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        tasks = await db.fetchall(query, params)
        for task in tasks:
            task["required_capabilities"] = json.loads(
                task.get("required_capabilities", "[]")
            )
            task["metadata"] = json.loads(task.get("metadata", "{}"))
        return tasks

    async def get_task_results(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all results for a task."""
        db = await get_db_instance()
        results = await db.fetchall(
            "SELECT * FROM task_results WHERE task_id = ? ORDER BY created_at",
            (task_id,),
        )
        for r in results:
            r["output"] = (
                json.loads(r["output"]) if r.get("output") else None
            )
        return results
