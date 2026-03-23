package api

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/go-chi/chi/v5"
	chimiddleware "github.com/go-chi/chi/v5/middleware"

	grpcclient "github.com/sadhasivam/texture/internal/grpc"
	"github.com/sadhasivam/texture/internal/middleware"
	"github.com/sadhasivam/texture/internal/services"
	"github.com/sadhasivam/texture/pb"
)

// RunRequest represents a run creation request
type RunRequest struct {
	AlgorithmID    string                 `json:"algorithm_id"`
	DatasetID      string                 `json:"dataset_id,omitempty"`      // Dataset ID from previous upload
	DatasetCSV     string                 `json:"dataset_csv,omitempty"`     // Inline CSV data for test endpoint
	TargetColumn   string                 `json:"target_column"`
	FeatureColumns []string               `json:"feature_columns"`
	Parameters     map[string]interface{} `json:"parameters"`
}

// RunResult contains the ML execution results
type RunResult struct {
	Status       string             `json:"status"`
	Summary      map[string]any     `json:"summary,omitempty"`
	Metrics      map[string]float64 `json:"metrics,omitempty"`
	Charts       []Chart            `json:"charts,omitempty"`
	Tables       []Table            `json:"tables,omitempty"`
	Explanations []string           `json:"explanations,omitempty"`
	Warnings     []string           `json:"warnings,omitempty"`
	ErrorMessage string             `json:"error_message,omitempty"`
}

// Chart represents visualization data
type Chart struct {
	Type    string                   `json:"type"`
	Title   string                   `json:"title"`
	Data    []map[string]float64     `json:"data"`
	Options map[string]string        `json:"options,omitempty"`
}

// Table represents tabular data
type Table struct {
	Type    string              `json:"type"`
	Columns []string            `json:"columns"`
	Rows    []map[string]string `json:"rows"`
}

// RegisterRunRoutesWithChi registers file upload route using native Chi with Clerk auth
func RegisterRunRoutesWithChi(router chi.Router, grpcClient *grpcclient.Client, datasetService *services.DatasetService) {
	// POST /api/v1/runs - Create and execute a run with file upload (requires Clerk auth)
	router.Route("/api/v1/runs", func(r chi.Router) {
		// Apply Clerk auth middleware to all routes in this group
		r.Use(middleware.ClerkAuth())

		r.Post("/", func(w http.ResponseWriter, r *http.Request) {
			contentType := r.Header.Get("Content-Type")

			// Handle JSON request body (from UI with dataset_id)
			if contentType == "application/json" {
				var req RunRequest
				if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
					w.Header().Set("Content-Type", "application/json")
					w.WriteHeader(http.StatusBadRequest)
					json.NewEncoder(w).Encode(map[string]string{
						"error": fmt.Sprintf("Invalid request body: %v", err),
					})
					return
				}

				result, err := executeRunFromJSONRequest(r.Context(), grpcClient, datasetService, req)
				if err != nil {
					w.Header().Set("Content-Type", "application/json")
					w.WriteHeader(http.StatusInternalServerError)
					json.NewEncoder(w).Encode(map[string]string{
						"error": err.Error(),
					})
					return
				}

				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusOK)
				json.NewEncoder(w).Encode(result)
				return
			}

			// Handle multipart/form-data (direct file upload)
			// Parse multipart form (32MB max)
			if err := r.ParseMultipartForm(32 << 20); err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusBadRequest)
				json.NewEncoder(w).Encode(map[string]string{
					"error": fmt.Sprintf("Failed to parse form: %v", err),
				})
				return
			}

			// Get CSV file
			file, _, err := r.FormFile("file")
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusBadRequest)
				json.NewEncoder(w).Encode(map[string]string{
					"error": fmt.Sprintf("Missing or invalid file: %v", err),
				})
				return
			}
			defer file.Close()

			// Read CSV data
			csvData, err := io.ReadAll(file)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusInternalServerError)
				json.NewEncoder(w).Encode(map[string]string{
					"error": fmt.Sprintf("Failed to read file: %v", err),
				})
				return
			}

			// Get form parameters
			algorithmID := r.FormValue("algorithm_id")
			targetColumn := r.FormValue("target_column")

			// Parse feature_columns JSON array
			featureColumnsJSON := r.FormValue("feature_columns")
			var featureColumns []string
			if err := json.Unmarshal([]byte(featureColumnsJSON), &featureColumns); err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusBadRequest)
				json.NewEncoder(w).Encode(map[string]string{
					"error": fmt.Sprintf("Invalid feature_columns: %v", err),
				})
				return
			}

			// Parse parameters JSON object
			parametersJSON := r.FormValue("parameters")
			var parameters map[string]string
			if parametersJSON != "" {
				if err := json.Unmarshal([]byte(parametersJSON), &parameters); err != nil {
					w.Header().Set("Content-Type", "application/json")
					w.WriteHeader(http.StatusBadRequest)
					json.NewEncoder(w).Encode(map[string]string{
						"error": fmt.Sprintf("Invalid parameters: %v", err),
					})
					return
				}
			}

			// Build gRPC request
			requestID := chimiddleware.GetReqID(r.Context())
			grpcReq := &pb.ExecuteRunRequest{
				AlgorithmId:    algorithmID,
				DatasetCsv:     csvData,
				TargetColumn:   targetColumn,
				FeatureColumns: featureColumns,
				Parameters:     parameters,
				RequestId:      requestID,
			}

			// Call Python gRPC service
			grpcResp, err := grpcClient.ExecuteRun(r.Context(), grpcReq)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusInternalServerError)
				json.NewEncoder(w).Encode(map[string]string{
					"error": fmt.Sprintf("Failed to execute run: %v", err),
				})
				return
			}

			// Check for errors
			if grpcResp.Status != "success" {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusBadRequest)
				json.NewEncoder(w).Encode(map[string]string{
					"error": grpcResp.ErrorMessage,
				})
				return
			}

			// Convert protobuf response to JSON response
			result := convertProtoToResult(grpcResp)

			// Return success response
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(result)
		})

		// POST /api/v1/runs/test - Test endpoint with inline CSV (requires Clerk auth)
		r.Post("/test", func(w http.ResponseWriter, r *http.Request) {
			var req RunRequest
			if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusBadRequest)
				json.NewEncoder(w).Encode(map[string]string{
					"error": fmt.Sprintf("Invalid request body: %v", err),
				})
				return
			}

			result, err := executeRunFromRequest(r.Context(), grpcClient, req)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusInternalServerError)
				json.NewEncoder(w).Encode(map[string]string{
					"error": err.Error(),
				})
				return
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(result)
		})
	})
}

