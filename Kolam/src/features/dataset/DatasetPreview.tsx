import SchemaTable from './SchemaTable';
import type { DatasetUploadResponse } from '../../types/dataset';
import './DatasetPreview.css';

interface DatasetPreviewProps {
  dataset: DatasetUploadResponse;
}

export default function DatasetPreview({ dataset }: DatasetPreviewProps) {
  return (
    <div className="dataset-preview">
      <div className="dataset-info">
        <h3>Dataset: {dataset.filename}</h3>
        <div className="dataset-stats">
          <span className="stat">
            <strong>{dataset.row_count.toLocaleString()}</strong> rows
          </span>
          <span className="stat-separator">·</span>
          <span className="stat">
            <strong>{dataset.column_count}</strong> columns
          </span>
        </div>
      </div>

      <SchemaTable columns={dataset.columns} />

      <div className="preview-rows">
        <h4>Preview</h4>
        <div className="preview-table-wrapper">
          <table className="preview-table">
            <thead>
              <tr>
                {dataset.columns.map((col) => (
                  <th key={col.name}>{col.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataset.preview_rows.slice(0, 5).map((row, idx) => (
                <tr key={idx}>
                  {dataset.columns.map((col) => (
                    <td key={col.name}>
                      {row[col.name] !== null && row[col.name] !== undefined
                        ? String(row[col.name])
                        : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
