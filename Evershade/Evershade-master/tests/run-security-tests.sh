#!/usr/bin/env bash
# Evershade Security Test Runner
#
# Runs all security tests for the infrastructure fixes.
# Usage:
#   ./tests/run-security-tests.sh          # Run all tests
#   ./tests/run-security-tests.sh verbose  # Run with verbose output
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================"
echo "  Evershade Security Tests"
echo "============================================"
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "Installing pytest..."
    pip install --quiet pytest pyyaml
fi

# Run tests
TEST_ARGS=""
if [ "${1:-}" = "verbose" ]; then
    TEST_ARGS="-v --tb=long"
fi

echo "Running security tests..."
echo ""

pytest tests/test_install_gui_security.py \
       tests/test_install_gui_win_security.py \
       tests/test_docker_compose_security.py \
       tests/test_caddyfile_security.py \
       tests/test_env_example_security.py \
       $TEST_ARGS

EXIT_CODE=$?

echo ""
echo "============================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "  ✓ All security tests passed"
else
    echo "  ✗ Some security tests failed"
fi
echo "============================================"

exit $EXIT_CODE
