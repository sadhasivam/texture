package server

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/clerk/clerk-sdk-go/v2"
	"github.com/danielgtaylor/huma/v2"
	"github.com/danielgtaylor/huma/v2/adapters/humachi"
	"github.com/go-chi/chi/v5"
	chimiddleware "github.com/go-chi/chi/v5/middleware"
	"github.com/sadhasivam/texture/internal/api"
	"github.com/sadhasivam/texture/internal/config"
	grpcclient "github.com/sadhasivam/texture/internal/grpc"
	"github.com/sadhasivam/texture/internal/middleware"
	"github.com/sadhasivam/texture/internal/services"
)

// Server represents the Loom HTTP server
type Server struct {
	config     *config.Config
	httpServer *http.Server
	grpcClient *grpcclient.Client
}

// New creates and configures a new Server instance
func New(ctx context.Context, cfg *config.Config) (*Server, error) {
	// Initialize Clerk SDK with secret key
	if cfg.ClerkSecretKey != "" {
		clerk.SetKey(cfg.ClerkSecretKey)
		log.Printf("🔐 Clerk JWT authentication enabled - using JWT template")
	} else {
		log.Printf("⚠️  Warning: CLERK_SECRET_KEY not set - running without authentication")
	}

	// Create Chi router
	router := chi.NewRouter()

	// Add Chi middleware
	router.Use(chimiddleware.RequestID)
	router.Use(chimiddleware.RealIP)
	router.Use(chimiddleware.Logger)
	router.Use(chimiddleware.Recoverer)
	router.Use(middleware.CORS())

	// Create gRPC client to Weaver
	grpcClient, err := grpcclient.NewClient(cfg.WeaverGRPCURL)
	if err != nil {
		return nil, fmt.Errorf("failed to create gRPC client: %w", err)
	}

	// Test connection to Weaver
	log.Printf("Testing connection to Weaver gRPC service at %s...", cfg.WeaverGRPCURL)
	healthResp, err := grpcClient.HealthCheck(ctx)
	if err != nil {
		log.Printf("Warning: Could not connect to Weaver: %v", err)
	} else {
		log.Printf("Weaver healthy - Python %s, %d algorithms loaded",
			healthResp.PythonVersion, len(healthResp.AvailableAlgorithms))
	}

	// Create algorithm service (reads YAML specs from Weaver)
	log.Printf("Loading algorithm specs from %s", cfg.AlgorithmSpecsPath)
	algoService, err := services.NewAlgorithmService(cfg.AlgorithmSpecsPath)
	if err != nil {
		grpcClient.Close()
		return nil, fmt.Errorf("failed to create algorithm service: %w", err)
	}
	log.Printf("Loaded %d algorithms from YAML specs", algoService.GetAlgorithmCount())

	// Create dataset service
	datasetService, err := services.NewDatasetService(cfg.DatasetStoragePath, grpcClient)
	if err != nil {
		grpcClient.Close()
		return nil, fmt.Errorf("failed to create dataset service: %w", err)
	}
	log.Printf("Dataset storage: %s", cfg.DatasetStoragePath)

	// Create Huma API with Chi adapter for public routes
	humaConfig := huma.DefaultConfig("Texture API", "1.0.0")
	humaConfig.Servers = []*huma.Server{
		{URL: fmt.Sprintf("http://localhost:%s", cfg.Port)},
	}
	humaAPI := humachi.New(router, humaConfig)

	// Register public routes (Huma for OpenAPI docs)
	api.RegisterHealthRoutes(humaAPI, cfg.Environment)

	// Register algorithm routes using Chi (reads from YAML specs)
	api.RegisterAlgorithmRoutes(router, algoService)

	// Register dataset routes using Chi (upload + schema inference + Clerk auth)
	api.RegisterDatasetRoutes(router, datasetService)

	// Register run routes using Chi (supports file upload + Clerk auth)
	api.RegisterRunRoutesWithChi(router, grpcClient, datasetService)

	// Protected routes (require Clerk auth) - only if clerk is configured
	if cfg.ClerkSecretKey != "" {
		router.Group(func(r chi.Router) {
			r.Use(middleware.ClerkAuth())

			// Create a new Huma API instance for protected routes
			protectedAPI := humachi.New(r, humaConfig)

			// Register protected routes
			api.RegisterAuthRoutes(protectedAPI)
		})
	}

	// Create HTTP server
	httpServer := &http.Server{
		Addr:         fmt.Sprintf(":%s", cfg.Port),
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Log startup information
	allowedOrigins := "same-origin only (CORS disabled)"
	if origins := os.Getenv("ALLOWED_ORIGINS"); origins != "" {
		allowedOrigins = origins
	}
	log.Printf("Starting Loom server on %s", httpServer.Addr)
	log.Printf("Environment: %s", cfg.Environment)
	log.Printf("CORS: %s", allowedOrigins)
	log.Printf("Weaver gRPC: %s", cfg.WeaverGRPCURL)
	log.Printf("OpenAPI docs: http://localhost:%s/docs", cfg.Port)

	return &Server{
		config:     cfg,
		httpServer: httpServer,
		grpcClient: grpcClient,
	}, nil
}

// Run starts the HTTP server (blocking)
func (s *Server) Run() error {
	return s.httpServer.ListenAndServe()
}

// Shutdown gracefully shuts down the server
func (s *Server) Shutdown(ctx context.Context) error {
	log.Printf("Shutting down server...")

	// Shutdown HTTP server
	if err := s.httpServer.Shutdown(ctx); err != nil {
		log.Printf("Error shutting down HTTP server: %v", err)
	}

	// Close gRPC client
	if s.grpcClient != nil {
		if err := s.grpcClient.Close(); err != nil {
			log.Printf("Error closing gRPC client: %v", err)
		}
	}

	log.Printf("Server shutdown complete")
	return nil
}
