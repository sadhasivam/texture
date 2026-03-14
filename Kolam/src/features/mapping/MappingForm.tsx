import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '../../services/api';
import TargetSelector from './TargetSelector';
import FeatureSelector from './FeatureSelector';
import ParameterForm from './ParameterForm';
import type { AlgorithmMetadata } from '../../types/algorithm';
import type { DatasetUploadResponse } from '../../types/dataset';
import type { RunResponse } from '../../types/run';
import './MappingForm.css';

interface MappingFormProps {
  algorithm: AlgorithmMetadata;
  dataset: DatasetUploadResponse;
  onRunComplete: (result: RunResponse) => void;
}

export default function MappingForm({
  algorithm,
  dataset,
  onRunComplete,
}: MappingFormProps) {
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [featureColumns, setFeatureColumns] = useState<string[]>([]);
  const [parameters, setParameters] = useState<Record<string, any>>(() => {
    const defaults: Record<string, any> = {};
    algorithm.parameters.forEach((param) => {
      defaults[param.name] = param.default;
    });
    return defaults;
  });

  const runMutation = useMutation({
    mutationFn: api.createRun,
    onSuccess: (result) => {
      onRunComplete(result);
    },
    onError: (error) => {
      console.error('Run failed:', error);
    },
  });

  const handleTargetChange = (column: string) => {
    setTargetColumn(column);
    // Remove the new target from features if it was selected
    if (featureColumns.includes(column)) {
      setFeatureColumns(featureColumns.filter(c => c !== column));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!targetColumn) {
      alert('Please select a target column');
      return;
    }

    if (featureColumns.length === 0) {
      alert('Please select at least one feature column');
      return;
    }

    runMutation.mutate({
      algorithm_id: algorithm.id,
      dataset_id: dataset.dataset_id,
      target_column: targetColumn,
      feature_columns: featureColumns,
      parameters,
    });
  };

  return (
    <form className="mapping-form" onSubmit={handleSubmit}>
      <h3>Configure Run</h3>

      <TargetSelector
        columns={dataset.columns}
        selectedColumn={targetColumn}
        onSelect={handleTargetChange}
        allowedTypes={algorithm.target.allowed_types}
      />

      <FeatureSelector
        columns={dataset.columns}
        selectedColumns={featureColumns}
        onSelect={setFeatureColumns}
        allowedTypes={algorithm.features.allowed_types}
        targetColumn={targetColumn}
      />

      {algorithm.parameters.length > 0 && (
        <ParameterForm
          parameters={algorithm.parameters}
          values={parameters}
          onChange={setParameters}
        />
      )}

      <div className="form-actions">
        <button
          type="submit"
          className="run-button"
          disabled={runMutation.isPending || !targetColumn || featureColumns.length === 0}
        >
          {runMutation.isPending ? 'Running...' : 'Run Algorithm'}
        </button>
      </div>

      {runMutation.isError && (
        <div className="run-error">
          <p>Failed to run algorithm.</p>
          {runMutation.error && (
            <p style={{ marginTop: '8px', fontSize: '12px' }}>
              {runMutation.error instanceof Error ? runMutation.error.message : 'Unknown error'}
            </p>
          )}
        </div>
      )}
    </form>
  );
}
