.PHONY: help install dev build run test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	go mod download
	go mod tidy

dev: ## Run in development mode
	go run cmd/loom/*.go serve

build: ## Build the binary
	go build -o bin/loom cmd/loom/*.go

run: build ## Build and run the binary
	./bin/loom

test: ## Run tests
	go test -v ./...

clean: ## Clean build artifacts
	rm -rf bin/
	go clean

deps: ## Add required dependencies
	go get github.com/danielgtaylor/huma/v2
	go get github.com/danielgtaylor/huma/v2/adapters/humachi
	go get github.com/go-chi/chi/v5
	go get github.com/go-chi/cors
	go get github.com/clerk/clerk-sdk-go/v2
	go get github.com/joho/godotenv
	go mod tidy
