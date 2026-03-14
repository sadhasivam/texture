import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import type { ChartData } from '../../types/run';
import './ChartRenderer.css';

interface ChartRendererProps {
  chart: ChartData;
}

export default function ChartRenderer({ chart }: ChartRendererProps) {
  const renderChart = () => {
    switch (chart.type) {
      case 'predicted_vs_actual':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="actual"
                name="Actual"
                label={{ value: 'Actual', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="predicted"
                name="Predicted"
                label={{ value: 'Predicted', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={chart.data} fill="#3b82f6" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'residual_plot':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="predicted"
                name="Predicted"
                label={{ value: 'Predicted', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="residual"
                name="Residual"
                label={{ value: 'Residual', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={chart.data} fill="#8b5cf6" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'feature_importance':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={chart.data}
              margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="feature"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis label={{ value: 'Importance', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="importance" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'class_distribution':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chart.data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="class" />
              <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="count" fill="#f59e0b">
                {chart.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={`hsl(${index * 50}, 70%, 60%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case 'confusion_matrix':
        return (
          <div className="confusion-matrix">
            <p className="chart-note">Confusion matrix visualization (simplified)</p>
            <div className="matrix-grid">
              {chart.data.map((item: any, idx) => (
                <div key={idx} className="matrix-cell">
                  <div className="matrix-labels">
                    True: {item.true} / Pred: {item.predicted}
                  </div>
                  <div className="matrix-count">{item.count}</div>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return (
          <div className="chart-fallback">
            <p>Unsupported chart type: {chart.type}</p>
          </div>
        );
    }
  };

  return (
    <div className="chart-container">
      <h4 className="chart-title">{chart.title}</h4>
      <div className="chart-content">{renderChart()}</div>
    </div>
  );
}
