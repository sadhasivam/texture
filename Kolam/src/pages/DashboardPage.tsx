import { useState } from 'react';
import AlgorithmSidebar from '../features/algorithms/AlgorithmSidebar';
import DatasetUpload from '../features/dataset/DatasetUpload';
import DatasetPreview from '../features/dataset/DatasetPreview';
import MappingForm from '../features/mapping/MappingForm';
import ResultsPanel from '../features/results/ResultsPanel';
import type { AlgorithmMetadata } from '../types/algorithm';
import type { DatasetUploadResponse } from '../types/dataset';
import type { RunResponse } from '../types/run';
import './DashboardPage.css';

export default function DashboardPage() {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<AlgorithmMetadata | null>(null);
  const [dataset, setDataset] = useState<DatasetUploadResponse | null>(null);
  const [runResult, setRunResult] = useState<RunResponse | null>(null);

  const handleReset = () => {
    setDataset(null);
    setRunResult(null);
  };

  const handleNewRun = () => {
    setRunResult(null);
  };

  const handleSelectAlgorithm = (metadata: AlgorithmMetadata) => {
    setSelectedAlgorithm(metadata);
    setDataset(null);
    setRunResult(null);
  };

  return (
    <div className="dashboard">
      <header className="app-header">
        <div className="app-branding">Texture</div>
        <div className="app-header-actions">
          <div className="user-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <AlgorithmSidebar
          selectedAlgorithmId={selectedAlgorithm?.id}
          onSelectAlgorithm={handleSelectAlgorithm}
        />

        <main className="workspace">

        {!selectedAlgorithm && (
          <div className="placeholder">
            <p>Select an algorithm from the sidebar to get started</p>
          </div>
        )}

        {selectedAlgorithm && (
          <div className="work-area">
            <div className="input-section">
              <div className="section-header">
                <h2>{selectedAlgorithm.name}</h2>
                <p>{selectedAlgorithm.description}</p>
              </div>

              {!dataset && (
                <DatasetUpload onUploadComplete={setDataset} />
              )}

              {dataset && (
                <>
                  <DatasetPreview dataset={dataset} />
                  <MappingForm
                    algorithm={selectedAlgorithm}
                    dataset={dataset}
                    onRunComplete={setRunResult}
                  />
                </>
              )}
            </div>

            <div className="output-section">
              {!runResult && (
                <div className="output-placeholder">
                  <p>Results will appear here after running the algorithm</p>
                </div>
              )}

              {runResult && (
                <>
                  <div className="results-actions">
                    <button onClick={handleNewRun} className="action-button">
                      New Run
                    </button>
                    <button onClick={handleReset} className="action-button secondary">
                      New Dataset
                    </button>
                  </div>
                  <ResultsPanel result={runResult} />
                </>
              )}
            </div>
          </div>
        )}
      </main>
      </div>
    </div>
  );
}
