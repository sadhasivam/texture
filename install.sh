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
echo -e "${YELLOW}[1/7] Updating system packages...${NC}"
sudo apt-get update

# Install Node.js (required for pnpm)
echo ""
echo -e "${YELLOW}[2/7] Installing Node.js...${NC}"
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
echo -e "${YELLOW}[3/7] Installing pnpm...${NC}"
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
echo -e "${YELLOW}[4/7] Checking Python installation...${NC}"
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
echo -e "${YELLOW}[5/7] Installing uv...${NC}"
if command_exists uv; then
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}✓ uv already installed: $UV_VERSION${NC}"
else
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}✓ uv installed: $(uv --version)${NC}"
fi

# Install Caddy
echo ""
echo -e "${YELLOW}[6/7] Installing Caddy...${NC}"
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
echo -e "${YELLOW}[7/7] Setting up project dependencies...${NC}"

# Setup Python backend (Weaver)
echo ""
echo "Setting up Weaver backend..."
cd Weaver
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
echo "Installing Node.js dependencies..."
# Add pnpm to PATH if not already there
export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$PATH"
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
echo "  - Node.js: $(node --version)"
echo "  - pnpm: $(pnpm --version)"
echo "  - Python: $(python3 --version)"
echo "  - uv: $(uv --version)"
echo "  - Caddy: $(caddy version | head -n1)"
echo ""
echo "Next steps:"
echo "  1. Development mode:  make start"
echo "  2. Production mode:   make prod"
echo "  3. Stop servers:      make stop (dev) or make prod-stop (prod)"
echo ""
echo "Production URL: http://localhost:8080"
echo ""
echo -e "${YELLOW}Note: You may need to reload your shell or run:${NC}"
echo "  source ~/.bashrc    # or ~/.zshrc"
echo ""
