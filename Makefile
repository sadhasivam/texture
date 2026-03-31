.PHONY: help install dev-loom dev-weaver build start stop status clean proto-generate proto-lint proto-format proto-breaking

export PATH := $(HOME)/.local/bin:$(HOME)/.cargo/bin:$(PATH)

ROOT := $(CURDIR)

help: ## Show this help message
	@echo 'Texture - ML Learning Studio'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies for backend services
	@echo "Installing Loom (Go backend) dependencies..."
	@cd Loom && go mod download && go mod tidy
	@echo "Installing Weaver (Python gRPC) dependencies..."
	@cd Weaver && uv sync
	@echo "✓ Backend dependencies installed"

dev-loom: ## Run Loom Go backend in dev mode
	@cd Loom && go run cmd/loom/*.go serve

dev-weaver: ## Run Weaver Python gRPC server in dev mode
	@cd Weaver && .venv/bin/python grpc_main.py

build: ## Build Loom Go backend binary
	@echo "Building Loom backend..."
	@cd Loom && go build -o bin/loom cmd/loom/*.go
	@echo "✓ Backend built to Loom/bin/loom"

start: build ## Start all production services in background
	@echo "Starting Weaver gRPC server..."
	@cd Weaver && nohup .venv/bin/python grpc_main.py > /tmp/weaver_grpc.log 2>&1 &
	@sleep 2
	@echo "Starting Loom API server..."
	@cd Loom && nohup ./bin/loom serve > /tmp/loom.log 2>&1 &
	@sleep 2
	@echo "Starting Caddy reverse proxy..."
	@caddy start --config "$(ROOT)/Caddyfile" --adapter caddyfile || true
	@echo "✓ All services started"
	@echo ""
	@echo "Services:"
	@echo "  Weaver gRPC: localhost:50051"
	@echo "  Loom API:    localhost:8080"
	@echo "  Caddy:       http://localhost"
	@echo ""
	@echo "Logs:"
	@echo "  Weaver: /tmp/weaver_grpc.log"
	@echo "  Loom:   /tmp/loom.log"

stop: ## Stop all production services
	@echo "Stopping Loom API server..."
	@pkill -f "./bin/loom serve" || true
	@echo "Stopping Weaver gRPC server..."
	@pkill -f "grpc_main.py" || true
	@echo "Stopping Caddy..."
	@caddy stop || true
	@pkill -f "caddy" || true
	@echo "✓ All services stopped"

status: ## Show status of backend services
	@echo "Texture Status"
	@echo "=============="
	@echo ""
	@echo "Loom (Go Backend - port 8080):"
	@pgrep -af "loom serve" || echo "  not running"
	@echo ""
	@echo "Weaver (gRPC - port 50051):"
	@pgrep -af "grpc_main.py" || echo "  not running"
	@echo ""
	@echo "Caddy (Reverse Proxy):"
	@pgrep -af "caddy" || echo "  not running"
	@echo ""
	@echo "Note: Use scripts/dev for full development workflow (includes Kolam frontend)"

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf Loom/bin
	@echo "✓ Cleaned"

proto-generate: ## Generate protobuf code for Go and Python
	@echo "Generating protobuf code..."
	@cd proto && $(MAKE) generate

proto-lint: ## Lint protobuf files
	@echo "Linting protobuf files..."
	@cd proto && $(MAKE) lint

proto-format: ## Format protobuf files
	@echo "Formatting protobuf files..."
	@cd proto && $(MAKE) format

proto-breaking: ## Check for breaking changes in protobuf
	@echo "Checking for breaking changes..."
	@cd proto && $(MAKE) breaking
