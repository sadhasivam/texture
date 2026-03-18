export interface AlgorithmParameter {
  name: string;
  type: string;
  default: number | string | boolean;
  label: string;
  options?: string[];
}

export interface AlgorithmTarget {
  required: boolean;
  allowed_types: string[];
  cardinality: string;
}

export interface AlgorithmFeatures {
  required: boolean;
  min_columns: number;
  max_columns: number | null;
  allowed_types: string[];
}

export interface AlgorithmOutputs {
  metrics: string[];
  charts: string[];
  tables: string[];
}

export interface AlgorithmMetadata {
  id: string;
  name: string;
  category: string;
  group: string;
  subgroup: string;
  description: string;
  tags: string[];
  difficulty: string;
  model_family: string;
  target: AlgorithmTarget;
  features: AlgorithmFeatures;
  parameters: AlgorithmParameter[];
  outputs: AlgorithmOutputs;
  validation_rules: string[];
}

export interface AlgorithmSummary {
  id: string;
  name: string;
  category: string;
  group: string;
  subgroup: string;
  description: string;
  tags: string[];
  difficulty: string;
  model_family: string;
}
