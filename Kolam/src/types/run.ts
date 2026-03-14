export interface RunRequest {
  algorithm_id: string;
  dataset_id: string;
  target_column: string;
  feature_columns: string[];
  parameters: Record<string, number | string | boolean>;
}

export interface RunSummary {
  target_column: string;
  feature_columns: string[];
  train_rows: number;
  test_rows: number;
}

export interface ChartData {
  type: string;
  title: string;
  data: Record<string, string | number>[];
}

export interface TableData {
  type: string;
  rows: Record<string, string | number>[];
}

export interface RunResponse {
  run_id: string;
  status: string;
  summary: RunSummary;
  metrics: Record<string, number>;
  charts: ChartData[];
  tables: TableData[];
  explanations: string[];
  warnings: string[];
}
