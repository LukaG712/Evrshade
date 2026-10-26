#!/bin/bash
# Evershade — Stop all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

PROFILE="${1:-full}"
VOLUMES=false

if [[ "$2" == "--volumes" ]] || [[ "$2" == "-v" ]]; then
    VOLUMES=true
fi

echo "🛑 Stopping Evershade (profile: $PROFILE)..."
echo ""

ARGS=("down" "--profile" "$PROFILE")
if [ "$VOLUMES" = true ]; then
    ARGS+=("--volumes")
fi

docker compose -f "$COMPOSE_FILE" "${ARGS[@]}"

echo ""
echo "✅ Services stopped."
