"""Spec-driven One-Class SVM - minimal boilerplate."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from app.ml.spec_adapter import SpecDrivenAdapter


class OneClassSVMAdapter(SpecDrivenAdapter):
    """One-Class SVM using YAML spec for metadata."""

    spec_path = "anomaly_detection/one-class-svm.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        nu = float(parameters.get("nu", 0.1))
        kernel = str(parameters.get("kernel", "rbf"))
        gamma_param = parameters.get("gamma", "auto")

        # Ensure valid parameters
        nu = max(0.0, min(1.0, nu))
        valid_kernels = ["rbf", "linear", "poly", "sigmoid"]
        if kernel not in valid_kernels:
            kernel = "rbf"

        # Handle gamma parameter
        if gamma_param == "auto" or gamma_param == "scale":
            gamma = gamma_param
        else:
            try:
                gamma = float(gamma_param)
            except (ValueError, TypeError):
                gamma = "auto"

        # Prepare data
        X = dataframe[features].copy()

        # Drop rows with missing values
        X = X.dropna()

        # Scale features (SVM is sensitive to feature scaling)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train One-Class SVM
        model = OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)
        predictions = model.fit_predict(X_scaled)

        # Get decision scores (distance from separating hyperplane)
        decision_scores = model.decision_function(X_scaled)

        # Count anomalies (predictions: 1 = normal, -1 = anomaly)
        n_anomalies = int((predictions == -1).sum())
        anomaly_percentage = float(n_anomalies / len(predictions) * 100)

        # Support vectors info
        n_support_vectors = len(model.support_vectors_)
        support_vector_percentage = float(n_support_vectors / len(predictions) * 100)

        # Metrics
        metrics = {
            "n_anomalies": n_anomalies,
            "anomaly_percentage": anomaly_percentage,
            "n_support_vectors": n_support_vectors,
            "support_vector_percentage": support_vector_percentage,
        }

        # Decision boundary scatter (use first 2 features)
        scatter_data = []
        for idx, row in X.iterrows():
            loc = X.index.get_loc(idx)
            is_support_vector = loc in model.support_
            scatter_data.append(
                {
                    "feature1": float(row[features[0]]),
                    "feature2": float(
                        row[features[1]] if len(features) > 1 else decision_scores[loc]
                    ),
                    "decision_score": float(decision_scores[loc]),
                    "is_anomaly": bool(predictions[loc] == -1),
                    "is_support_vector": bool(is_support_vector),
                }
            )

        # Decision score distribution histogram
        n_bins = min(30, len(decision_scores) // 10) if len(decision_scores) > 30 else 10
        hist, bin_edges = np.histogram(decision_scores, bins=n_bins)
        score_distribution_data = []
        for i in range(len(hist)):
            bin_center = (bin_edges[i] + bin_edges[i + 1]) / 2
            # Check if this bin contains anomalies
            bin_mask = (decision_scores >= bin_edges[i]) & (decision_scores < bin_edges[i + 1])
            anomalies_in_bin = int((predictions[bin_mask] == -1).sum())
            score_distribution_data.append(
                {
                    "score": float(bin_center),
                    "count": int(hist[i]),
                    "anomaly_count": anomalies_in_bin,
                    "normal_count": int(hist[i]) - anomalies_in_bin,
                    "bin_start": float(bin_edges[i]),
                    "bin_end": float(bin_edges[i + 1]),
                }
            )

        charts = [
            {
                "type": "decision_boundary",
                "title": "One-Class SVM Decision Boundary",
                "data": scatter_data,
            },
            {
                "type": "decision_scores",
                "title": "Decision Score Distribution",
                "data": score_distribution_data,
            },
        ]

        # Top anomalies by decision score (most negative)
        anomaly_indices = np.where(predictions == -1)[0]
        sorted_anomaly_indices = sorted(
            anomaly_indices, key=lambda i: decision_scores[i]
        )[:10]

        top_anomalies = []
        for i in sorted_anomaly_indices:
            anomaly_entry = {
                "index": int(X.index[i]),
                "decision_score": float(decision_scores[i]),
            }
            # Add feature values (limit to first 5 features)
            for feature in features[:5]:
                anomaly_entry[feature] = float(X.iloc[i][feature])
            top_anomalies.append(anomaly_entry)

        tables = [
            {
                "type": "top_anomalies",
                "rows": top_anomalies,
            }
        ]

        # Explanations
        explanations = [
            f"One-Class SVM detected {n_anomalies} anomalies ({anomaly_percentage:.1f}% of data).",
            f"Used {n_support_vectors} support vectors ({support_vector_percentage:.1f}% of data).",
            f"Kernel: {kernel}, Nu: {nu:.2f}.",
            "One-Class SVM learns a decision boundary around normal data points.",
            "Negative decision scores indicate anomalies (outside the boundary).",
        ]

        if kernel == "rbf":
            explanations.append(
                "RBF kernel creates a smooth, non-linear decision boundary."
            )
        elif kernel == "linear":
            explanations.append("Linear kernel creates a linear decision boundary.")

        # Warnings
        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(f"Dropped {dropped} rows with missing values before training.")

        if n_anomalies == 0:
            warnings.append("No anomalies detected. Consider increasing nu parameter.")

        if support_vector_percentage > 50:
            warnings.append(
                f"{support_vector_percentage:.1f}% of data are support vectors. "
                "Consider adjusting nu or kernel parameters."
            )

        if len(X) < 100:
            warnings.append(
                f"Small sample size ({len(X)} points). "
                "SVM works best with larger datasets."
            )

        # Feature scaling note
        if len(features) > 1:
            explanations.append("Features were automatically scaled (StandardScaler) before training.")

        return {
            "summary": {
                "feature_columns": features,
                "total_samples": len(X),
                "n_anomalies": n_anomalies,
                "kernel": kernel,
                "nu": nu,
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
