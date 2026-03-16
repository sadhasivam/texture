import type { ColumnSchema } from '../../types/dataset';
import './TargetSelector.css';

interface TargetSelectorProps {
  columns: ColumnSchema[];
  selectedColumn: string;
  onSelect: (column: string) => void;
  allowedTypes: string[];
}

export default function TargetSelector({
  columns,
  selectedColumn,
  onSelect,
  allowedTypes,
}: TargetSelectorProps) {
  const validColumns = columns.filter((col) =>
    allowedTypes.includes(col.inferred_type)
  );

  // Debug logging
  console.log('TargetSelector - Allowed types:', allowedTypes);
  console.log('TargetSelector - All columns:', columns.map(c => `${c.name}(${c.inferred_type})`));
  console.log('TargetSelector - Valid columns:', validColumns.map(c => `${c.name}(${c.inferred_type})`));

  return (
    <div className="selector-group">
      <label className="selector-label">
        Target Column
        <span className="required">*</span>
      </label>
      <select
        className="selector-input"
        value={selectedColumn}
        onChange={(e) => onSelect(e.target.value)}
      >
        <option value="">Select target column...</option>
        {validColumns.map((col) => (
          <option key={col.name} value={col.name}>
            {col.name} ({col.inferred_type})
          </option>
        ))}
      </select>
      <p className="selector-hint">
        Allowed types: {allowedTypes.join(', ')}
        {validColumns.length === 0 && (
          <span style={{ color: 'red', display: 'block', marginTop: '4px' }}>
            ⚠ No columns match the allowed types
          </span>
        )}
      </p>
    </div>
  );
}
