import type { AlgorithmMetadata, AlgorithmSummary } from '../types/algorithm';
import type { DatasetDetails, DatasetUploadResponse } from '../types/dataset';
import type { RunRequest, RunResponse } from '../types/run';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.LOOM_API_URL || 'http://localhost:8080/api/v1';

// Store for auth token getter function
let getTokenFn: (() => Promise<string | null>) | null = null;

// Set auth token getter (called from a component with useAuth hook)
export function setAuthTokenGetter(fn: () => Promise<string | null>) {
  getTokenFn = fn;
}

// Helper to get auth headers
async function getAuthHeaders(): Promise<HeadersInit> {
  const headers: HeadersInit = {};

  if (getTokenFn) {
    const token = await getTokenFn();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  return headers;
}

export const api = {
  // Health check
  async health(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },

  // Algorithms
  async listAlgorithms(): Promise<AlgorithmSummary[]> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/algorithms`, { headers });
    if (!response.ok) throw new Error('Failed to fetch algorithms');
    return response.json();
  },

  async getAlgorithmMetadata(algorithmId: string): Promise<AlgorithmMetadata> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/algorithms/${algorithmId}`, { headers });
    if (!response.ok) throw new Error(`Failed to fetch metadata for ${algorithmId}`);
    return response.json();
  },

  // Datasets
  async uploadDataset(file: File): Promise<DatasetUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const headers = await getAuthHeaders();

    const response = await fetch(`${API_BASE_URL}/datasets/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload dataset');
    }

    return response.json();
  },

  async getDataset(datasetId: string): Promise<DatasetDetails> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, { headers });
    if (!response.ok) throw new Error(`Failed to fetch dataset ${datasetId}`);
    return response.json();
  },

  // Runs
  async createRun(request: RunRequest): Promise<RunResponse> {
    const authHeaders = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.detail || 'Failed to create run');
    }

    return response.json();
  },

  async getRun(runId: string): Promise<RunResponse> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/runs/${runId}`, { headers });
    if (!response.ok) throw new Error(`Failed to fetch run ${runId}`);
    return response.json();
  },
};
