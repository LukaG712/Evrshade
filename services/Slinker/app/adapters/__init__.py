"""Slinker — Coding Agent Adapter Base Class.

Defines the interface that all coding agent backends must implement.
New coding agents can be added by creating a new adapter class.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import shlex
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)

# Dangerous shell metacharacters that enable command injection
_DANGEROUS_CHARS = re.compile(r"[;&|`$(){}!\\\n\r]")

# Allowed commands for safe execution
ALLOWED_COMMANDS = {
    "python",
    "python3",
    "pip",
    "pip3",
    "node",
    "npm",
    "npx",
    "git",
    "make",
    "cmake",
    "pytest",
    "ruff",
    "black",
    "mypy",
    "cargo",
    "go",
    "rustc",
    "java",
    "javac",
    "mvn",
    "gradle",
    "docker",
    "docker-compose",
    "ls",
    "cat",
    "head",
    "tail",
    "grep",
    "find",
    "echo",
    "date",
    "pwd",
    "whoami",
    "curl",
    "wget",
    "tar",
    "zip",
    "unzip",
    "chmod",
    "chown",
    "rm",
    "cp",
    "mv",
    "mkdir",
    "python -m pytest",
    "python -m ruff",
}


def validate_command(command: str) -> str:
    """Validate a shell command for safety.

    Checks for dangerous shell metacharacters and validates the command
    is in the allowlist. Raises ValueError if the command is unsafe.

    Args:
        command: The shell command to validate.

    Returns:
        The validated command string.

    Raises:
        ValueError: If the command contains dangerous patterns.
    """
    if not command or not command.strip():
        raise ValueError("Empty command is not allowed")

    # Extract the base command (first word)
    try:
        parts = shlex.split(command)
        base_cmd = parts[0] if parts else ""
        # Handle commands like "python -m pytest"
        if base_cmd == "python" and len(parts) > 2 and parts[1] == "-m":
            base_cmd = f"python -m {parts[2]}"
    except ValueError:
        # shlex.split can fail on malformed input - fall back to simple split
        base_cmd = command.split()[0] if command.split() else ""

    # Check for dangerous shell metacharacters
    if _DANGEROUS_CHARS.search(command):
        raise ValueError(
            f"Command contains dangerous characters: {_DANGEROUS_CHARS.search(command).group()}"
        )

    # Check if the base command is allowed
    base_name = os.path.basename(base_cmd)
    if base_name not in ALLOWED_COMMANDS and base_cmd not in ALLOWED_COMMANDS:
        raise ValueError(
            f"Command '{base_name}' is not in the allowlist. "
            f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
        )

    return command


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class FileChange:
    """Represents a file modification made by a coding agent."""

    path: str
    action: str  # "created", "modified", "deleted"
    diff: str | None = None
    content: str | None = None


@dataclass
class ExecutionResult:
    """Structured result from a coding agent execution."""

    task_id: str
    status: str
    output: str = ""
    error: str | None = None
    exit_code: int = 0
    file_changes: list[FileChange] = field(default_factory=list)
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "exit_code": self.exit_code,
            "file_changes": [
                {
                    "path": fc.path,
                    "action": fc.action,
                    "diff": fc.diff,
                }
                for fc in self.file_changes
            ],
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionRequest:
    """Request to execute a coding task."""

    task_id: str
    title: str
    description: str
    workspace_path: str
    files: list[str] | None = None  # Files to focus on
    commands: list[str] | None = None  # Commands to run after
    timeout: int = 300
    permissions: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class CodingAgentAdapter(ABC):
    """
    Base class for coding agent adapters.

    Subclasses implement:
    - execute(): Run the coding task
    - stream_progress(): Yield progress updates
    - cancel(): Cancel a running task
    - get_status(): Check task status

    Each adapter handles:
    - Workspace isolation
    - File access control
    - Test/lint/build execution
    - Streaming progress
    - Timeout handling
    - Structured result reporting
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._active_tasks: dict[str, asyncio.Task] = {}
        self._cancel_events: dict[str, asyncio.Event] = {}

    @abstractmethod
    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """Execute a coding task and return structured results."""

    @abstractmethod
    async def stream_progress(
        self,
        task_id: str,
    ) -> AsyncGenerator[str, None]:
        """Stream progress updates as SSE events."""

    async def cancel(self, task_id: str) -> bool:
        """Cancel a running task."""
        event = self._cancel_events.get(task_id)
        if event:
            event.set()
            return True
        return False

    def is_cancelled(self, task_id: str) -> bool:
        """Check if a task has been cancelled."""
        event = self._cancel_events.get(task_id)
        return event is not None and event.is_set()

    def _track_task(self, task_id: str, task: asyncio.Task) -> None:
        """Track an active task for cancellation."""
        self._cancel_events[task_id] = asyncio.Event()
        self._active_tasks[task_id] = task

    def _cleanup_task(self, task_id: str) -> None:
        """Clean up task tracking."""
        self._cancel_events.pop(task_id, None)
        self._active_tasks.pop(task_id, None)

    async def run_with_timeout(
        self,
        coro,
        timeout: float,
        task_id: str,
    ) -> Any:
        """Run a coroutine with timeout and cancellation support."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except TimeoutError:
            raise TimeoutError(f"Task {task_id} timed out after {timeout}s")
        except asyncio.CancelledError:
            raise asyncio.CancelledError(f"Task {task_id} was cancelled")

    async def capture_file_changes(
        self,
        workspace_path: str,
        before_files: set | None = None,
    ) -> list[FileChange]:
        """Capture file changes in a workspace."""
        changes = []
        if not os.path.isdir(workspace_path):
            return changes

        current_files = set()
        for root, dirs, files in os.walk(workspace_path):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, workspace_path)
                current_files.add(rel_path)

        # New files
        if before_files:
            new_files = current_files - before_files
            for path in new_files:
                full_path = os.path.join(workspace_path, path)
                try:
                    content = await asyncio.get_running_loop().run_in_executor(
                        None, self._read_file, full_path
                    )
                    changes.append(
                        FileChange(
                            path=path,
                            action="created",
                            content=content,
                        )
                    )
                except Exception:
                    pass

            # Deleted files
            deleted_files = before_files - current_files
            for path in deleted_files:
                changes.append(
                    FileChange(
                        path=path,
                        action="deleted",
                    )
                )

        return changes

    async def run_command(
        self,
        command: str,
        workspace_path: str,
        timeout: int = 60,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """Run a shell command in the workspace.

        Validates the command for safety before execution to prevent
        command injection attacks.
        """
        # Validate command safety
        try:
            validate_command(command)
        except ValueError as e:
            return {
                "stdout": "",
                "stderr": f"Command rejected for safety: {e}",
                "returncode": -1,
                "duration_ms": 0,
            }

        start = time.time()
        process = None
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace_path,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            duration = int((time.time() - start) * 1000)
            return {
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "returncode": process.returncode,
                "duration_ms": duration,
            }
        except TimeoutError:
            if process:
                process.kill()
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "returncode": -1,
                "duration_ms": timeout * 1000,
            }

    async def run_tests(
        self,
        workspace_path: str,
        test_command: str | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Run tests in the workspace."""
        if test_command:
            cmd = test_command
        elif os.path.exists(os.path.join(workspace_path, "pytest.ini")):
            cmd = "python -m pytest -x --tb=short"
        elif os.path.exists(os.path.join(workspace_path, "package.json")):
            cmd = "npm test -- --reporter=dot"
        else:
            cmd = "python -m pytest -x --tb=short"

        result = await self.run_command(cmd, workspace_path, timeout)
        passed = result["returncode"] == 0
        return {
            "passed": passed,
            "output": result["stdout"],
            "error": result["stderr"],
            "returncode": result["returncode"],
        }

    async def run_lint(
        self,
        workspace_path: str,
        lint_command: str | None = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Run linter in the workspace."""
        if lint_command:
            cmd = lint_command
        elif os.path.exists(os.path.join(workspace_path, "pyproject.toml")):
            cmd = "python -m ruff check ."
        elif os.path.exists(os.path.join(workspace_path, "package.json")):
            cmd = "npm run lint"
        else:
            cmd = "python -m py_compile ."

        result = await self.run_command(cmd, workspace_path, timeout)
        passed = result["returncode"] in (0, 1)  # Some linters return 1 for warnings
        return {
            "passed": passed,
            "output": result["stdout"],
            "error": result["stderr"],
            "returncode": result["returncode"],
        }

    async def run_build(
        self,
        workspace_path: str,
        build_command: str | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Run build in the workspace."""
        if build_command:
            cmd = build_command
        elif os.path.exists(os.path.join(workspace_path, "setup.py")):
            cmd = "python setup.py build"
        elif os.path.exists(os.path.join(workspace_path, "package.json")):
            cmd = "npm run build"
        elif os.path.exists(os.path.join(workspace_path, "Makefile")):
            cmd = "make"
        else:
            return {
                "passed": True,
                "output": "No build system detected",
                "returncode": 0,
            }

        result = await self.run_command(cmd, workspace_path, timeout)
        passed = result["returncode"] == 0
        return {
            "passed": passed,
            "output": result["stdout"],
            "error": result["stderr"],
            "returncode": result["returncode"],
        }
