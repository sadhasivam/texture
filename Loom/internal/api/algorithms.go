package api

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/sadhasivam/texture/internal/services"
)

// AlgorithmMetadataResponse is the frontend-friendly format for algorithm details
type AlgorithmMetadataResponse struct {
	ID              string                 `json:"id"`
	Name            string                 `json:"name"`
	Category        string                 `json:"category"`
	Group           string                 `json:"group"`
	Subgroup        string                 `json:"subgroup"`
	Description     string                 `json:"description"`
	Tags            []string               `json:"tags"`
	Difficulty      string                 `json:"difficulty"`
	ModelFamily     string                 `json:"model_family"`
	Target          TargetConfig           `json:"target"`
	Features        FeaturesConfig         `json:"features"`
	Parameters      []ParameterConfig      `json:"parameters"`
	Outputs         OutputsConfig          `json:"outputs"`
	ValidationRules []string               `json:"validation_rules"`
}

type TargetConfig struct {
	Required     bool     `json:"required"`
	AllowedTypes []string `json:"allowed_types"`
	Cardinality  string   `json:"cardinality"`
}

type FeaturesConfig struct {
	Required     bool     `json:"required"`
	MinColumns   int      `json:"min_columns"`
	MaxColumns   *int     `json:"max_columns"`
	AllowedTypes []string `json:"allowed_types"`
}

type ParameterConfig struct {
	Name    string   `json:"name"`
	Type    string   `json:"type"`
	Default any      `json:"default"`
	Label   string   `json:"label"`
	Options []string `json:"options"`
}

type OutputsConfig struct {
	Metrics []string `json:"metrics"`
	Charts  []string `json:"charts"`
	Tables  []string `json:"tables"`
}

// RegisterAlgorithmRoutes registers algorithm-related routes using Chi
func RegisterAlgorithmRoutes(router chi.Router, algoService *services.AlgorithmService) {
	router.Route("/api/v1/algorithms", func(r chi.Router) {
		// GET /api/v1/algorithms - List all algorithms
		r.Get("/", func(w http.ResponseWriter, r *http.Request) {
			algorithms := algoService.ListAlgorithms()

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(algorithms)
		})

		// GET /api/v1/algorithms/{id} - Get algorithm metadata
		r.Get("/{id}", func(w http.ResponseWriter, r *http.Request) {
			id := chi.URLParam(r, "id")

			spec, err := algoService.GetAlgorithm(id)
			if err != nil {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusNotFound)
				json.NewEncoder(w).Encode(map[string]string{
					"error": err.Error(),
				})
				return
			}

			// Transform to frontend-friendly format
			metadata := transformToMetadataResponse(spec)

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(metadata)
		})
	})
}

// transformToMetadataResponse converts AlgorithmSpec to frontend-friendly format
func transformToMetadataResponse(spec *services.AlgorithmSpec) AlgorithmMetadataResponse {
	// Derive group and subgroup
	category := spec.Metadata.Labels["category"]
	if category == "" {
		category = "general"
	}

	// Derive group from namespace
	group := ""
	if spec.Metadata.Namespace != "" {
		parts := make([]rune, 0)
		for _, r := range spec.Metadata.Namespace {
			if r == '-' {
				break
			}
			parts = append(parts, r)
		}
		group = string(parts)
	}
	if category == "anomaly_detection" {
		group = "anomaly_detection"
	}

	subgroup := category

	// Extract metric names
	metricNames := make([]string, 0, len(spec.Spec.Outputs.Metrics))
	for _, m := range spec.Spec.Outputs.Metrics {
		if name, ok := m["name"].(string); ok {
			metricNames = append(metricNames, name)
		}
	}

	// Extract chart names
	chartNames := make([]string, 0, len(spec.Spec.Outputs.Visualizations))
	for _, v := range spec.Spec.Outputs.Visualizations {
		if name, ok := v["name"].(string); ok {
			chartNames = append(chartNames, name)
		}
	}

	// Extract table names
	tableNames := make([]string, 0, len(spec.Spec.Outputs.Tables))
	for _, t := range spec.Spec.Outputs.Tables {
		if name, ok := t["name"].(string); ok {
			tableNames = append(tableNames, name)
		}
	}

	// Transform parameters
	params := make([]ParameterConfig, 0, len(spec.Spec.Parameters))
	for _, p := range spec.Spec.Parameters {
		params = append(params, ParameterConfig{
			Name:    p.Name,
			Type:    p.Type,
			Default: p.Default,
			Label:   p.Label,
			Options: nil, // Will be populated if parameter has options
		})
	}

	return AlgorithmMetadataResponse{
		ID:          spec.Spec.ID,
		Name:        spec.Metadata.DisplayName,
		Category:    category,
		Group:       group,
		Subgroup:    subgroup,
		Description: spec.Spec.Description,
		Tags:        spec.Spec.Tags,
		Difficulty:  spec.Spec.Difficulty,
		ModelFamily: spec.Spec.ModelFamily,
		Target: TargetConfig{
			Required:     spec.Spec.Target.Required,
			AllowedTypes: spec.Spec.Target.Types,
			Cardinality:  spec.Spec.Target.Cardinality,
		},
		Features: FeaturesConfig{
			Required:     spec.Spec.Features.Required,
			MinColumns:   spec.Spec.Features.Min,
			MaxColumns:   spec.Spec.Features.Max,
			AllowedTypes: spec.Spec.Features.Types,
		},
		Parameters:      params,
		Outputs: OutputsConfig{
			Metrics: metricNames,
			Charts:  chartNames,
			Tables:  tableNames,
		},
		ValidationRules: spec.Spec.ValidationRules,
	}
}
