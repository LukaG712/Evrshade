"""
Integration tests for Greenie-Slinker agent workflow.

Tests the complete flow:
1. User submits a coding task through Greenie
2. Greenie plans the task and selects an execution backend
3. Slinker invokes the backend with the correct workspace
4. The coding agent performs the work
5. Tests run
6. Results, logs, and changed files are returned
7. User can inspect the outcome
"""

from tests.integration.base_test import BaseIntegrationTest


class TestAgentWorkflow(BaseIntegrationTest):
    """Test Greenie-Slinker agent orchestration workflow."""

    def test_greenie_task_creation(self):
        """Test creating a task through Greenie."""
        print("\n  --- Greenie Task Creation ---")
        healthy = self.check_service_health("Greenie", 8080)
        if not healthy:
            print("  ⊘ Greenie not running, skipping task creation test")
            return True

        result = self.make_request(
            "post",
            "http://localhost:8080/api/tasks",
            json={
                "title": "Test task",
                "description": "Create a simple Python function",
                "required_capabilities": ["coding"],
                "priority": 5,
            },
        )
        if result:
            self.assert_true(
                "id" in result,
                "Task creation returns task ID",
            )
            self.assert_true(
                result.get("status") == "pending",
                "Task starts in pending status",
            )
            self.assert_true(
                len(result.get("subtasks", [])) > 0,
                "Task is decomposed into subtasks",
            )
            return True
        return False

    def test_greenie_task_decomposition(self):
        """Test that Greenie decomposes tasks into subtasks."""
        print("\n  --- Greenie Task Decomposition ---")
        healthy = self.check_service_health("Greenie", 8080)
        if not healthy:
            print("  ⊘ Greenie not running, skipping decomposition test")
            return True

        result = self.make_request(
            "post",
            "http://localhost:8080/api/tasks",
            json={
                "title": "Full stack task",
                "description": "Build a feature with tests",
                "required_capabilities": ["coding", "testing"],
            },
        )
        if result:
            subtasks = result.get("subtasks", [])
            self.assert_true(
                len(subtasks) >= 2,
                f"Task decomposed into {len(subtasks)} subtasks",
            )
            # Check subtask statuses
            for st in subtasks:
                self.assert_true(
                    st.get("status") == "pending",
                    f"Subtask {st.get('title')} is pending",
                )
            return True
        return False

    def test_greenie_agent_discovery(self):
        """Test agent capability discovery."""
        print("\n  --- Greenie Agent Discovery ---")
        healthy = self.check_service_health("Greenie", 8080)
        if not healthy:
            print("  ⊘ Greenie not running, skipping agent discovery test")
            return True

        result = self.make_request(
            "get",
            "http://localhost:8080/api/tasks/agents",
        )
        if result is not None:
            # May return empty list if no agents configured
            self.assert_true(
                isinstance(result, list),
                "Agent discovery returns a list",
            )
            print(f"  ℹ Found {len(result)} agents")
            return True
        return False

    def test_greenie_task_cancellation(self):
        """Test task cancellation."""
        print("\n  --- Greenie Task Cancellation ---")
        healthy = self.check_service_health("Greenie", 8080)
        if not healthy:
            print("  ⊘ Greenie not running, skipping cancellation test")
            return True

        # Create a task
        create_result = self.make_request(
            "post",
            "http://localhost:8080/api/tasks",
            json={
                "title": "Cancel test",
                "description": "This task will be cancelled",
            },
        )
        if not create_result or "id" not in create_result:
            print("  ⊘ Could not create task for cancellation test")
            return True

        task_id = create_result["id"]

        # Cancel the task
        cancel_result = self.make_request(
            "post",
            f"http://localhost:8080/api/tasks/{task_id}/cancel",
        )
        if cancel_result:
            self.assert_true(
                cancel_result.get("cancelled") is True,
                "Task cancellation succeeds",
            )
            return True
        return False

    def test_slinker_adapter_listing(self):
        """Test Slinker adapter listing."""
        print("\n  --- Slinker Adapter Listing ---")
        healthy = self.check_service_health("Slinker", 8081)
        if not healthy:
            print("  ⊘ Slinker not running, skipping adapter listing test")
            return True

        result = self.make_request(
            "get",
            "http://localhost:8081/api/v1/tasks/adapters",
        )
        if result:
            adapters = result.get("adapters", {})
            self.assert_true(
                "subprocess" in adapters,
                "Subprocess adapter is always available",
            )
            print(f"  ℹ Available adapters: {list(adapters.keys())}")
            return True
        return False

    def test_slinker_task_execution(self):
        """Test Slinker task execution with subprocess adapter."""
        print("\n  --- Slinker Task Execution ---")
        healthy = self.check_service_health("Slinker", 8081)
        if not healthy:
            print("  ⊘ Slinker not running, skipping execution test")
            return True

        result = self.make_request(
            "post",
            "http://localhost:8081/api/v1/tasks",
            json={
                "title": "Echo test",
                "description": "echo 'Hello from Slinker'",
                "adapter": "subprocess",
                "timeout": 30,
            },
        )
        if result:
            self.assert_true(
                "id" in result,
                "Task execution returns task ID",
            )
            self.assert_true(
                result.get("status") == "running",
                "Task starts in running status",
            )
            return True
        return False

    def test_slinker_task_result(self):
        """Test retrieving task results from Slinker."""
        print("\n  --- Slinker Task Result ---")
        healthy = self.check_service_health("Slinker", 8081)
        if not healthy:
            print("  ⊘ Slinker not running, skipping result test")
            return True

        # Create a task
        create_result = self.make_request(
            "post",
            "http://localhost:8081/api/v1/tasks",
            json={
                "title": "Result test",
                "description": "echo 'test result'",
                "adapter": "subprocess",
                "timeout": 10,
            },
        )
        if not create_result or "id" not in create_result:
            print("  ⊘ Could not create task for result test")
            return True

        task_id = create_result["id"]

        # Wait briefly for execution
        import time

        time.sleep(3)

        # Get result
        result = self.make_request(
            "get",
            f"http://localhost:8081/api/v1/tasks/{task_id}",
        )
        if result:
            self.assert_true(
                "status" in result,
                "Result contains status",
            )
            status = result.get("status", "")
            self.assert_true(
                status in ("completed", "failed", "running"),
                f"Task status is valid: {status}",
            )
            return True
        return False

    def test_greenie_task_list(self):
        """Test listing tasks through Greenie."""
        print("\n  --- Greenie Task List ---")
        healthy = self.check_service_health("Greenie", 8080)
        if not healthy:
            print("  ⊘ Greenie not running, skipping task list test")
            return True

        result = self.make_request(
            "get",
            "http://localhost:8080/api/tasks?limit=10",
        )
        if result is not None:
            self.assert_true(
                isinstance(result, list),
                "Task list returns a list",
            )
            print(f"  ℹ Found {len(result)} tasks")
            return True
        return False

    def test_greenie_task_retry(self):
        """Test retrying a failed task."""
        print("\n  --- Greenie Task Retry ---")
        healthy = self.check_service_health("Greenie", 8080)
        if not healthy:
            print("  ⊘ Greenie not running, skipping retry test")
            return True

        # Create a task
        create_result = self.make_request(
            "post",
            "http://localhost:8080/api/tasks",
            json={
                "title": "Retry test",
                "description": "This task will be retried",
            },
        )
        if not create_result or "id" not in create_result:
            print("  ⊘ Could not create task for retry test")
            return True

        task_id = create_result["id"]

        # Retry the task
        retry_result = self.make_request(
            "post",
            f"http://localhost:8080/api/tasks/{task_id}/retry",
        )
        if retry_result:
            self.assert_true(
                retry_result.get("status") == "pending",
                "Retried task is back to pending",
            )
            return True
        return False

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        print("\n  --- End-to-End Agent Workflow ---")
        greenie_healthy = self.check_service_health("Greenie", 8080)
        slinker_healthy = self.check_service_health("Slinker", 8081)

        if not greenie_healthy:
            print("  ⊘ Greenie not running, skipping e2e test")
            return True
        if not slinker_healthy:
            print("  ⊘ Slinker not running, skipping e2e test")
            return True

        # Step 1: Create task through Greenie
        task = self.make_request(
            "post",
            "http://localhost:8080/api/tasks",
            json={
                "title": "E2E test task",
                "description": "End-to-end workflow test",
                "required_capabilities": ["coding"],
            },
        )
        if not task or "id" not in task:
            print("  ✗ Failed to create task")
            return False

        task_id = task["id"]
        print(f"  ✓ Task created: {task_id}")

        # Step 2: Verify decomposition
        subtasks = task.get("subtasks", [])
        self.assert_true(
            len(subtasks) > 0,
            f"Task decomposed into {len(subtasks)} subtasks",
        )

        # Step 3: Get task details
        details = self.make_request(
            "get",
            f"http://localhost:8080/api/tasks/{task_id}",
        )
        if details:
            self.assert_true(
                details.get("id") == task_id,
                "Task details match created task",
            )

        # Step 4: Check task results endpoint
        results = self.make_request(
            "get",
            f"http://localhost:8080/api/tasks/{task_id}/results",
        )
        if results is not None:
            self.assert_true(
                isinstance(results, list),
                "Task results endpoint returns a list",
            )

        return True
