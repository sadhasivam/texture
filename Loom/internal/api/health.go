package api

import (
	"context"
	"net/http"

	"github.com/danielgtaylor/huma/v2"
)

// HealthResponse represents the health check response
type HealthResponse struct {
	Body struct {
		Status      string `json:"status" example:"ok"`
		Environment string `json:"environment" example:"development"`
	}
}

// RegisterHealthRoutes registers health check routes
func RegisterHealthRoutes(api huma.API, environment string) {
	huma.Register(api, huma.Operation{
		OperationID: "health-check",
		Method:      http.MethodGet,
		Path:        "/api/v1/health",
		Summary:     "Health check",
		Description: "Returns the health status of the service",
		Tags:        []string{"Health"},
	}, func(ctx context.Context, input *struct{}) (*HealthResponse, error) {
		resp := &HealthResponse{}
		resp.Body.Status = "ok"
		resp.Body.Environment = environment
		return resp, nil
	})
}
