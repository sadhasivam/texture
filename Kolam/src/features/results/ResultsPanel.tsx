import MetricsCards from './MetricsCards';
import ChartRenderer from './ChartRenderer';
import ExplanationPanel from './ExplanationPanel';
import WarningsPanel from './WarningsPanel';
import type { RunResponse } from '../../types/run';
import './ResultsPanel.css';

interface ResultsPanelProps {
  result: RunResponse;
}

export default function ResultsPanel({ result }: ResultsPanelProps) {
  const hasSplitData = result.summary?.train_rows != null && result.summary?.test_rows != null;

  return (
    <div className="results-panel">
      <div className="results-header">
        <h2>Results</h2>
        {hasSplitData && result.summary && (
          <div className="results-summary">
            <span className="summary-item">
              <strong>{result.summary.train_rows}</strong> training rows
            </span>
            <span className="summary-separator">·</span>
            <span className="summary-item">
              <strong>{result.summary.test_rows}</strong> test rows
            </span>
          </div>
        )}
      </div>

      {result.warnings && result.warnings.length > 0 && <WarningsPanel warnings={result.warnings} />}

      {result.metrics && <MetricsCards metrics={result.metrics} />}

      {result.charts && result.charts.length > 0 && (
        <div className="charts-section">
          <h3>Visualizations</h3>
          <div className="charts-grid">
            {result.charts.map((chart, idx) => (
              <ChartRenderer key={idx} chart={chart} />
            ))}
          </div>
        </div>
      )}

      {result.explanations && result.explanations.length > 0 && (
        <ExplanationPanel explanations={result.explanations} />
      )}

      {result.tables && result.tables.length > 0 && (
        <div className="tables-section">
          <h3>Details</h3>
          {result.tables.map((table, idx) => (
            <div key={idx} className="result-table-container">
              <h4>{table.type.replace(/_/g, ' ')}</h4>
              <table className="result-table">
                <thead>
                  <tr>
                    {table.rows.length > 0 &&
                      Object.keys(table.rows[0]).map((key) => (
                        <th key={key}>{key}</th>
                      ))}
                  </tr>
                </thead>
                <tbody>
                  {table.rows.map((row, rowIdx) => (
                    <tr key={rowIdx}>
                      {Object.values(row).map((val, cellIdx) => (
                        <td key={cellIdx}>
                          {typeof val === 'number' ? val.toFixed(4) : String(val)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
