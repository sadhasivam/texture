"""Spec-driven Matrix Profile - minimal boilerplate."""

import numpy as np
import pandas as pd

try:
    import stumpy
    STUMPY_AVAILABLE = True
except ImportError:
    STUMPY_AVAILABLE = False

from app.ml.spec_adapter import SpecDrivenAdapter


class MatrixProfileAdapter(SpecDrivenAdapter):
    """Matrix Profile using YAML spec for metadata."""

    spec_path = "anomaly_detection/matrix-profile.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        # Check if stumpy is available
        if not STUMPY_AVAILABLE:
            raise ImportError(
                "stumpy library is required for Matrix Profile. "
                "Install with: uv add stumpy"
            )

        window_size = int(parameters.get("window_size", 50))
        threshold_multiplier = float(parameters.get("threshold_multiplier", 3.0))

        # Ensure valid parameters
        window_size = max(4, window_size)  # Minimum window size
        threshold_multiplier = max(0.0, threshold_multiplier)

        # Get time series (single feature)
        feature = features[0]
        time_series = dataframe[feature].dropna().values

        # Validate window size
        if window_size >= len(time_series) / 2:
            window_size = max(4, len(time_series) // 4)
            warnings = [
                f"Window size too large for time series length. "
                f"Reduced to {window_size}."
            ]
        else:
            warnings = []

        # Compute Matrix Profile using STUMPY
        # Matrix Profile: minimum distance to nearest neighbor for each subsequence
        # Index Profile: index of nearest neighbor
        mp = stumpy.stump(time_series, m=window_size)
        matrix_profile = mp[:, 0]  # Distance profile
        index_profile = mp[:, 1].astype(int)  # Nearest neighbor indices

        # Calculate statistics
        mean_distance = float(np.mean(matrix_profile))
        std_distance = float(np.std(matrix_profile))
        max_distance = float(np.max(matrix_profile))

        # Threshold for anomalies (mean + k * std)
        threshold = mean_distance + (threshold_multiplier * std_distance)

        # Identify anomalies
        anomaly_mask = matrix_profile > threshold
        n_anomalies = int(np.sum(anomaly_mask))
        anomaly_percentage = float(n_anomalies / len(matrix_profile) * 100)

        # Metrics
        metrics = {
            "n_anomalies": n_anomalies,
            "anomaly_percentage": anomaly_percentage,
            "max_distance": max_distance,
            "mean_distance": mean_distance,
        }

        # Time series plot with anomalies highlighted
        time_series_data = []
        for i, value in enumerate(time_series):
            # Mark as anomaly if any window containing this index is anomalous
            is_anomaly = False
            for w in range(max(0, i - window_size + 1), min(len(matrix_profile), i + 1)):
                if anomaly_mask[w]:
                    is_anomaly = True
                    break

            time_series_data.append(
                {
                    "index": i,
                    "value": float(value),
                    "is_anomaly": bool(is_anomaly),
                }
            )

        # Matrix profile plot
        matrix_profile_data = []
        for i, distance in enumerate(matrix_profile):
            matrix_profile_data.append(
                {
                    "index": i,
                    "distance": float(distance),
                    "threshold_line": float(threshold),
                    "is_anomaly": bool(anomaly_mask[i]),
                }
            )

        # Anomaly windows scatter
        anomaly_indices = np.where(anomaly_mask)[0]
        anomaly_windows_data = []
        for idx in anomaly_indices:
            anomaly_windows_data.append(
                {
                    "window_start": int(idx),
                    "window_end": int(idx + window_size),
                    "distance": float(matrix_profile[idx]),
                    "nearest_neighbor": int(index_profile[idx]),
                }
            )

        charts = [
            {
                "type": "time_series_plot",
                "title": "Time Series with Anomalies",
                "data": time_series_data,
            },
            {
                "type": "matrix_profile_plot",
                "title": "Matrix Profile",
                "data": matrix_profile_data,
            },
            {
                "type": "anomaly_windows",
                "title": "Anomalous Subsequences",
                "data": anomaly_windows_data,
            },
        ]

        # Top anomalies table (sorted by distance)
        top_anomaly_indices = anomaly_indices[
            np.argsort(matrix_profile[anomaly_indices])[::-1]
        ][:10]

        top_anomalies = []
        for idx in top_anomaly_indices:
            top_anomalies.append(
                {
                    "window_start": int(idx),
                    "window_end": int(idx + window_size),
                    "distance": float(matrix_profile[idx]),
                    "nearest_neighbor_index": int(index_profile[idx]),
                }
            )

        tables = [
            {
                "type": "top_anomalies",
                "rows": top_anomalies,
            }
        ]

        # Explanations
        explanations = [
            f"Matrix Profile detected {n_anomalies} anomalous subsequences "
            f"({anomaly_percentage:.1f}% of windows).",
            f"Window size: {window_size}, Threshold: {threshold:.2f}.",
            f"Mean distance: {mean_distance:.2f}, Max distance: {max_distance:.2f}.",
            "Matrix Profile measures z-normalized Euclidean distance between subsequences.",
            "High distances indicate subsequences that are dissimilar to all others.",
            "Anomalies are subsequences with distance > mean + "
            f"{threshold_multiplier:.1f} * std.",
        ]

        # Additional context
        if n_anomalies > 0:
            explanations.append(
                "Each anomaly represents a unique pattern not found elsewhere in the series."
            )

        # Warnings
        if len(time_series) < len(dataframe[feature]):
            dropped = len(dataframe[feature]) - len(time_series)
            warnings.append(f"Dropped {dropped} missing values from time series.")

        if n_anomalies == 0:
            warnings.append(
                "No anomalies detected. Consider lowering threshold_multiplier or "
                "adjusting window_size."
            )

        if len(time_series) < 100:
            warnings.append(
                f"Short time series ({len(time_series)} points). "
                "Matrix Profile works best with longer series."
            )

        if n_anomalies > len(matrix_profile) * 0.3:
            warnings.append(
                f"{anomaly_percentage:.1f}% of subsequences are anomalies. "
                "Consider increasing threshold_multiplier."
            )

        # Window size guidance
        if window_size < 10:
            warnings.append(
                f"Very small window size ({window_size}). "
                "Consider increasing for more meaningful patterns."
            )

        return {
            "summary": {
                "feature_column": feature,
                "series_length": len(time_series),
                "window_size": window_size,
                "n_anomalies": n_anomalies,
                "threshold": float(threshold),
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
