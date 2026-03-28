"""Spec-driven Z-Score Anomaly Detection - minimal boilerplate."""

import numpy as np
import pandas as pd

from app.ml.spec_adapter import SpecDrivenAdapter


class ZScoreAdapter(SpecDrivenAdapter):
    """Z-Score Anomaly Detection using YAML spec for metadata."""

    spec_path = "anomaly_detection/z-score.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        threshold = float(parameters.get("threshold", 3.0))

        # Ensure threshold is positive
        if threshold <= 0:
            threshold = 3.0

        # Get the single feature column
        feature_col = features[0]
        X = dataframe[[feature_col]].copy()

        # Drop rows with missing values
        X_clean = X.dropna()
        values = X_clean[feature_col].values

        # Calculate mean and standard deviation
        mean = float(np.mean(values))
        std_dev = float(np.std(values, ddof=1))  # Sample standard deviation

        # Handle edge case: all values are identical
        if std_dev == 0:
            std_dev = 1e-10  # Avoid division by zero

        # Calculate z-scores: z = (x - μ) / σ
        z_scores = (values - mean) / std_dev

        # Detect anomalies: |z| > threshold
        is_anomaly = np.abs(z_scores) > threshold

        # Count anomalies
        n_anomalies = int(np.sum(is_anomaly))
        anomaly_percentage = float(n_anomalies / len(values) * 100)

        # Metrics
        metrics = {
            "anomaly_count": n_anomalies,
            "anomaly_percentage": anomaly_percentage,
            "mean": mean,
            "std_dev": std_dev,
            "min_z_score": float(np.min(z_scores)),
            "max_z_score": float(np.max(z_scores)),
        }

        # Chart 1: Distribution with threshold bands
        # Create histogram bins
        hist, bin_edges = np.histogram(values, bins=30)
        distribution_data = []
        for i in range(len(hist)):
            bin_center = (bin_edges[i] + bin_edges[i + 1]) / 2
            z_score = (bin_center - mean) / std_dev
            distribution_data.append(
                {
                    "bin_center": float(bin_center),
                    "count": int(hist[i]),
                    "is_within_threshold": bool(abs(z_score) <= threshold),
                }
            )

        # Chart 2: Z-score plot
        z_score_data = []
        for idx, (value, z, anom) in enumerate(zip(values, z_scores, is_anomaly)):
            z_score_data.append(
                {
                    "index": int(X_clean.index[idx]),
                    "value": float(value),
                    "z_score": float(z),
                    "is_anomaly": bool(anom),
                }
            )

        # Chart 3: Anomaly scatter (index vs value)
        anomaly_scatter_data = []
        for idx, (value, z, anom) in enumerate(zip(values, z_scores, is_anomaly)):
            anomaly_scatter_data.append(
                {
                    "index": int(X_clean.index[idx]),
                    "value": float(value),
                    "z_score": float(z),
                    "is_anomaly": bool(anom),
                }
            )

        charts = [
            {
                "type": "distribution_with_threshold",
                "title": f"Distribution of {feature_col}",
                "data": distribution_data,
                "metadata": {
                    "mean": mean,
                    "std_dev": std_dev,
                    "threshold": threshold,
                },
            },
            {
                "type": "z_score_plot",
                "title": "Z-Score Values",
                "data": z_score_data,
                "metadata": {
                    "threshold": threshold,
                },
            },
            {
                "type": "anomaly_scatter",
                "title": "Detected Anomalies",
                "data": anomaly_scatter_data,
            },
        ]

        # Table: Top anomalies (sorted by absolute z-score)
        anomaly_indices = np.where(is_anomaly)[0]
        anomaly_table_data = []

        if len(anomaly_indices) > 0:
            # Sort by absolute z-score (most extreme first)
            sorted_indices = anomaly_indices[
                np.argsort(np.abs(z_scores[anomaly_indices]))[::-1]
            ]

            for idx in sorted_indices[:20]:  # Top 20 anomalies
                anomaly_table_data.append(
                    {
                        "original_index": int(X_clean.index[idx]),
                        "value": float(values[idx]),
                        "z_score": float(z_scores[idx]),
                        "deviation_from_mean": float(values[idx] - mean),
                        "std_devs_away": float(abs(z_scores[idx])),
                    }
                )

        tables = [
            {
                "type": "anomaly_details",
                "rows": anomaly_table_data,
            }
        ]

        # Explanations
        explanations = [
            f"Z-Score analysis detected {n_anomalies} anomalies ({anomaly_percentage:.1f}% of data).",
            f"Data distribution: mean = {mean:.2f}, standard deviation = {std_dev:.2f}.",
            f"Threshold: |z| > {threshold:.1f} (values more than {threshold:.1f} standard deviations from mean).",
        ]

        if n_anomalies > 0:
            max_z = float(np.max(np.abs(z_scores[is_anomaly])))
            explanations.append(
                f"Most extreme anomaly is {max_z:.1f} standard deviations from the mean."
            )
        else:
            explanations.append(
                "All data points fall within the threshold. Consider lowering the threshold if you expect outliers."
            )

        # Add interpretation
        if threshold == 3.0:
            explanations.append(
                "Using threshold of 3 (corresponds to ~99.7% of data in normal distribution)."
            )
        elif threshold == 2.0:
            explanations.append(
                "Using threshold of 2 (corresponds to ~95% of data in normal distribution)."
            )

        # Warnings
        warnings = []
        if len(X_clean) < len(dataframe):
            dropped = len(dataframe) - len(X_clean)
            warnings.append(f"Dropped {dropped} rows with missing values before analysis.")

        if n_anomalies == 0:
            warnings.append(
                f"No anomalies detected at threshold {threshold:.1f}. "
                "Consider lowering the threshold (e.g., 2.0) for stricter detection."
            )

        if anomaly_percentage > 20:
            warnings.append(
                f"{anomaly_percentage:.1f}% of data flagged as anomalies. "
                "This is unusually high - your data may not follow a normal distribution, "
                "or the threshold may be too strict."
            )

        if len(values) < 30:
            warnings.append(
                "Small sample size (< 30). Z-score is most reliable with larger datasets."
            )

        # Check for normality warning
        if std_dev < 1e-9:
            warnings.append("All values are nearly identical. Z-score may not be meaningful.")

        return {
            "summary": {
                "feature_column": feature_col,
                "total_samples": len(values),
                "n_anomalies": n_anomalies,
                "threshold": threshold,
                "mean": mean,
                "std_dev": std_dev,
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
