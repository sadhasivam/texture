import type { AlgorithmSummary } from '../../types/algorithm';
import './AlgorithmCard.css';

interface AlgorithmCardProps {
  algorithm: AlgorithmSummary;
  isSelected: boolean;
  onSelect: () => void;
}

export default function AlgorithmCard({
  algorithm,
  isSelected,
  onSelect,
}: AlgorithmCardProps) {
  return (
    <button
      className={`algorithm-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      type="button"
    >
      <div className="algorithm-card-header">
        <h3>{algorithm.name}</h3>
        <span className="algorithm-category">{algorithm.category}</span>
      </div>
      <p className="algorithm-description">{algorithm.description}</p>
    </button>
  );
}
