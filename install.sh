#!/bin/bash
# Evershade — Interactive Installation Script (Linux/macOS)
# Sets up all services using Docker Compose with interactive configuration.
# Safe to re-run.

set -e

# ─── Colors ─────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Helpers ────────────────────────────────────────────────────────
info()    { echo -e "${BLUE}[INFO]${NC}    $*"; }
success() { echo -e "${GREEN}[OK]${NC}      $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}    $*"; }
error()   { echo -e "${RED}[ERROR]${NC}   $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
ENV_FILE="$SCRIPT_DIR/.env"

# ─── Banner ─────────────────────────────────────────────────────────
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║       Evershade — Installation Wizard                        ║"
echo "║                                                              ║"
echo "║  Self-hosted AI agent platform (Docker-based microservices)  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# ─── Prerequisite Checks ────────────────────────────────────────────

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed."
    echo ""
    echo "  Install Docker:"
    echo "    Ubuntu:  curl -fsSL https://get.docker.com | sh"
    echo "    macOS:   brew install --cask docker"
    echo "    Or visit: https://docs.docker.com/get-docker/"
    echo ""
    exit 1
fi
success "Docker is available ($(docker --version 2>/dev/null || echo 'installed'))"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    error "Docker Compose is not available."
    echo ""
    echo "  Install Docker Compose Plugin:"
    echo "    Ubuntu:  sudo apt install docker-compose-plugin"
    echo "    Or visit: https://docs.docker.com/compose/install/"
    echo ""
    exit 1
fi
success "Docker Compose is available"

# Check Docker is running
if ! docker info &>/dev/null 2>&1; then
    error "Docker daemon is not running."
    echo ""
    echo "  Start Docker:"
    echo "    Ubuntu:  sudo systemctl start docker"
    echo "    macOS:   Open Docker Desktop application"
    echo ""
    exit 1
fi
success "Docker daemon is running"

# Check compose file
if [ ! -f "$COMPOSE_FILE" ]; then
    error "docker-compose.yml not found at $COMPOSE_FILE"
    exit 1
fi
success "docker-compose.yml found"

# ─── Interactive Profile Selection ──────────────────────────────────
echo ""
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Installation Profile Selection                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "  [1] Minimal  — Core services only (Greenie, Slinker, Trapper, Gobber)"
echo "  [2] Standard — All services except dashboard (default)"
echo "  [3] Full     — Everything including Slammer dashboard and Speedy CLI"
echo ""
read -rp "  Select profile (1-3) [2]: " PROFILE_CHOICE
PROFILE_CHOICE="${PROFILE_CHOICE:-2}"
case "$PROFILE_CHOICE" in
    1) PROFILE="minimal" ;;
    2) PROFILE="standard" ;;
    3) PROFILE="full" ;;
    *) warn "Invalid choice, using default: standard"; PROFILE="standard" ;;
esac
echo ""
success "Selected profile: $PROFILE"

