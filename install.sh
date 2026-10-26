#!/bin/bash
# Evershade — Installation script
# Sets up all services using Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
ENV_FILE="$SCRIPT_DIR/.env"

echo "╔════════════════════════════════════════════════════════╗"
echo "║          Evershade Platform Installation               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check docker-compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available."
    exit 1
fi

# Check compose file
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ docker-compose.yml not found at $COMPOSE_FILE"
    exit 1
fi

# Setup .env
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        echo "📋 Creating .env from .env.example..."
        cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
        echo "   ⚠️  Please edit $ENV_FILE and configure your settings."
    else
        echo "⚠️  No .env.example found. Creating empty .env..."
        touch "$ENV_FILE"
    fi
fi

# Profile selection
PROFILE="${1:-full}"
echo ""
echo "📦 Installing with profile: $PROFILE"
echo ""

# Pull images
echo "🔄 Pulling Docker images..."
docker compose -f "$COMPOSE_FILE" pull --profile "$PROFILE"

echo ""
echo "✅ Images pulled successfully!"
echo ""
echo "Next steps:"
echo "  1. Configure .env file: $ENV_FILE"
echo "  2. Start services: ./start.sh $PROFILE"
echo ""
echo "Or use the CLI:"
echo "  evershade install --profile $PROFILE"
echo "  evershade start --profile $PROFILE"
