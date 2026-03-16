.PHONY: start stop

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
