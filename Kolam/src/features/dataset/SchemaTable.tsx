import type { ColumnSchema } from '../../types/dataset';
import './SchemaTable.css';

interface SchemaTableProps {
  columns: ColumnSchema[];
}

export default function SchemaTable({ columns }: SchemaTableProps) {
  return (
    <div className="schema-table-container">
      <h4>Schema</h4>
      <table className="schema-table">
        <thead>
          <tr>
            <th>Column</th>
            <th>Type</th>
            <th>Missing</th>
            <th>Unique</th>
            <th>Samples</th>
          </tr>
        </thead>
        <tbody>
          {columns.map((column) => (
            <tr key={column.name}>
              <td className="column-name">{column.name}</td>
              <td>
                <span className={`type-badge type-${column.inferred_type}`}>
                  {column.inferred_type}
                </span>
              </td>
              <td className="column-stat">{column.missing_count}</td>
              <td className="column-stat">{column.unique_count}</td>
              <td className="column-samples">
                {column.sample_values.slice(0, 3).join(', ')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