// executeRunFromJSONRequest handles run execution from JSON request with dataset_id
func executeRunFromJSONRequest(ctx context.Context, grpcClient *grpcclient.Client, datasetService *services.DatasetService, req RunRequest) (RunResult, error) {
	// Get CSV data from dataset service
	csvData, err := datasetService.GetDatasetCSV(req.DatasetID)
	if err != nil {
		return RunResult{}, fmt.Errorf("failed to get dataset: %w", err)
	}

	// Convert parameters from interface{} to string
	parameters := make(map[string]string)
	for k, v := range req.Parameters {
		parameters[k] = fmt.Sprintf("%v", v)
	}

	// Build gRPC request
	requestID := chimiddleware.GetReqID(ctx)
	grpcReq := &pb.ExecuteRunRequest{
		AlgorithmId:    req.AlgorithmID,
		DatasetCsv:     csvData,
		TargetColumn:   req.TargetColumn,
		FeatureColumns: req.FeatureColumns,
		Parameters:     parameters,
		RequestId:      requestID,
	}

	// Call Python gRPC service
	grpcResp, err := grpcClient.ExecuteRun(ctx, grpcReq)
	if err != nil {
		return RunResult{}, fmt.Errorf("failed to execute run: %w", err)
	}

	// Check for errors
	if grpcResp.Status != "success" {
		return RunResult{
			Status:       "error",
			ErrorMessage: grpcResp.ErrorMessage,
		}, nil
	}

	// Convert protobuf response to JSON response
	result := convertProtoToResult(grpcResp)
	return result, nil
}

// executeRunFromRequest is a helper to execute a run from a RunRequest with inline CSV
func executeRunFromRequest(ctx context.Context, grpcClient *grpcclient.Client, req RunRequest) (RunResult, error) {
	// Convert parameters from interface{} to string
	parameters := make(map[string]string)
	for k, v := range req.Parameters {
		parameters[k] = fmt.Sprintf("%v", v)
	}

	// Build gRPC request
	grpcReq := &pb.ExecuteRunRequest{
		AlgorithmId:    req.AlgorithmID,
		DatasetCsv:     []byte(req.DatasetCSV),
		TargetColumn:   req.TargetColumn,
		FeatureColumns: req.FeatureColumns,
		Parameters:     parameters,
		RequestId:      fmt.Sprintf("req_%v", ctx.Value("request_id")),
	}

	// Call Python gRPC service
	grpcResp, err := grpcClient.ExecuteRun(ctx, grpcReq)
	if err != nil {
		return RunResult{}, fmt.Errorf("failed to execute run: %w", err)
	}

	// Check for errors
	if grpcResp.Status != "success" {
		return RunResult{
			Status:       "error",
			ErrorMessage: grpcResp.ErrorMessage,
		}, nil
	}

	// Convert protobuf response to JSON response
	result := convertProtoToResult(grpcResp)
	return result, nil
}

// convertProtoToResult converts protobuf ExecuteRunResponse to RunResult
func convertProtoToResult(proto *pb.ExecuteRunResponse) RunResult {
	result := RunResult{
		Status:       proto.Status,
		Metrics:      proto.Metrics,
		Explanations: proto.Explanations,
		Warnings:     proto.Warnings,
		ErrorMessage: proto.ErrorMessage,
	}

	// Convert summary
	if proto.Summary != nil {
		result.Summary = map[string]any{
			"target_column":   proto.Summary.TargetColumn,
			"feature_columns": proto.Summary.FeatureColumns,
			"train_rows":      proto.Summary.TrainRows,
			"test_rows":       proto.Summary.TestRows,
			"parameters":      proto.Summary.Parameters,
		}
	}

	// Convert charts
	for _, chart := range proto.Charts {
		data := make([]map[string]float64, len(chart.Data))
		for i, point := range chart.Data {
			data[i] = point.Values
		}

		result.Charts = append(result.Charts, Chart{
			Type:    chart.Type,
			Title:   chart.Title,
			Data:    data,
			Options: chart.Options,
		})
	}

	// Convert tables
	for _, table := range proto.Tables {
		rows := make([]map[string]string, len(table.Rows))
		for i, row := range table.Rows {
			rows[i] = row.Cells
		}

		result.Tables = append(result.Tables, Table{
			Type:    table.Type,
			Columns: table.Columns,
			Rows:    rows,
		})
	}

	return result
}
