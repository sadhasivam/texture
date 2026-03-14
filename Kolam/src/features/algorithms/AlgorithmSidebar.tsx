import { useState, useEffect } from 'react';
import { useAlgorithms, useAlgorithmMetadata } from './useAlgorithms';
import AlgorithmCard from './AlgorithmCard';
import type { AlgorithmMetadata } from '../../types/algorithm';
import './AlgorithmSidebar.css';

interface AlgorithmSidebarProps {
  selectedAlgorithmId?: string;
  onSelectAlgorithm: (metadata: AlgorithmMetadata) => void;
}

export default function AlgorithmSidebar({
  selectedAlgorithmId,
  onSelectAlgorithm,
}: AlgorithmSidebarProps) {
  const { data: algorithms, isLoading, error } = useAlgorithms();
  const [fetchingAlgorithmId, setFetchingAlgorithmId] = useState<string | null>(null);
  const { data: selectedMetadata } = useAlgorithmMetadata(fetchingAlgorithmId);

  // When metadata is loaded, pass it to parent
  useEffect(() => {
    if (selectedMetadata && selectedMetadata.id === fetchingAlgorithmId) {
      onSelectAlgorithm(selectedMetadata);
      setFetchingAlgorithmId(null);
    }
  }, [selectedMetadata, fetchingAlgorithmId, onSelectAlgorithm]);

  const handleSelectAlgorithm = (algorithmId: string) => {
    setFetchingAlgorithmId(algorithmId);
  };

  return (
    <aside className="algorithm-sidebar">
      <div className="sidebar-header">
        <h2>Algorithms</h2>
      </div>

      <div className="sidebar-content">
        {isLoading && (
          <div className="sidebar-loading">
            <p>Loading algorithms...</p>
          </div>
        )}

        {error && (
          <div className="sidebar-error">
            <p>Failed to load algorithms</p>
          </div>
        )}

        {algorithms && algorithms.length === 0 && (
          <div className="sidebar-empty">
            <p>No algorithms available</p>
          </div>
        )}

        {algorithms && algorithms.map((algorithm) => (
          <AlgorithmCard
            key={algorithm.id}
            algorithm={algorithm}
            isSelected={algorithm.id === selectedAlgorithmId}
            onSelect={() => handleSelectAlgorithm(algorithm.id)}
          />
        ))}
      </div>
    </aside>
  );
}
