import type { AlgorithmParameter } from '../../types/algorithm';
import './ParameterForm.css';

interface ParameterFormProps {
  parameters: AlgorithmParameter[];
  values: Record<string, any>;
  onChange: (values: Record<string, any>) => void;
}

export default function ParameterForm({
  parameters,
  values,
  onChange,
}: ParameterFormProps) {
  const handleChange = (name: string, value: any) => {
    onChange({ ...values, [name]: value });
  };

  return (
    <div className="parameter-form">
      <h4>Parameters</h4>
      {parameters.map((param) => (
        <div key={param.name} className="parameter-field">
          <label className="parameter-label">{param.label}</label>
          {param.type === 'select' && param.options ? (
            <select
              value={String(values[param.name] ?? param.default)}
              onChange={(e) => handleChange(param.name, e.target.value)}
              className="parameter-input"
            >
              {param.options.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          ) : (
            <input
              type={param.type === 'float' || param.type === 'int' ? 'number' : 'text'}
              value={values[param.name] ?? param.default}
              onChange={(e) => {
                const val =
                  param.type === 'float'
                    ? parseFloat(e.target.value)
                    : param.type === 'int'
                    ? parseInt(e.target.value, 10)
                    : e.target.value;
                handleChange(param.name, val);
              }}
              step={param.type === 'float' ? '0.01' : undefined}
              className="parameter-input"
            />
          )}
          <p className="parameter-hint">Default: {String(param.default)}</p>
        </div>
      ))}
    </div>
  );
}
