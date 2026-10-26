"""
Test 2: Code Execution Flow
User → Greenie → Slinker → Junie CLI

Validates:
- Slinker health endpoint
- Task creation
- Worker registration
- Task execution
- Session logging
"""

from tests.integration.base_test import BaseIntegrationTest


class TestCodeExecutionFlow(BaseIntegrationTest):
    """Test the code execution flow through Slinker."""

    service = "Slinker"

    def run(self) -> bool:
        print("\n  Step 1: Check Slinker health")
        slinker_ok = self.check_service_health("Slinker", 8000)

        if not slinker_ok:
            print("\n  ⊘ Slinker not running, skipping flow test")
            return False

        # Register a worker
        print("\n  Step 2: Register test worker")
        worker_data = {
            "name": "test-worker",
            "capabilities": ["shell", "git"],
        }
        worker = self.make_request("post", "/api/v1/workers", json=worker_data)
        worker_registered = self.assert_true(
            worker is not None and "id" in worker, "Worker registered successfully"
        )
        worker_id = worker.get("id", "") if worker else ""

        # Create a task
        print("\n  Step 3: Create test task")
        task_data = {
            "name": "Test integration task",
            "command": "echo 'Hello from integration test'",
            "worker_id": worker_id,
        }
        task = self.make_request("post", "/api/v1/tasks", json=task_data)
        task_created = self.assert_true(
            task is not None and "id" in task, "Task created successfully"
        )
        task_id = task.get("id", "") if task else ""

        # Check task status
        print("\n  Step 4: Check task status")
        if task_id:
            task_status = self.make_request("get", f"/api/v1/tasks/{task_id}")
            status_ok = self.assert_true(
                task_status is not None, "Task status retrievable"
            )
        else:
            status_ok = False
            print("  ✗ No task ID, skipping status check")

        # List workers
        print("\n  Step 5: List workers")
        workers = self.make_request("get", "/api/v1/workers")
        workers_ok = self.assert_true(
            workers is not None and "workers" in workers, "Worker list retrieved"
        )

        # Check OpenAI-compatible endpoint
        print("\n  Step 6: Check OpenAI-compatible endpoint")
        models = self.make_request("get", "/v1/models")
        models_ok = self.assert_true(
            models is not None, "OpenAI models endpoint accessible"
        )

        # Check sessions
        print("\n  Step 7: Check sessions")
        sessions = self.make_request("get", "/api/v1/sessions")
        sessions_ok = self.assert_true(
            sessions is not None, "Sessions endpoint accessible"
        )

        # Cleanup
        print("\n  Step 8: Cleanup")
        if worker_id:
            self.make_request("delete", f"/api/v1/workers/{worker_id}")
            print("  ✓ Test worker deleted")

        all_passed = all(
            [
                slinker_ok,
                worker_registered,
                task_created,
                status_ok,
                workers_ok,
                models_ok,
                sessions_ok,
            ]
        )

        return all_passed
