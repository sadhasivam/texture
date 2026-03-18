#!/bin/bash
set -e

# Texture Installation Script for Digital Ocean/Ubuntu/Debian
# Installs Caddy, pnpm, uv, and sets up the application

echo "======================================"
echo "Texture Installation Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Ubuntu/Debian
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    echo "Detected OS: $OS"
else
    echo -e "${RED}Cannot detect OS. This script is for Ubuntu/Debian systems.${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update system packages
echo ""
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
sudo apt-get update

# Install build essentials (includes make)
echo ""
echo -e "${YELLOW}[2/8] Installing build essentials...${NC}"
if command_exists make; then
    MAKE_VERSION=$(make --version | head -n1)
    echo -e "${GREEN}✓ make already installed: $MAKE_VERSION${NC}"
else
    echo "Installing make and build tools..."
    sudo apt-get install -y build-essential
    echo -e "${GREEN}✓ make installed: $(make --version | head -n1)${NC}"
fi

# Install Node.js (required for pnpm)
echo ""
echo -e "${YELLOW}[3/8] Installing Node.js...${NC}"
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js already installed: $NODE_VERSION${NC}"
else
    echo "Installing Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo -e "${GREEN}✓ Node.js installed: $(node --version)${NC}"
fi

# Install pnpm
echo ""
echo -e "${YELLOW}[4/8] Installing pnpm...${NC}"
if command_exists pnpm; then
    PNPM_VERSION=$(pnpm --version)
    echo -e "${GREEN}✓ pnpm already installed: $PNPM_VERSION${NC}"
else
    echo "Installing pnpm..."
    curl -fsSL https://get.pnpm.io/install.sh | sh -
    # Add pnpm to PATH for current session
    export PNPM_HOME="$HOME/.local/share/pnpm"
    export PATH="$PNPM_HOME:$PATH"
    echo -e "${GREEN}✓ pnpm installed: $(pnpm --version)${NC}"
fi

# Install Python 3 (required for uv)
echo ""
echo -e "${YELLOW}[5/8] Checking Python installation...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python already installed: $PYTHON_VERSION${NC}"
else
    echo "Installing Python 3..."
    sudo apt-get install -y python3 python3-pip python3-venv
    echo -e "${GREEN}✓ Python installed: $(python3 --version)${NC}"
fi

# Install uv (Python package manager)
echo ""
echo -e "${YELLOW}[6/8] Installing uv...${NC}"
if command_exists uv; then
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}✓ uv already installed: $UV_VERSION${NC}"
else
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for current session
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    # Also try common installation locations
    if [ -f "$HOME/.cargo/bin/uv" ]; then
        UV_BIN="$HOME/.cargo/bin/uv"
    elif [ -f "$HOME/.local/bin/uv" ]; then
        UV_BIN="$HOME/.local/bin/uv"
    else
        # Source the environment to get uv
        [ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
    fi
    echo -e "${GREEN}✓ uv installed: $(uv --version 2>/dev/null || echo 'installed')${NC}"
fi

# Install Caddy
echo ""
echo -e "${YELLOW}[7/8] Installing Caddy...${NC}"
if command_exists caddy; then
    CADDY_VERSION=$(caddy version)
    echo -e "${GREEN}✓ Caddy already installed: $CADDY_VERSION${NC}"
else
    echo "Installing Caddy..."
    sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
    sudo apt update
    sudo apt install -y caddy
    echo -e "${GREEN}✓ Caddy installed: $(caddy version)${NC}"
fi

# Setup project dependencies
echo ""
echo -e "${YELLOW}[8/8] Setting up project dependencies...${NC}"

# Setup Python backend (Weaver)
echo ""
echo "Setting up Weaver backend..."
cd Weaver

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    uv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

echo "Installing Python dependencies..."
uv sync
echo -e "${GREEN}✓ Python dependencies installed${NC}"
cd ..

# Setup Node.js frontend (Kolam)
echo ""
echo "Setting up Kolam frontend..."
cd Kolam

# Ensure pnpm is in PATH
export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$PATH"
# Source pnpm environment if it exists
[ -s "$PNPM_HOME/pnpm.sh" ] && . "$PNPM_HOME/pnpm.sh"

echo "Installing Node.js dependencies..."
pnpm install
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
cd ..

# Create storage directory for uploads
echo ""
echo "Creating storage directories..."
mkdir -p Weaver/app/storage/uploads
echo -e "${GREEN}✓ Storage directories created${NC}"

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "======================================"
echo ""
echo "Installed versions:"
echo "  - make: $(make --version | head -n1)"
echo "  - Node.js: $(node --version)"
echo "  - pnpm: $(pnpm --version)"
echo "  - Python: $(python3 --version)"
echo "  - uv: $(uv --version)"
echo "  - Caddy: $(caddy version | head -n1)"
echo ""
echo "Next steps:"
echo "  1. Production mode:   make prod       (runs in background)"
echo "  2. Stop servers:      make prod-stop"
echo "  3. Check logs:        tail -f weaver.log caddy.log"
echo ""
echo "Access at: http://YOUR_SERVER_IP:8080"
echo ""
echo "Note: 'make prod' runs all servers in background as daemons."
echo ""
echo -e "${YELLOW}IMPORTANT: Reload your shell to use the newly installed tools:${NC}"
echo "  source ~/.bashrc    # for bash"
echo "  source ~/.zshrc     # for zsh"
echo ""
echo "Or close and reopen your terminal."
echo ""
