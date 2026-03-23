package services

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"
)

// AlgorithmSpec represents a parsed algorithm YAML spec
type AlgorithmSpec struct {
	APIVersion string `yaml:"apiVersion"`
	Kind       string `yaml:"kind"`
	Metadata   struct {
		Name        string            `yaml:"name"`
		DisplayName string            `yaml:"displayName"`
		Namespace   string            `yaml:"namespace"`
		Labels      map[string]string `yaml:"labels"`
	} `yaml:"metadata"`
	Spec struct {
		ID          string   `yaml:"id"`
		Description string   `yaml:"description"`
		Tags        []string `yaml:"tags"`
		Difficulty  string   `yaml:"difficulty"`
		ModelFamily string   `yaml:"modelFamily"`
		Target      struct {
			Required    bool     `yaml:"required"`
			Types       []string `yaml:"types"`
			Cardinality string   `yaml:"cardinality"`
			Nullable    bool     `yaml:"nullable"`
		} `yaml:"target"`
		Features struct {
			Required bool     `yaml:"required"`
			Types    []string `yaml:"types"`
			Min      int      `yaml:"min"`
			Max      *int     `yaml:"max"`
		} `yaml:"features"`
		Parameters []struct {
			Name    string  `yaml:"name"`
			Type    string  `yaml:"type"`
			Default any     `yaml:"default"`
			Label   string  `yaml:"label"`
		} `yaml:"parameters"`
		Outputs struct {
			Metrics        []map[string]any `yaml:"metrics"`
			Visualizations []map[string]any `yaml:"visualizations"`
			Tables         []map[string]any `yaml:"tables"`
		} `yaml:"outputs"`
		ValidationRules []string `yaml:"validationRules"`
	} `yaml:"spec"`
}

// AlgorithmSummary is a lightweight algorithm listing
type AlgorithmSummary struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Category    string   `json:"category"`
	Group       string   `json:"group"`
	Subgroup    string   `json:"subgroup"`
	Description string   `json:"description"`
	Tags        []string `json:"tags"`
	Difficulty  string   `json:"difficulty"`
	ModelFamily string   `json:"model_family"`
}

// AlgorithmService handles algorithm metadata operations
type AlgorithmService struct {
	specsPath string
	specs     map[string]*AlgorithmSpec
}

// NewAlgorithmService creates a new algorithm service
func NewAlgorithmService(specsPath string) (*AlgorithmService, error) {
	service := &AlgorithmService{
		specsPath: specsPath,
		specs:     make(map[string]*AlgorithmSpec),
	}

	if err := service.loadSpecs(); err != nil {
		return nil, err
	}

	return service, nil
}

// loadSpecs reads all YAML specs from the specs directory
func (s *AlgorithmService) loadSpecs() error {
	return filepath.Walk(s.specsPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories and non-YAML files
		if info.IsDir() || !strings.HasSuffix(info.Name(), ".yaml") {
			return nil
		}

		// Read and parse YAML
		data, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("failed to read %s: %w", path, err)
		}

		var spec AlgorithmSpec
		if err := yaml.Unmarshal(data, &spec); err != nil {
			return fmt.Errorf("failed to parse %s: %w", path, err)
		}

		// Only load Algorithm kind, skip Ontology and other kinds
		if spec.Kind != "Algorithm" {
			return nil
		}

		// Skip if spec has no ID (invalid algorithm spec)
		if spec.Spec.ID == "" {
			return nil
		}

		// Store by algorithm ID
		s.specs[spec.Spec.ID] = &spec

		return nil
	})
}

// ListAlgorithms returns all algorithm summaries
func (s *AlgorithmService) ListAlgorithms() []AlgorithmSummary {
	summaries := make([]AlgorithmSummary, 0, len(s.specs))

	for _, spec := range s.specs {
		category := spec.Metadata.Labels["category"]
		if category == "" {
			category = "general"
		}

		// Derive group from namespace (supervised-learning -> supervised, unsupervised-learning -> unsupervised)
		group := spec.Metadata.Labels["group"]
		if group == "" && spec.Metadata.Namespace != "" {
			// Extract group from namespace (e.g., "supervised-learning" -> "supervised")
			parts := strings.Split(spec.Metadata.Namespace, "-")
			if len(parts) > 0 {
				group = parts[0]
			}
		}
		// Special case for anomaly detection
		if category == "anomaly_detection" {
			group = "anomaly_detection"
		}

		// Subgroup is the same as category
		subgroup := spec.Metadata.Labels["subgroup"]
		if subgroup == "" {
			subgroup = category
		}

		tags := spec.Spec.Tags
		if tags == nil {
			tags = []string{}
		}

		summaries = append(summaries, AlgorithmSummary{
			ID:          spec.Spec.ID,
			Name:        spec.Metadata.DisplayName,
			Category:    category,
			Group:       group,
			Subgroup:    subgroup,
			Description: spec.Spec.Description,
			Tags:        tags,
			Difficulty:  spec.Spec.Difficulty,
			ModelFamily: spec.Spec.ModelFamily,
		})
	}

	return summaries
}

// GetAlgorithm returns full metadata for a specific algorithm
func (s *AlgorithmService) GetAlgorithm(id string) (*AlgorithmSpec, error) {
	spec, ok := s.specs[id]
	if !ok {
		return nil, fmt.Errorf("algorithm '%s' not found", id)
	}
	return spec, nil
}

// GetAlgorithmCount returns the number of loaded algorithms
func (s *AlgorithmService) GetAlgorithmCount() int {
	return len(s.specs)
}
