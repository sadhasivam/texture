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
  Line,
  LineChart,
  Legend,
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
        // Add index to each data point for x-axis
        const indexedData = chart.data.map((d: any, idx: number) => ({
          index: idx,
          actual: d.actual,
          predicted: d.predicted,
          best_fit: d.best_fit,
        }));

        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={indexedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="index"
                label={{ value: 'Sample', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="Actual"
              />
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="#f97316"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Predicted"
              />
              <Line
                type="monotone"
                dataKey="best_fit"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                name="Best Fit Line"
              />
            </LineChart>
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

      case 'anomaly_scatter':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="x"
                name="X"
                label={{ value: 'Feature 1', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Y"
                label={{ value: 'Feature 2 / Score', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter
                name="Normal"
                data={chart.data.filter((d: any) => !d.is_anomaly)}
                fill="#10b981"
              />
              <Scatter
                name="Anomaly"
                data={chart.data.filter((d: any) => d.is_anomaly)}
                fill="#ef4444"
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'anomaly_score_distribution':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="score"
                name="Score"
                label={{ value: 'Anomaly Score', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                domain={[0, 1]}
                label={{ value: 'Is Anomaly', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter
                name="Normal"
                data={chart.data.filter((d: any) => !d.is_anomaly)}
                fill="#10b981"
              />
              <Scatter
                name="Anomaly"
                data={chart.data.filter((d: any) => d.is_anomaly)}
                fill="#ef4444"
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'cluster_scatter':
        const clusterColors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];
        const hasNoise = chart.data.some((d: any) => d.is_noise);
        const clusters = Array.from(new Set(chart.data.map((d: any) => d.cluster))).sort();

        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="x"
                name="X"
                label={{ value: 'Feature 1', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Y"
                label={{ value: 'Feature 2', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              {clusters.map((cluster: any) => {
                if (cluster === -1 && hasNoise) {
                  return (
                    <Scatter
                      key={cluster}
                      name="Noise"
                      data={chart.data.filter((d: any) => d.cluster === cluster)}
                      fill="#6b7280"
                    />
                  );
                }
                return (
                  <Scatter
                    key={cluster}
                    name={`Cluster ${cluster}`}
                    data={chart.data.filter((d: any) => d.cluster === cluster)}
                    fill={clusterColors[cluster % clusterColors.length]}
                  />
                );
              })}
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'pca_scatter':
      case 'tsne_scatter':
        const xKey = chart.type === 'pca_scatter' ? 'PC1' : 'x';
        const yKey = chart.type === 'pca_scatter' ? 'PC2' : 'y';
        const hasTarget = chart.data.some((d: any) => d.target !== undefined);

        if (hasTarget) {
          const targetGroups = Array.from(new Set(chart.data.map((d: any) => d.target)));
          const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
          return (
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  dataKey={xKey}
                  name={xKey}
                  label={{ value: xKey, position: 'insideBottom', offset: -10 }}
                />
                <YAxis
                  type="number"
                  dataKey={yKey}
                  name={yKey}
                  label={{ value: yKey, angle: -90, position: 'insideLeft' }}
                />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                {targetGroups.map((target: any, idx) => (
                  <Scatter
                    key={target}
                    name={String(target)}
                    data={chart.data.filter((d: any) => d.target === target)}
                    fill={colors[idx % colors.length]}
                  />
                ))}
              </ScatterChart>
            </ResponsiveContainer>
          );
        }

        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey={xKey}
                name={xKey}
                label={{ value: xKey, position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey={yKey}
                name={yKey}
                label={{ value: yKey, angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={chart.data} fill="#3b82f6" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'variance_explained':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={chart.data}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="component" />
              <YAxis label={{ value: 'Variance (%)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="variance" fill="#3b82f6" name="Individual" />
              <Bar dataKey="cumulative" fill="#10b981" name="Cumulative" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'time_series_plot':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chart.data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="index"
                label={{ value: 'Time Index', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                dataKey="value"
                label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.is_anomaly) {
                    return <circle cx={cx} cy={cy} r={4} fill="#ef4444" />;
                  }
                  return null;
                }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'matrix_profile_plot':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chart.data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="index"
                label={{ value: 'Window Index', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                label={{ value: 'Distance', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="distance"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="Matrix Profile"
              />
              <Line
                type="monotone"
                dataKey="threshold_line"
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Threshold"
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'anomaly_windows':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="window_start"
                name="Window Start"
                label={{ value: 'Window Start Index', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="distance"
                name="Distance"
                label={{ value: 'Matrix Profile Distance', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={chart.data} fill="#ef4444" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'distance_scatter':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="feature1"
                name="Feature 1"
                label={{ value: 'Feature 1', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="feature2"
                name="Feature 2"
                label={{ value: 'Feature 2 / Distance', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter
                name="Normal"
                data={chart.data.filter((d: any) => !d.is_anomaly)}
                fill="#10b981"
              />
              <Scatter
                name="Anomaly"
                data={chart.data.filter((d: any) => d.is_anomaly)}
                fill="#ef4444"
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'distance_distribution':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={chart.data}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="distance"
                label={{ value: 'Mahalanobis Distance', position: 'insideBottom', offset: -10 }}
              />
              <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="normal_count" stackId="a" fill="#10b981" name="Normal" />
              <Bar dataKey="anomaly_count" stackId="a" fill="#ef4444" name="Anomaly" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'decision_boundary':
        const normalPoints = chart.data.filter((d: any) => !d.is_anomaly && !d.is_support_vector);
        const supportVectors = chart.data.filter((d: any) => d.is_support_vector);
        const anomalyPoints = chart.data.filter((d: any) => d.is_anomaly);

        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="feature1"
                name="Feature 1"
                label={{ value: 'Feature 1', position: 'insideBottom', offset: -10 }}
              />
              <YAxis
                type="number"
                dataKey="feature2"
                name="Feature 2"
                label={{ value: 'Feature 2 / Decision Score', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter
                name="Normal"
                data={normalPoints}
                fill="#10b981"
              />
              <Scatter
                name="Support Vectors"
                data={supportVectors}
                fill="#3b82f6"
                shape="triangle"
              />
              <Scatter
                name="Anomaly"
                data={anomalyPoints}
                fill="#ef4444"
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'decision_scores':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={chart.data}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="score"
                label={{ value: 'Decision Score', position: 'insideBottom', offset: -10 }}
              />
              <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="normal_count" stackId="a" fill="#10b981" name="Normal" />
              <Bar dataKey="anomaly_count" stackId="a" fill="#ef4444" name="Anomaly" />
            </BarChart>
          </ResponsiveContainer>
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
