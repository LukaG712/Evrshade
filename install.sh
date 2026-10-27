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

# ─── Service Definitions ────────────────────────────────────────────
REQUIRED_SERVICES=("Greenie" "Slinker" "Trapper" "Gobber")
OPTIONAL_SERVICES=(
    "Sneaker|Observability & alerting"
    "Hider|Encrypted secrets management"
    "Poltergeist|Notifications (Slack, Discord, Email, Telegram)"
    "Shrewd|LLM providers (OpenAI, Anthropic, Google, Ollama)"
    "Slammer|Web dashboard"
)

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

# ─── Interactive Service Selection ──────────────────────────────────
echo ""
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Select Services to Install                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "  ${YELLOW}Required services (always included):${NC}"
echo "    [x] Greenie    — Central API backend"
echo "    [x] Slinker    — Code execution"
echo "    [x] Trapper    — Web scraping"
echo "    [x] Gobber     — Storage & search"
echo ""
echo -e "  ${YELLOW}Optional services (press number to toggle):${NC}"
idx=1
for svc in "${OPTIONAL_SERVICES[@]}"; do
    name="${svc%%|*}"
    desc="${svc##*|}"
    echo "    [$idx] $name — $desc"
    ((idx++))
done
echo ""
echo -e "  ${BLUE}Enter numbers to toggle, or press Enter to continue:${NC}"

# Start with required services selected
selected=("${REQUIRED_SERVICES[@]}")

while true; do
    read -rp "  > " CHOICE
    if [[ -z "$CHOICE" ]]; then
        break
    fi
    if [[ "$CHOICE" =~ ^[0-9]+$ ]] && [[ "$CHOICE" -ge 1 ]] && [[ "$CHOICE" -le ${#OPTIONAL_SERVICES[@]} ]]; then
        svc_name="${OPTIONAL_SERVICES[$((CHOICE-1))]%%|*}"
        found=false
        for s in "${selected[@]}"; do
            if [[ "$s" == "$svc_name" ]]; then
                found=true
                break
            fi
        done
        if $found; then
            new_selected=()
            for s in "${selected[@]}"; do
                if [[ "$s" != "$svc_name" ]]; then
                    new_selected+=("$s")
                fi
            done
            selected=("${new_selected[@]}")
            echo -e "  ${RED}[XX] Removed $svc_name${NC}"
        else
            selected+=("$svc_name")
            echo -e "  ${GREEN}[OK] Added $svc_name${NC}"
        fi
    else
        echo -e "  ${RED}[XX] Invalid choice. Enter 1-${#OPTIONAL_SERVICES[@]}, or press Enter.${NC}"
    fi
done

# Derive profile from selected services
has_slammer=false
has_supporting=false
for s in "${selected[@]}"; do
    if [[ "$s" == "Slammer" ]]; then
        has_slammer=true
    fi
    if [[ "$s" == "Sneaker" || "$s" == "Hider" || "$s" == "Poltergeist" || "$s" == "Shrewd" ]]; then
        has_supporting=true
    fi
done

if $has_slammer; then
    PROFILE="full"
elif $has_supporting; then
    PROFILE="standard"
else
    PROFILE="minimal"
fi

echo ""
success "Selected services: ${selected[*]}"
success "Installation profile: $PROFILE"

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
