import type { ColumnSchema } from '../../types/dataset';
import './FeatureSelector.css';

interface FeatureSelectorProps {
  columns: ColumnSchema[];
  selectedColumns: string[];
  onSelect: (columns: string[]) => void;
  allowedTypes: string[];
  targetColumn: string;
}

export default function FeatureSelector({
  columns,
  selectedColumns,
  onSelect,
  allowedTypes,
  targetColumn,
}: FeatureSelectorProps) {
  const validColumns = columns.filter(
    (col) => allowedTypes.includes(col.inferred_type) && col.name !== targetColumn
  );

  // Debug logging
  console.log('FeatureSelector - Allowed types:', allowedTypes);
  console.log('FeatureSelector - Target column:', targetColumn);
  console.log('FeatureSelector - All columns:', columns.map(c => `${c.name}(${c.inferred_type})`));
  console.log('FeatureSelector - Valid columns:', validColumns.map(c => `${c.name}(${c.inferred_type})`));

  const handleToggle = (columnName: string) => {
    if (selectedColumns.includes(columnName)) {
      onSelect(selectedColumns.filter((c) => c !== columnName));
    } else {
      onSelect([...selectedColumns, columnName]);
    }
  };

  return (
    <div className="selector-group">
      <label className="selector-label">
        Feature Columns
        <span className="required">*</span>
      </label>
      <div className="feature-list">
        {validColumns.length === 0 && (
          <p className="no-features">
            No valid feature columns available
            <br />
            <small style={{ color: '#666' }}>
              Looking for: {allowedTypes.join(', ')}
              {targetColumn && ` (excluding target: ${targetColumn})`}
            </small>
          </p>
        )}
        {validColumns.map((col) => (
          <label key={col.name} className="feature-checkbox-label">
            <input
              type="checkbox"
              checked={selectedColumns.includes(col.name)}
              onChange={() => handleToggle(col.name)}
              className="feature-checkbox"
            />
            <span className="feature-name">{col.name}</span>
            <span className="feature-type">({col.inferred_type})</span>
          </label>
        ))}
      </div>
      <p className="selector-hint">
        Allowed types: {allowedTypes.join(', ')}
      </p>
    </div>
  );
}
