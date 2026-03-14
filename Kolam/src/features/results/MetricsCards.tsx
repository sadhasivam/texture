import './MetricsCards.css';

interface MetricsCardsProps {
  metrics: Record<string, number>;
}

export default function MetricsCards({ metrics }: MetricsCardsProps) {
  return (
    <div className="metrics-section">
      <h3>Metrics</h3>
      <div className="metrics-grid">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="metric-card">
            <div className="metric-label">{key.toUpperCase()}</div>
            <div className="metric-value">{value.toFixed(4)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
