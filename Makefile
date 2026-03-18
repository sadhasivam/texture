.PHONY: build start stop status

# Export PATH to include pnpm and uv
export PNPM_HOME := $(HOME)/.local/share/pnpm
export PATH := $(PNPM_HOME):$(HOME)/.local/bin:$(HOME)/.cargo/bin:$(PATH)

# Build frontend
build:
	@echo "Building Kolam frontend..."
	@cd Kolam && pnpm build
	@echo "✓ Frontend built to Kolam/dist"

# Start all servers in production mode
start: build
	@echo "Starting Weaver backend..."
	@cd Weaver && nohup .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../weaver.log 2>&1 & echo $$! > ../weaver.pid
	@sleep 2
	@echo "Weaver backend started (PID: $$(cat weaver.pid))"
	@echo "Verifying backend is running..."
	@if pgrep -f "uvicorn app.main:app" > /dev/null; then \
		echo "  ✓ Backend is running"; \
	else \
		echo "  ✗ Backend failed to start - check weaver.log"; \
		tail -20 weaver.log; \
	fi
	@echo "Starting Caddy server..."
	@caddy start --config $(PWD)/Caddyfile --adapter caddyfile > caddy.log 2>&1
	@sleep 1
	@echo "✓ Production server started"
	@echo "  Application: http://0.0.0.0:8080"
	@echo "  Backend: http://localhost:8000 (internal)"
	@echo "  Logs: weaver.log, caddy.log"
	@echo ""
	@echo "Both servers running in background. Safe to close terminal."
	@echo "Check status: make status"
	@echo "Stop servers: make stop"

# Stop all servers
stop:
	@echo "Stopping all servers..."
	@echo ""
	@echo "Stopping Caddy..."
	@caddy stop 2>/dev/null && echo "  ✓ Caddy stopped" || echo "  - Caddy not running"
	@pkill -9 -f "caddy" 2>/dev/null || true
	@echo ""
	@echo "Stopping backend..."
	@if [ -f weaver.pid ]; then \
		PID=$$(cat weaver.pid 2>/dev/null); \
		if [ -n "$$PID" ] && kill -0 $$PID 2>/dev/null; then \
			kill -9 $$PID && echo "  ✓ Backend stopped (PID $$PID)"; \
		fi; \
	fi
	@pkill -9 -f "uvicorn app.main:app" 2>/dev/null && echo "  ✓ Killed uvicorn processes" || true
	@pkill -9 -f ".venv/bin/python -m uvicorn" 2>/dev/null || true
	@pkill -9 -f "python -m uvicorn" 2>/dev/null || true
	@echo ""
	@echo "Cleaning up..."
	@rm -f weaver.pid
	@sleep 1
	@echo ""
	@if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then \
		echo "⚠ Warning: Backend still running!"; \
		ps aux | grep "uvicorn" | grep -v grep; \
	else \
		echo "✓ All servers stopped"; \
	fi

# Check status
status:
	@echo "Texture Status"
	@echo "=============="
	@echo ""
	@echo "Backend (Weaver):"
	@if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then \
		echo "  ✓ Running (PID: $$(pgrep -f 'uvicorn app.main:app'))"; \
	else \
		echo "  ✗ Not running"; \
	fi
	@echo ""
	@echo "Caddy:"
	@if pgrep -f "caddy" > /dev/null 2>&1; then \
		echo "  ✓ Running (PID: $$(pgrep -f 'caddy'))"; \
	else \
		echo "  ✗ Not running"; \
	fi
