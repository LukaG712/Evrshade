"""Slinker — Junie CLI Coding Agent Adapter.

Integrates with Junie CLI for coding agent execution.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import UTC, datetime
from typing import Any, AsyncGenerator

from . import (
    CodingAgentAdapter,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)

logger = logging.getLogger(__name__)


class JunieAdapter(CodingAgentAdapter):
    """
    Coding agent adapter using Junie CLI.

    Executes coding tasks via the Junie CLI with workspace isolation,
    file access control, and structured result reporting.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.junie_path = self.config.get("junie_path", "junie")
        self.junie_args = self.config.get("junie_args", [])

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """Execute a coding task using Junie CLI."""
        start = time.time()
        task_id = request.task_id

        self._track_task(task_id, asyncio.current_task())

        try:
            # Capture files before execution
            before_files = set()
            if os.path.isdir(request.workspace_path):
                for root, dirs, files in os.walk(request.workspace_path):
                    for f in files:
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, request.workspace_path)
                        before_files.add(rel_path)

            # Build Junie command
            prompt = self._build_prompt(request)
            cmd_parts = (
                [self.junie_path]
                + self.junie_args
                + [
                    "--non-interactive",
                    f"--workspace={request.workspace_path}",
                    "--prompt",
                    prompt,
                ]
            )

            # Run Junie
            output_parts = []
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=request.workspace_path,
            )

            # Stream output
            if process.stdout:
                async for line in process.stdout:
                    text = line.decode("utf-8", errors="replace").strip()
                    if text:
                        output_parts.append(text)
                        if self.is_cancelled(task_id):
                            process.kill()
                            break

            stdout, stderr = await process.communicate()
            stdout_text = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_text = stderr.decode("utf-8", errors="replace") if stderr else ""

            # Capture file changes
            file_changes = await self.capture_file_changes(
                request.workspace_path, before_files
            )

            duration = int((time.time() - start) * 1000)
            success = process.returncode == 0

            status = ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED
            if self.is_cancelled(task_id):
                status = ExecutionStatus.CANCELLED

            return ExecutionResult(
                task_id=task_id,
                status=status.value,
                output=stdout_text or "\n".join(output_parts),
                error=stderr_text if not success else None,
                exit_code=process.returncode,
                file_changes=file_changes,
                duration_ms=duration,
                metadata={
                    "adapter": "junie",
                    "command": " ".join(cmd_parts),
                },
            )

        except TimeoutError:
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                task_id=task_id,
                status=ExecutionStatus.TIMEOUT.value,
                error=f"Junie execution timed out after {request.timeout}s",
                exit_code=-1,
                duration_ms=duration,
                metadata={"adapter": "junie"},
            )
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                task_id=task_id,
                status=ExecutionStatus.FAILED.value,
                error=str(e),
                exit_code=-1,
                duration_ms=duration,
                metadata={"adapter": "junie"},
            )
        finally:
            self._cleanup_task(task_id)

    async def stream_progress(
        self,
        task_id: str,
    ) -> AsyncGenerator[str, None]:
        """Stream progress updates."""
        # Progress is streamed via the execute method's output
        # This endpoint polls for status updates
        while not self.is_cancelled(task_id):
            yield json.dumps(
                {
                    "task_id": task_id,
                    "status": "running",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            await asyncio.sleep(2)

    def _build_prompt(self, request: ExecutionRequest) -> str:
        """Build the prompt for Junie CLI."""
        parts = [request.title, request.description]

        if request.files:
            parts.append("\nFocus on these files:\n" + "\n".join(request.files))

        if request.permissions:
            perms = request.permissions
            if not perms.get("file_write", True):
                parts.append("\nRead-only mode: do not modify files.")
            if not perms.get("execute", True):
                parts.append("\nNo execution: do not run commands.")

        return "\n".join(parts)
