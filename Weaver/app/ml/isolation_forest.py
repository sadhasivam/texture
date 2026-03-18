"""Isolation Forest algorithm adapter."""

import pandas as pd
from sklearn.ensemble import IsolationForest as SklearnIsolationForest

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class IsolationForestAdapter(AlgorithmAdapter):
    id = "isolation_forest"
    name = "Isolation Forest"
    category = "anomaly_detection"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            group="anomaly_detection",
            subgroup="anomaly_detection",
            description="Detects anomalies by isolating observations through random partitioning.",
            target=AlgorithmTarget(
                required=False,
                allowed_types=[],
                cardinality="single",
            ),
            features=AlgorithmFeatures(
                required=True,
                min_columns=1,
                max_columns=None,
                allowed_types=["numeric"],
            ),
            parameters=[
                AlgorithmParameter(
                    name="contamination",
                    type="float",
                    default=0.1,
                    label="Expected proportion of anomalies",
                ),
                AlgorithmParameter(
                    name="n_estimators",
                    type="int",
                    default=100,
                    label="Number of trees",
                ),
                AlgorithmParameter(
                    name="max_samples",
                    type="int",
                    default=256,
                    label="Samples per tree",
                ),
            ],
            outputs=AlgorithmOutputs(
                metrics=["n_anomalies", "anomaly_percentage"],
                charts=["anomaly_scatter", "anomaly_score_distribution"],
                tables=["anomaly_summary"],
            ),
            validation_rules=[
                "At least 1 feature column required",
                "All features must be numeric",
                "Contamination must be between 0 and 0.5",
            ],
        )

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        contamination = parameters.get("contamination", 0.1)
        n_estimators = parameters.get("n_estimators", 100)
        max_samples = parameters.get("max_samples", 256)

        # Ensure contamination is valid
        contamination = max(0.0, min(0.5, contamination))

        # Prepare data
        X = dataframe[features]

        # Drop rows with missing values
        X = X.dropna()

        # Adjust max_samples if needed
        if max_samples > len(X):
            max_samples = len(X)

        # Train Isolation Forest
        model = SklearnIsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=42,
        )

        # Predict: -1 for anomalies, 1 for normal
        predictions = model.fit_predict(X)

        # Get anomaly scores (lower = more anomalous)
        anomaly_scores = model.score_samples(X)

        # Count anomalies
        n_anomalies = int((predictions == -1).sum())
        anomaly_percentage = float(n_anomalies / len(predictions) * 100)

        metrics = {
            "n_anomalies": n_anomalies,
            "anomaly_percentage": anomaly_percentage,
        }

        # Anomaly scatter plot (use first 2 features)
        scatter_data = []
        for idx, row in X.iterrows():
            loc = X.index.get_loc(idx)
            scatter_data.append({
                "x": float(row[features[0]]),
                "y": float(
                    row[features[1]]
                    if len(features) > 1
                    else anomaly_scores[loc]
                ),
                "is_anomaly": bool(predictions[loc] == -1),
                "anomaly_score": float(anomaly_scores[loc]),
            })

        # Anomaly score distribution
        score_distribution = [
            {
                "score": float(score),
                "is_anomaly": bool(pred == -1),
            }
            for score, pred in zip(anomaly_scores, predictions)
        ]

        charts = [
            {
                "type": "anomaly_scatter",
                "title": "Anomaly Detection",
                "data": scatter_data,
            },
            {
                "type": "anomaly_score_distribution",
                "title": "Anomaly Score Distribution",
                "data": score_distribution,
            },
        ]

        # Anomaly summary table
        # Get top anomalies by score
        anomaly_indices = [i for i, p in enumerate(predictions) if p == -1]
        anomaly_data = [
            {
                "index": int(X.index[i]),
                "score": float(anomaly_scores[i]),
                **{
                    feature: float(X.iloc[i][feature])
                    for feature in features[:5]  # Limit to first 5 features
                },
            }
            for i in sorted(anomaly_indices, key=lambda i: anomaly_scores[i])[:10]
        ]

        tables = [
            {
                "type": "anomaly_summary",
                "rows": anomaly_data,
            }
        ]

        explanations = [
            f"Isolation Forest detected {n_anomalies} anomalies ({anomaly_percentage:.1f}% of data).",
            f"Expected contamination: {contamination*100:.1f}%.",
            "Anomalies are observations that are easily isolated (require fewer splits).",
            f"Used {n_estimators} trees for robust anomaly detection.",
        ]

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(
                f"Dropped {dropped} rows with missing values before detection."
            )

        if n_anomalies == 0:
            warnings.append(
                "No anomalies detected. Consider increasing contamination parameter."
            )

        if anomaly_percentage > contamination * 100 * 1.5:
            warnings.append(
                f"Detected {anomaly_percentage:.1f}% anomalies, "
                f"but expected {contamination*100:.1f}%. "
                "This may indicate the contamination parameter is too low."
            )

        return {
            "summary": {
                "feature_columns": features,
                "total_samples": len(X),
                "n_anomalies": n_anomalies,
                "contamination": contamination,
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
