"""Spec-driven Mahalanobis Distance - minimal boilerplate."""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial.distance import mahalanobis

from app.ml.spec_adapter import SpecDrivenAdapter


class MahalanobisDistanceAdapter(SpecDrivenAdapter):
    """Mahalanobis Distance using YAML spec for metadata."""

    spec_path = "anomaly_detection/mahalanobis-distance.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        threshold = float(parameters.get("threshold", 3.0))
        contamination = float(parameters.get("contamination", 0.1))

        # Ensure valid parameters
        threshold = max(0.0, threshold)
        contamination = max(0.0, min(0.5, contamination))

        # Prepare data
        X = dataframe[features].copy()

        # Drop rows with missing values
        X = X.dropna()

        # Convert to numpy array
        X_array = X.to_numpy()

        # Calculate mean and covariance matrix
        mean = np.mean(X_array, axis=0)
        cov_matrix = np.cov(X_array, rowvar=False)

        # Check if covariance matrix is singular
        try:
            cov_inv = np.linalg.inv(cov_matrix)
        except np.linalg.LinAlgError:
            # Use pseudoinverse if covariance matrix is singular
            cov_inv = np.linalg.pinv(cov_matrix)
            warnings_list = [
                "Covariance matrix is singular. Using pseudo-inverse. "
                "Consider removing highly correlated features."
            ]
        else:
            warnings_list = []

        # Calculate Mahalanobis distance for each point
        distances = np.array(
            [mahalanobis(x, mean, cov_inv) for x in X_array]
        )

        # Convert to chi-square p-values (for interpretability)
        # Mahalanobis distance squared follows chi-square distribution
        # with degrees of freedom = number of features
        p_values = 1 - stats.chi2.cdf(distances**2, df=len(features))

        # Determine threshold
        # Option 1: Use fixed threshold (in standard deviations)
        # Option 2: Use contamination-based threshold (percentile)
        if contamination > 0:
            # Use contamination to set threshold as percentile
            threshold_value = np.percentile(distances, (1 - contamination) * 100)
        else:
            # Use fixed threshold (approximate as chi-square critical value)
            # For large samples, Mahalanobis distance ~ sqrt(chi2)
            chi2_critical = stats.chi2.ppf(1 - 0.05, df=len(features))
            threshold_value = np.sqrt(chi2_critical) * (threshold / 3.0)

        # Classify anomalies
        predictions = distances > threshold_value
        n_anomalies = int(predictions.sum())
        anomaly_percentage = float(n_anomalies / len(predictions) * 100)
        max_distance = float(distances.max())

        # Metrics
        metrics = {
            "n_anomalies": n_anomalies,
            "anomaly_percentage": anomaly_percentage,
            "max_distance": max_distance,
            "threshold_used": float(threshold_value),
        }

        # Distance scatter plot (use first 2 features for visualization)
        scatter_data = []
        for idx, row in X.iterrows():
            loc = X.index.get_loc(idx)
            scatter_data.append(
                {
                    "feature1": float(row[features[0]]),
                    "feature2": float(row[features[1]] if len(features) > 1 else distances[loc]),
                    "distance": float(distances[loc]),
                    "is_anomaly": bool(predictions[loc]),
                    "p_value": float(p_values[loc]),
                }
            )

        # Distance distribution histogram
        n_bins = min(30, len(distances) // 10) if len(distances) > 30 else 10
        hist, bin_edges = np.histogram(distances, bins=n_bins)
        distribution_data = []
        for i in range(len(hist)):
            bin_center = (bin_edges[i] + bin_edges[i + 1]) / 2
            # Check if this bin contains anomalies
            bin_mask = (distances >= bin_edges[i]) & (distances < bin_edges[i + 1])
            anomalies_in_bin = int(predictions[bin_mask].sum())
            distribution_data.append(
                {
                    "distance": float(bin_center),
                    "count": int(hist[i]),
                    "anomaly_count": anomalies_in_bin,
                    "normal_count": int(hist[i]) - anomalies_in_bin,
                    "bin_start": float(bin_edges[i]),
                    "bin_end": float(bin_edges[i + 1]),
                }
            )

        charts = [
            {
                "type": "distance_scatter",
                "title": "Mahalanobis Distance in Feature Space",
                "data": scatter_data,
            },
            {
                "type": "distance_distribution",
                "title": "Mahalanobis Distance Distribution",
                "data": distribution_data,
            },
        ]

        # Top anomalies table
        anomaly_indices = np.where(predictions)[0]
        sorted_anomaly_indices = sorted(
            anomaly_indices,
            key=lambda i: distances[i],
            reverse=True
        )[:10]

        top_anomalies = []
        for i in sorted_anomaly_indices:
            anomaly_entry = {
                "index": int(X.index[i]),
                "distance": float(distances[i]),
                "p_value": float(p_values[i]),
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
            f"Mahalanobis Distance detected {n_anomalies} anomalies "
            f"({anomaly_percentage:.1f}% of data).",
            f"Threshold used: {threshold_value:.2f} (distance units).",
            "Mahalanobis distance accounts for correlations between features, "
            "unlike Euclidean distance.",
            f"Maximum distance in dataset: {max_distance:.2f}.",
        ]

        if contamination > 0:
            explanations.append(
                f"Threshold automatically calculated using {contamination * 100:.1f}% "
                "expected contamination."
            )
        else:
            explanations.append(
                f"Using fixed threshold of {threshold:.1f} standard deviations."
            )

        explanations.append(
            "Points with high Mahalanobis distance are outliers considering "
            "feature correlations."
        )

        # Warnings
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings_list.append(
                f"Dropped {dropped} rows with missing values before detection."
            )

        if n_anomalies == 0:
            warnings_list.append(
                "No anomalies detected. Consider lowering threshold or increasing contamination."
            )

        if len(features) < 2:
            warnings_list.append(
                "Mahalanobis Distance works best with at least 2 features. "
                "Consider using more features."
            )

        if len(X) < len(features) * 10:
            warnings_list.append(
                f"Sample size ({len(X)}) is small relative to features ({len(features)}). "
                "Covariance estimation may be unreliable."
            )

        # Check for multicollinearity
        condition_number = np.linalg.cond(cov_matrix)
        if condition_number > 1000:
            warnings_list.append(
                f"High condition number ({condition_number:.0f}) detected. "
                "Features may be highly correlated. Consider feature selection."
            )

        return {
            "summary": {
                "feature_columns": features,
                "total_samples": len(X),
                "n_anomalies": n_anomalies,
                "threshold_used": float(threshold_value),
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings_list,
        }
