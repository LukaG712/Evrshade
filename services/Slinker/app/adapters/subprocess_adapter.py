"""Slinker — Subprocess Coding Agent Adapter.

Simple adapter that runs shell commands directly.
Used as fallback when no coding agent is available.
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


class SubprocessAdapter(CodingAgentAdapter):
    """
    Simple coding agent adapter using shell commands.

    Executes commands directly in the workspace without an AI agent.
    Useful for simple tasks like running tests, linters, or build scripts.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """Execute commands in the workspace."""
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

            # Build command from description
            commands = request.commands or [request.description]
            output_parts = []
            all_stderr = []
            last_returncode = 0

            for cmd in commands:
                if self.is_cancelled(task_id):
                    break

                result = await self.run_command(
                    cmd,
                    request.workspace_path,
                    timeout=request.timeout,
                    task_id=task_id,
                )
                output_parts.append(f"$ {cmd}")
                output_parts.append(result["stdout"])
                if result["stderr"]:
                    all_stderr.append(result["stderr"])
                last_returncode = result["returncode"]

                if last_returncode != 0:
                    logger.warning(f"Command failed with code {last_returncode}: {cmd}")

            # Capture file changes
            file_changes = await self.capture_file_changes(
                request.workspace_path, before_files
            )

            duration = int((time.time() - start) * 1000)
            success = last_returncode == 0

            status = ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED
            if self.is_cancelled(task_id):
                status = ExecutionStatus.CANCELLED

            return ExecutionResult(
                task_id=task_id,
                status=status.value,
                output="\n".join(output_parts),
                error="\n".join(all_stderr) if not success else None,
                exit_code=last_returncode,
                file_changes=file_changes,
                duration_ms=duration,
                metadata={
                    "adapter": "subprocess",
                    "commands": commands,
                },
            )

        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return ExecutionResult(
                task_id=task_id,
                status=ExecutionStatus.FAILED.value,
                error=str(e),
                exit_code=-1,
                duration_ms=duration,
                metadata={"adapter": "subprocess"},
            )
        finally:
            self._cleanup_task(task_id)

    async def stream_progress(
        self,
        task_id: str,
    ) -> AsyncGenerator[str, None]:
        """Stream progress updates."""
        while not self.is_cancelled(task_id):
            yield json.dumps(
                {
                    "task_id": task_id,
                    "status": "running",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            await asyncio.sleep(2)
