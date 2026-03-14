import './ExplanationPanel.css';

interface ExplanationPanelProps {
  explanations: string[];
}

export default function ExplanationPanel({ explanations }: ExplanationPanelProps) {
  return (
    <div className="explanation-panel">
      <h3>Explanations</h3>
      <ul className="explanation-list">
        {explanations.map((explanation, idx) => (
          <li key={idx} className="explanation-item">
            {explanation}
          </li>
        ))}
      </ul>
    </div>
  );
}
