import './WarningsPanel.css';

interface WarningsPanelProps {
  warnings: string[];
}

export default function WarningsPanel({ warnings }: WarningsPanelProps) {
  return (
    <div className="warnings-panel">
      <h4>Warnings</h4>
      <ul className="warnings-list">
        {warnings.map((warning, idx) => (
          <li key={idx} className="warning-item">
            {warning}
          </li>
        ))}
      </ul>
    </div>
  );
}
