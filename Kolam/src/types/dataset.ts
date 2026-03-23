export interface ColumnSchema {
  name: string;
  inferred_type: string;
  missing_count: number;
  unique_count: number;
  sample_values: (string | number)[];
}

export interface DatasetUploadResponse {
  id: string;
  filename: string;
  row_count: number;
  column_count: number;
  columns: ColumnSchema[];
  preview_rows: Record<string, string | number | null>[];
}

export interface DatasetDetails {
  id: string;
  filename: string;
  row_count: number;
  column_count: number;
  columns: ColumnSchema[];
  preview_rows: Record<string, string | number | null>[];
}
