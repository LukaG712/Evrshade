#!/bin/bash
# Evershade — Start all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

PROFILE="${1:-full}"

echo "🚀 Starting Evershade (profile: $PROFILE)..."
echo ""

docker compose -f "$COMPOSE_FILE" up -d --profile "$PROFILE"

echo ""
echo "✅ Services started!"
echo ""
echo "Access the dashboard at: http://localhost:5173"
echo "Grafana: http://localhost:3000"
echo "Prometheus: http://localhost:9090"
echo ""
echo "Use 'evershade status' to check service health."
