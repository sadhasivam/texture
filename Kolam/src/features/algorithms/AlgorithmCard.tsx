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
  const difficultyClass = `difficulty-badge difficulty-${algorithm.difficulty}`;
  const displayTags = algorithm.tags.slice(0, 3);

  return (
    <button
      className={`algorithm-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      type="button"
    >
      <div className="algorithm-card-header">
        <h3>{algorithm.name}</h3>
        <span className={difficultyClass}>{algorithm.difficulty}</span>
      </div>
      <p className="algorithm-description">{algorithm.description}</p>
      {displayTags.length > 0 && (
        <div className="algorithm-tags">
          {displayTags.map((tag) => (
            <span key={tag} className="algorithm-tag">
              {tag}
            </span>
          ))}
        </div>
      )}
    </button>
  );
}
