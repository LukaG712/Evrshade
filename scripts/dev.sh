#!/bin/bash
# Evershade — Development helper script
# Starts all services in development mode with hot reload

set -e

echo "Starting Evershade in development mode..."

# Set development environment
export EVERSHADE_ENVIRONMENT=dev
export EVERSHADE_LOG_LEVEL=DEBUG

# Start Docker Compose with dev profile
docker compose --profile dev --profile monitoring up -d

echo ""
echo "Services starting..."
echo "Wait for services to be healthy..."
sleep 5

# Check health
echo ""
echo "Health status:"
for port in 8080 8000 3000 8085 8086 8087 8088 8089; do
    service=$(curl -s http://localhost:$port/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('service', 'unknown'))" 2>/dev/null || echo "port:$port")
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null || echo "000")
    printf "  %-15s port %-5s status %s\n" "$service" "$port" "$status"
done

echo ""
echo "Dashboard: http://localhost:5173"
echo "Grafana:   http://localhost:3001"
echo "Prometheus: http://localhost:9090"
echo ""
echo "Press Ctrl+C to stop"
trap "docker compose down; exit" INT TERM
wait