# ─── .env Configuration ─────────────────────────────────────────────
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Environment Configuration${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        info "Creating .env from .env.example..."
        cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"

        # Auto-generate secure API keys
        info "Generating secure API keys..."

        generate_key() {
            if command -v openssl &>/dev/null; then
                openssl rand -hex 32
            elif [ -f /dev/urandom ]; then
                head -c 64 /dev/urandom | od -An -tx1 | tr -d ' \n' | head -c 64
            else
                echo "CHANGE_ME_$(date +%s)_$(shuf -i 100000-999999 -n 1 2>/dev/null || echo $$)"
            fi
        }

        # Replace default keys with generated ones
        sed -i "s/^EVERSHADE_GREENIE_API_KEY=.*/EVERSHADE_GREENIE_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_SLINKER_API_KEY=.*/EVERSHADE_SLINKER_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_TRAPPER_API_KEY=.*/EVERSHADE_TRAPPER_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_GOBBER_API_KEY=.*/EVERSHADE_GOBBER_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_SNEAKER_API_KEY=.*/EVERSHADE_SNEAKER_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_HIDER_API_KEY=.*/EVERSHADE_HIDER_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_POLTERGEIST_API_KEY=.*/EVERSHADE_POLTERGEIST_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_SHREWD_API_KEY=.*/EVERSHADE_SHREWD_API_KEY=$(generate_key)/" "$ENV_FILE"
        sed -i "s/^EVERSHADE_ENCRYPTION_KEY=.*/EVERSHADE_ENCRYPTION_KEY=$(generate_key)/" "$ENV_FILE"

        success ".env created with auto-generated secure keys"
    else
        warn "No .env.example found. Creating empty .env..."
        touch "$ENV_FILE"
        warn "Please manually configure $ENV_FILE before starting services."
    fi
else
    info ".env already exists at $ENV_FILE"
    read -rp "  Regenerate .env with new secure keys? (y/N): " REGEN_ANS
    if [[ "$REGEN_ANS" =~ ^[Yy] ]]; then
        read -rp "  This will overwrite your current .env. Are you sure? (y/N): " CONFIRM
        if [[ "$CONFIRM" =~ ^[Yy] ]]; then
            info "Regenerating .env..."
            if [ -f "$SCRIPT_DIR/.env.example" ]; then
                cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"

                generate_key() {
                    openssl rand -hex 32
                }

                sed -i "s/^EVERSHADE_GREENIE_API_KEY=.*/EVERSHADE_GREENIE_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_SLINKER_API_KEY=.*/EVERSHADE_SLINKER_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_TRAPPER_API_KEY=.*/EVERSHADE_TRAPPER_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_GOBBER_API_KEY=.*/EVERSHADE_GOBBER_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_SNEAKER_API_KEY=.*/EVERSHADE_SNEAKER_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_HIDER_API_KEY=.*/EVERSHADE_HIDER_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_POLTERGEIST_API_KEY=.*/EVERSHADE_POLTERGEIST_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_SHREWD_API_KEY=.*/EVERSHADE_SHREWD_API_KEY=$(generate_key)/" "$ENV_FILE"
                sed -i "s/^EVERSHADE_ENCRYPTION_KEY=.*/EVERSHADE_ENCRYPTION_KEY=$(generate_key)/" "$ENV_FILE"

                success ".env regenerated with new keys"
            fi
        else
            info "Keeping existing .env"
        fi
    fi
fi

# ─── LLM API Keys Prompt ────────────────────────────────────────────
echo ""
info "For LLM providers, you'll need to add your API keys to $ENV_FILE:"
echo "  EVERSHADE_OPENAI_API_KEY    — OpenAI (GPT-4, GPT-3.5)"
echo "  EVERSHADE_ANTHROPIC_API_KEY — Anthropic (Claude)"
echo "  EVERSHADE_GOOGLE_API_KEY    — Google (Gemini)"
echo ""
info "You can edit these later: nano $ENV_FILE"

# ─── Pull Docker Images ─────────────────────────────────────────────
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Pulling Docker Images${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
info "Pulling images for profile: $PROFILE"
docker compose -f "$COMPOSE_FILE" pull --profile "$PROFILE"

# ─── Summary ────────────────────────────────────────────────────────
echo ""
success "╔══════════════════════════════════════════════════════════════╗"
success "║  Evershade installation complete!                           ║"
success "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Installation summary:"
echo "  Directory:  $SCRIPT_DIR"
echo "  Profile:    $PROFILE"
echo "  Config:     $ENV_FILE"
echo ""
echo "Quick commands:"
echo "  cd $SCRIPT_DIR"
echo "  ./start.sh --profile $PROFILE   # Start services"
echo "  ./stop.sh                      # Stop services"
echo ""
echo "API endpoint:  http://localhost:8080"
echo ""
success "Welcome to Evershade! 🏚️"
