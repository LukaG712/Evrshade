#!/bin/bash
# Evershade — Lint and format check
# Runs ruff on all Python code

set -e

echo "Running linters..."

# Install ruff if not present
pip install ruff --quiet 2>/dev/null || true

# Check Python files
echo "Python linting..."
ruff check . --exclude .junie --exclude node_modules --output-format github || {
    echo "Linting failed!"
    exit 1
}

echo "Python formatting..."
ruff format . --exclude .junie --exclude node_modules --check --diff || {
    echo "Formatting check failed!"
    exit 1
}

echo "All checks passed!"
