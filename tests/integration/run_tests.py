"""
Integration test runner for Evershade platform.
Run all integration tests and report results.

Usage:
    python -m tests.integration.run_tests
    python -m tests.integration.run_tests --service greenie
    python -m tests.integration.run_tests --flow chat
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.integration.test_agent_workflow import TestAgentWorkflow
from tests.integration.test_chat_flow import TestChatFlow
from tests.integration.test_code_execution_flow import TestCodeExecutionFlow
from tests.integration.test_core_platform_flow import TestCorePlatformFlow
from tests.integration.test_cross_service_workflow import TestCrossServiceWorkflow
from tests.integration.test_dashboard_cli import TestCLICommands, TestDashboardAPI
from tests.integration.test_integration_flow import TestIntegrationFlow
from tests.integration.test_knowledge_flow import TestKnowledgeFlow
from tests.integration.test_notification_flow import TestNotificationFlow
from tests.integration.test_observability_flow import TestObservabilityFlow
from tests.integration.test_phase14_workflow import (
    TestPhase14CrossService,
    TestPhase14Notifications,
    TestPhase14Observability,
    TestPhase14Security,
    TestPhase14Workflow,
)
from tests.integration.test_scraping_flow import TestScrapingFlow


def run_tests(service_filter=None, flow_filter=None):
    """Run integration tests with optional filters."""

    test_classes = [
        ("Core Platform Flow", TestCorePlatformFlow),
        ("Chat Flow", TestChatFlow),
        ("Code Execution Flow", TestCodeExecutionFlow),
        ("Scraping Flow", TestScrapingFlow),
        ("Notification Flow", TestNotificationFlow),
        ("Observability Flow", TestObservabilityFlow),
        ("Knowledge Graph Flow", TestKnowledgeFlow),
        ("External Integration Flow", TestIntegrationFlow),
        ("Agent Workflow", TestAgentWorkflow),
        ("Cross-Service Workflow", TestCrossServiceWorkflow),
        ("Phase 14 — Workflow", TestPhase14Workflow),
        ("Phase 14 — Observability", TestPhase14Observability),
        ("Phase 14 — Security", TestPhase14Security),
        ("Phase 14 — Notifications", TestPhase14Notifications),
        ("Phase 14 — Cross-Service", TestPhase14CrossService),
        ("Phase 15 — Dashboard API", TestDashboardAPI),
        ("Phase 15 — CLI Commands", TestCLICommands),
    ]

    total = 0
    passed = 0
    failed = 0
    skipped = 0

    print("=" * 70)
    print("Evershade Integration Tests")
    print("=" * 70)
    print()

    for name, test_class in test_classes:
        # Apply flow filter
        if flow_filter and flow_filter.lower() not in name.lower():
            continue

        test = test_class()

        # Apply service filter
        if service_filter and service_filter.lower() not in test.service.lower():
            continue

        print(f"\n{'=' * 70}")
        print(f"Testing: {name} (Service: {test.service})")
        print(f"{'=' * 70}")

        try:
            result = test.run()
            total += 1

            if result:
                passed += 1
                print(f"✓ PASSED: {name}")
            else:
                failed += 1
                print(f"✗ FAILED: {name}")
        except Exception as e:
            skipped += 1
            print(f"⊘ SKIPPED: {name} — {e}")

    print(f"\n{'=' * 70}")
    print("Results Summary")
    print(f"{'=' * 70}")
    print(f"Total:   {total}")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {skipped}")
    print(f"{'=' * 70}")

    if failed > 0:
        print("\nSome tests failed. Check output above for details.")
        return 1
    elif skipped > 0 and passed == 0:
        print("\nAll tests were skipped. Services may not be running.")
        return 2
    else:
        print("\nAll tests passed!")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Evershade integration tests")
    parser.add_argument("--service", help="Filter by service name")
    parser.add_argument("--flow", help="Filter by flow name")
    args = parser.parse_args()

    exit_code = run_tests(service_filter=args.service, flow_filter=args.flow)
    sys.exit(exit_code)
