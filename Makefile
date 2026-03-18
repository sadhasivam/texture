.PHONY: start stop prod prod-stop build

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
	@echo "Stopping servers..."
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "uv run uvicorn" 2>/dev/null || true
	@pkill -f "rsbuild dev" 2>/dev/null || true
	@pkill -f "rsbuild-node" 2>/dev/null || true
	@pkill -f "pnpm dev" 2>/dev/null || true
	@rm -f weaver.pid kolam.pid
	@sleep 1
	@echo "✓ All servers stopped"

# Production mode (Caddy serves built frontend + proxies to backend)
build:
	@echo "Building Kolam frontend..."
	@cd Kolam && pnpm build
	@echo "✓ Frontend built to Kolam/dist"

prod: build
	@echo "Starting Weaver backend..."
	@cd Weaver && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../weaver.log 2>&1 & echo $$! > ../weaver.pid
	@echo "Weaver backend started (PID: $$(cat weaver.pid))"
	@echo "Starting Caddy server..."
	@caddy start --config Caddyfile > caddy.log 2>&1
	@echo "✓ Production server started"
	@echo "  Application: http://localhost:8080"
	@echo "  Backend: http://localhost:8000 (internal)"
	@echo "  Logs: weaver.log, caddy.log"

prod-stop:
	@echo "Stopping production servers..."
	@caddy stop 2>/dev/null || true
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "uv run uvicorn" 2>/dev/null || true
	@rm -f weaver.pid
	@sleep 1
	@echo "✓ Production servers stopped"
