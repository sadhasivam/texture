.PHONY: start stop prod prod-stop build status

# Export PATH to include pnpm and uv
export PNPM_HOME := $(HOME)/.local/share/pnpm
export PATH := $(PNPM_HOME):$(HOME)/.local/bin:$(HOME)/.cargo/bin:$(PATH)

# Development mode (separate frontend dev server)
start:
	@echo "Starting Weaver backend..."
	@cd Weaver && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../weaver.log 2>&1 & echo $$! > ../weaver.pid
	@echo "Weaver backend started (PID: $$(cat weaver.pid))"
	@echo "Starting Kolam frontend..."
	@cd Kolam && pnpm dev > ../kolam.log 2>&1 & echo $$! > ../kolam.pid
	@echo "Kolam frontend started (PID: $$(cat kolam.pid))"
	@echo "✓ Both servers started"
	@echo "  Weaver: http://localhost:8000"
	@echo "  Kolam: http://localhost:3000"
	@echo "  Logs: weaver.log, kolam.log"

stop:
	@echo "Stopping all development servers..."
	@echo ""
	@echo "Killing backend processes..."
	@pkill -9 -f "uvicorn" 2>/dev/null && echo "  ✓ uvicorn killed" || echo "  - No uvicorn processes"
	@pkill -9 -f "python.*app.main" 2>/dev/null || true
	@pkill -9 -f "uv run" 2>/dev/null || true
	@echo ""
	@echo "Killing frontend processes..."
	@pkill -9 -f "rsbuild" 2>/dev/null && echo "  ✓ rsbuild killed" || echo "  - No rsbuild processes"
	@pkill -9 -f "pnpm" 2>/dev/null && echo "  ✓ pnpm killed" || echo "  - No pnpm processes"
	@pkill -9 -f "node.*rsbuild" 2>/dev/null || true
	@echo ""
	@echo "Cleaning up PID files..."
	@rm -f weaver.pid kolam.pid
	@sleep 2
	@echo ""
	@echo "Final verification..."
	@ps aux | grep -E "(uvicorn|rsbuild|pnpm)" | grep -v grep || echo "  ✓ All processes stopped"
	@echo ""
	@echo "✓ Cleanup complete"

# Production mode (Caddy serves built frontend + proxies to backend)
build:
	@echo "Building Kolam frontend..."
	@cd Kolam && pnpm build
	@echo "✓ Frontend built to Kolam/dist"

prod: build
	@echo "Updating Caddyfile with absolute path..."
	@sed -i 's|root \* .*/Kolam/dist|root * $(PWD)/Kolam/dist|g' Caddyfile || sed -i.bak 's|root \* .*/Kolam/dist|root * $(PWD)/Kolam/dist|g' Caddyfile
	@echo "Starting Weaver backend..."
	@cd Weaver && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../weaver.log 2>&1 & echo $$! > ../weaver.pid
	@sleep 1
	@echo "Weaver backend started (PID: $$(cat weaver.pid))"
	@echo "Starting Caddy server..."
	@caddy start --config $(PWD)/Caddyfile --adapter caddyfile 2>&1 | tee caddy.log
	@sleep 1
	@echo "✓ Production server started"
	@echo "  Application: http://0.0.0.0:8080"
	@echo "  Backend: http://localhost:8000 (internal)"
	@echo "  Logs: weaver.log, caddy.log"
	@echo ""
	@echo "Verify frontend path: $(PWD)/Kolam/dist"

prod-stop:
	@echo "Stopping all production servers..."
	@echo ""
	@echo "Stopping Caddy..."
	@caddy stop 2>/dev/null && echo "  ✓ Caddy stopped gracefully" || echo "  - Caddy not running or already stopped"
	@sleep 1
	@pkill -9 -f "caddy" 2>/dev/null && echo "  ✓ Force killed remaining Caddy processes" || true
	@echo ""
	@echo "Stopping Weaver backend..."
	@pkill -9 -f "uvicorn" 2>/dev/null && echo "  ✓ uvicorn killed" || echo "  - No uvicorn processes"
	@pkill -9 -f "python.*app.main" 2>/dev/null || true
	@pkill -9 -f "uv run" 2>/dev/null || true
	@echo ""
	@echo "Cleaning up PID files..."
	@rm -f weaver.pid
	@sleep 2
	@echo ""
	@echo "Final verification..."
	@ps aux | grep -E "(uvicorn|caddy)" | grep -v grep || echo "  ✓ All processes stopped"
	@echo ""
	@echo "✓ All production servers stopped"

# Check status of running services
status:
	@echo "Checking Texture services status..."
	@echo ""
	@echo "Backend (Weaver):"
	@if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then \
		echo "  ✓ Running (PID: $$(pgrep -f 'uvicorn app.main:app'))"; \
	else \
		echo "  ✗ Not running"; \
	fi
	@echo ""
	@echo "Frontend (Kolam dev server):"
	@if pgrep -f "rsbuild dev" > /dev/null 2>&1; then \
		echo "  ✓ Running (PID: $$(pgrep -f 'rsbuild dev'))"; \
	else \
		echo "  ✗ Not running"; \
	fi
	@echo ""
	@echo "Caddy (Production):"
	@if pgrep -f "caddy" > /dev/null 2>&1; then \
		echo "  ✓ Running (PID: $$(pgrep -f 'caddy'))"; \
	else \
		echo "  ✗ Not running"; \
	fi
	@echo ""
	@if [ -f weaver.pid ]; then \
		echo "PID files found: weaver.pid"; \
	fi
	@if [ -f kolam.pid ]; then \
		echo "PID files found: kolam.pid"; \
	fi
