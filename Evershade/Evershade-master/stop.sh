#!/bin/bash
# Unified Workflow — Stop Script (Linux/macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PROFILE="full"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./stop.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profile NAME   Compose profile: minimal, standard, full (default: full)"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Stopping all services (profile: $PROFILE)..."

docker compose --profile "$PROFILE" down

echo "Services stopped."
echo ""
echo "To remove volumes and data: docker compose --profile $PROFILE down -v"
echo "To start again: ./start.sh --profile $PROFILE"
