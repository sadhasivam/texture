package services

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sync"

	grpcclient "github.com/sadhasivam/texture/internal/grpc"
	"github.com/sadhasivam/texture/pb"
)

// DatasetMetadata represents metadata about an uploaded dataset
type DatasetMetadata struct {
	ID          string                `json:"id"`
	Filename    string                `json:"filename"`
	RowCount    int                   `json:"row_count"`
	ColumnCount int                   `json:"column_count"`
	Columns     []ColumnMetadata      `json:"columns"`
	PreviewRows []map[string]string   `json:"preview_rows"`
	FilePath    string                `json:"-"` // Internal use only
}

// ColumnMetadata represents column schema information
type ColumnMetadata struct {
	Name         string   `json:"name"`
	InferredType string   `json:"inferred_type"`
	MissingCount int      `json:"missing_count"`
	UniqueCount  int      `json:"unique_count"`
	SampleValues []string `json:"sample_values"`
}

// DatasetService manages dataset uploads and metadata
type DatasetService struct {
	storageDir  string
	grpcClient  *grpcclient.Client
	datasets    map[string]*DatasetMetadata
	datasetsMux sync.RWMutex
}

// NewDatasetService creates a new dataset service
func NewDatasetService(storageDir string, grpcClient *grpcclient.Client) (*DatasetService, error) {
	// Create storage directory if it doesn't exist
	if err := os.MkdirAll(storageDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create storage directory: %w", err)
	}

	return &DatasetService{
		storageDir: storageDir,
		grpcClient: grpcClient,
		datasets:   make(map[string]*DatasetMetadata),
	}, nil
}

// UploadDataset saves a CSV file and infers its schema via gRPC
func (s *DatasetService) UploadDataset(ctx context.Context, filename string, data []byte) (*DatasetMetadata, error) {
	// Generate unique dataset ID
	datasetID := generateID()

	// Save file to disk
	filePath := filepath.Join(s.storageDir, fmt.Sprintf("%s_%s", datasetID, filename))
	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return nil, fmt.Errorf("failed to save file: %w", err)
	}

	// Call Python gRPC service to infer schema
	grpcReq := &pb.InferSchemaRequest{
		DatasetCsv: data,
		DatasetId:  datasetID,
	}

	grpcResp, err := s.grpcClient.InferSchema(ctx, grpcReq)
	if err != nil {
		// Cleanup file on error
		os.Remove(filePath)
		return nil, fmt.Errorf("failed to infer schema: %w", err)
	}

	// Convert protobuf response to metadata
	columns := make([]ColumnMetadata, len(grpcResp.Columns))
	for i, col := range grpcResp.Columns {
		columns[i] = ColumnMetadata{
			Name:         col.Name,
			InferredType: col.InferredType,
			MissingCount: int(col.MissingCount),
			UniqueCount:  int(col.UniqueCount),
			SampleValues: col.SampleValues,
		}
	}

	previewRows := make([]map[string]string, len(grpcResp.PreviewRows))
	for i, row := range grpcResp.PreviewRows {
		previewRows[i] = row.Cells
	}

	metadata := &DatasetMetadata{
		ID:          datasetID,
		Filename:    filename,
		RowCount:    int(grpcResp.RowCount),
		ColumnCount: int(grpcResp.ColumnCount),
		Columns:     columns,
		PreviewRows: previewRows,
		FilePath:    filePath,
	}

	// Store metadata
	s.datasetsMux.Lock()
	s.datasets[datasetID] = metadata
	s.datasetsMux.Unlock()

	return metadata, nil
}

// GetDataset retrieves dataset metadata by ID
func (s *DatasetService) GetDataset(id string) (*DatasetMetadata, error) {
	s.datasetsMux.RLock()
	defer s.datasetsMux.RUnlock()

	metadata, ok := s.datasets[id]
	if !ok {
		return nil, fmt.Errorf("dataset '%s' not found", id)
	}

	return metadata, nil
}

// GetDatasetCSV returns the raw CSV data for a dataset
func (s *DatasetService) GetDatasetCSV(id string) ([]byte, error) {
	s.datasetsMux.RLock()
	metadata, ok := s.datasets[id]
	s.datasetsMux.RUnlock()

	if !ok {
		return nil, fmt.Errorf("dataset '%s' not found", id)
	}

	data, err := os.ReadFile(metadata.FilePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read dataset file: %w", err)
	}

	return data, nil
}

// generateID creates a random hex ID
func generateID() string {
	bytes := make([]byte, 8)
	rand.Read(bytes)
	return "ds_" + hex.EncodeToString(bytes)
}
