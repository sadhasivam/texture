package api

import (
	"encoding/json"
	"io"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/sadhasivam/texture/internal/middleware"
	"github.com/sadhasivam/texture/internal/services"
)

// RegisterDatasetRoutes registers dataset-related routes using Chi with Clerk auth
func RegisterDatasetRoutes(router chi.Router, datasetService *services.DatasetService) {
	router.Route("/api/v1/datasets", func(r chi.Router) {
		// Apply Clerk auth middleware to all dataset routes
		r.Use(middleware.ClerkAuth())
		// POST /api/v1/datasets/upload - Upload a CSV file
		r.Post("/upload", func(w http.ResponseWriter, r *http.Request) {
			// Parse multipart form (32MB max)
			if err := r.ParseMultipartForm(32 << 20); err != nil {
				http.Error(w, "Failed to parse form", http.StatusBadRequest)
				return
			}

			// Get CSV file
			file, header, err := r.FormFile("file")
			if err != nil {
				http.Error(w, "Missing or invalid file", http.StatusBadRequest)
				return
			}
			defer file.Close()

			// Read file data
			data, err := io.ReadAll(file)
			if err != nil {
				http.Error(w, "Failed to read file", http.StatusInternalServerError)
				return
			}

			// Upload and infer schema
			metadata, err := datasetService.UploadDataset(r.Context(), header.Filename, data)
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}

			// Return metadata
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(metadata)
		})

		// GET /api/v1/datasets/{id} - Get dataset metadata
		r.Get("/{id}", func(w http.ResponseWriter, r *http.Request) {
			id := chi.URLParam(r, "id")

			metadata, err := datasetService.GetDataset(id)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusNotFound)
				json.NewEncoder(w).Encode(map[string]string{
					"error": err.Error(),
				})
				return
			}

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(metadata)
		})
	})
}
