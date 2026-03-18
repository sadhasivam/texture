"""DBSCAN (Density-Based Spatial Clustering) algorithm adapter."""

import pandas as pd
from sklearn.cluster import DBSCAN as SklearnDBSCAN
from sklearn.metrics import silhouette_score

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class DBSCANAdapter(AlgorithmAdapter):
    id = "dbscan"
    name = "DBSCAN"
    category = "clustering"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            group="unsupervised",
            subgroup="clustering",
            description="Density-based clustering that finds clusters of arbitrary shape and identifies outliers.",
            target=AlgorithmTarget(
                required=False,
                allowed_types=[],
                cardinality="single",
            ),
            features=AlgorithmFeatures(
                required=True,
                min_columns=2,
                max_columns=None,
                allowed_types=["numeric"],
            ),
            parameters=[
                AlgorithmParameter(
                    name="eps",
                    type="float",
                    default=0.5,
                    label="Epsilon (neighborhood radius)",
                ),
                AlgorithmParameter(
                    name="min_samples",
                    type="int",
                    default=5,
                    label="Minimum samples in neighborhood",
                ),
            ],
            outputs=AlgorithmOutputs(
                metrics=["n_clusters", "n_noise", "silhouette_score"],
                charts=["cluster_scatter"],
                tables=["cluster_summary"],
            ),
            validation_rules=[
                "At least 2 feature columns required",
                "All features must be numeric",
            ],
        )

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        eps = parameters.get("eps", 0.5)
        min_samples = parameters.get("min_samples", 5)

        # Prepare data
        X = dataframe[features]

        # Drop rows with missing values
        X = X.dropna()

        # Apply DBSCAN
        model = SklearnDBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = model.fit_predict(X)

        # Count clusters and noise points
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)

        metrics = {
            "n_clusters": n_clusters,
            "n_noise": n_noise,
        }

        # Silhouette score (only if at least 2 clusters and some non-noise points)
        if n_clusters > 1 and n_noise < len(cluster_labels):
            # Only calculate for non-noise points
            non_noise_mask = cluster_labels != -1
            if sum(non_noise_mask) > 0:
                silhouette = float(
                    silhouette_score(
                        X[non_noise_mask], cluster_labels[non_noise_mask]
                    )
                )
                metrics["silhouette_score"] = silhouette

        # Cluster scatter plot
        scatter_data = []
        for idx, row in X.iterrows():
            cluster_id = int(cluster_labels[X.index.get_loc(idx)])
            scatter_data.append({
                "x": float(row[features[0]]),
                "y": float(row[features[1]] if len(features) > 1 else row[features[0]]),
                "cluster": cluster_id,
                "is_noise": cluster_id == -1,
            })

        charts = [
            {
                "type": "cluster_scatter",
                "title": "DBSCAN Clustering",
                "data": scatter_data,
            }
        ]

        # Cluster summary
        cluster_summary = []
        unique_clusters = set(cluster_labels)

        for cluster_id in sorted(unique_clusters):
            if cluster_id == -1:
                cluster_summary.append({
                    "cluster": "Noise",
                    "cluster_id": -1,
                    "size": int(n_noise),
                    "percentage": float(n_noise / len(cluster_labels) * 100),
                })
            else:
                cluster_mask = cluster_labels == cluster_id
                cluster_size = int(cluster_mask.sum())
                cluster_summary.append({
                    "cluster": f"Cluster {cluster_id}",
                    "cluster_id": int(cluster_id),
                    "size": cluster_size,
                    "percentage": float(cluster_size / len(cluster_labels) * 100),
                })

        tables = [
            {
                "type": "cluster_summary",
                "rows": cluster_summary,
            }
        ]

        explanations = [
            f"DBSCAN identified {n_clusters} clusters based on density.",
            f"Found {n_noise} noise points ({n_noise/len(cluster_labels)*100:.1f}% of data).",
            f"Epsilon (neighborhood radius): {eps}. Smaller values create more strict clusters.",
            f"Minimum samples: {min_samples}. Core points must have this many neighbors.",
        ]

        if n_clusters == 0:
            explanations.append(
                "No clusters found. Try increasing epsilon or decreasing min_samples."
            )

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(
                f"Dropped {dropped} rows with missing values before clustering."
            )

        if n_noise > len(cluster_labels) * 0.5:
            warnings.append(
                f"More than 50% of points are noise. Consider adjusting parameters."
            )

        return {
            "summary": {
                "n_clusters": n_clusters,
                "feature_columns": features,
                "total_samples": len(X),
                "noise_points": n_noise,
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
