import type { AlgorithmMetadata, AlgorithmSummary } from '../types/algorithm';
import type { DatasetDetails, DatasetUploadResponse } from '../types/dataset';
import type { RunRequest, RunResponse } from '../types/run';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = {
  // Health check
  async health(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },

  // Algorithms
  async listAlgorithms(): Promise<AlgorithmSummary[]> {
    const response = await fetch(`${API_BASE_URL}/algorithms`);
    if (!response.ok) throw new Error('Failed to fetch algorithms');
    return response.json();
  },

  async getAlgorithmMetadata(algorithmId: string): Promise<AlgorithmMetadata> {
    const response = await fetch(`${API_BASE_URL}/algorithms/${algorithmId}`);
    if (!response.ok) throw new Error(`Failed to fetch metadata for ${algorithmId}`);
    return response.json();
  },

  // Datasets
  async uploadDataset(file: File): Promise<DatasetUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/datasets/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload dataset');
    }

    return response.json();
  },

  async getDataset(datasetId: string): Promise<DatasetDetails> {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`);
    if (!response.ok) throw new Error(`Failed to fetch dataset ${datasetId}`);
    return response.json();
  },

  // Runs
  async createRun(request: RunRequest): Promise<RunResponse> {
    const response = await fetch(`${API_BASE_URL}/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create run');
    }

    return response.json();
  },

  async getRun(runId: string): Promise<RunResponse> {
    const response = await fetch(`${API_BASE_URL}/runs/${runId}`);
    if (!response.ok) throw new Error(`Failed to fetch run ${runId}`);
    return response.json();
  },
};
