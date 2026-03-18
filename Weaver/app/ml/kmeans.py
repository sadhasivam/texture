"""K-Means Clustering algorithm adapter."""

import pandas as pd
from sklearn.cluster import KMeans as SklearnKMeans
from sklearn.metrics import silhouette_score

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class KMeansAdapter(AlgorithmAdapter):
    id = "kmeans"
    name = "K-Means Clustering"
    category = "clustering"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            group="unsupervised",
            subgroup="clustering",
            description="Partitions data into K distinct clusters based on feature similarity.",
            tags=["unsupervised", "fast", "simple", "centroid-based", "beginner-friendly"],
            difficulty="beginner",
            model_family="clustering",
            target=AlgorithmTarget(
                required=False,  # Unsupervised - no target needed!
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
                    name="n_clusters",
                    type="int",
                    default=3,
                    label="Number of clusters (K)",
                ),
                AlgorithmParameter(
                    name="max_iter",
                    type="int",
                    default=300,
                    label="Maximum iterations",
                ),
                AlgorithmParameter(
                    name="random_state",
                    type="int",
                    default=42,
                    label="Random seed",
                ),
            ],
            outputs=AlgorithmOutputs(
                metrics=["inertia", "silhouette_score"],
                charts=["cluster_scatter", "elbow_curve"],
                tables=["cluster_summary"],
            ),
            validation_rules=[
                "At least 2 feature columns required",
                "All features must be numeric",
                "Number of clusters must be less than number of samples",
            ],
        )

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        n_clusters = parameters.get("n_clusters", 3)
        max_iter = parameters.get("max_iter", 300)
        random_state = parameters.get("random_state", 42)

        # Prepare data
        X = dataframe[features]

        # Drop rows with missing values
        X = X.dropna()

        # Train K-Means
        model = SklearnKMeans(
            n_clusters=n_clusters, max_iter=max_iter, random_state=random_state
        )
        cluster_labels = model.fit_predict(X)

        # Calculate metrics
        inertia = float(model.inertia_)

        # Silhouette score (only if n_clusters > 1 and n_samples > n_clusters)
        silhouette = None
        if n_clusters > 1 and len(X) > n_clusters:
            silhouette = float(silhouette_score(X, cluster_labels))

        metrics = {
            "inertia": inertia,
        }

        if silhouette is not None:
            metrics["silhouette_score"] = silhouette

        # Cluster scatter plot (use first 2 features for visualization)
        scatter_data = []
        for idx, row in X.iterrows():
            scatter_data.append({
                "x": float(row[features[0]]),
                "y": float(row[features[1]] if len(features) > 1 else row[features[0]]),
                "cluster": int(cluster_labels[X.index.get_loc(idx)]),
            })

        # Cluster centers
        centers_data = []
        for i, center in enumerate(model.cluster_centers_):
            centers_data.append({
                "x": float(center[0]),
                "y": float(center[1] if len(center) > 1 else center[0]),
                "cluster": int(i),
            })

        charts = [
            {
                "type": "cluster_scatter",
                "title": "Cluster Visualization",
                "data": scatter_data,
                "centers": centers_data,
            }
        ]

        # Cluster summary table
        cluster_summary = []
        for cluster_id in range(n_clusters):
            cluster_mask = cluster_labels == cluster_id
            cluster_size = int(cluster_mask.sum())
            cluster_summary.append({
                "cluster": cluster_id,
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
            f"K-Means partitioned the data into {n_clusters} clusters.",
            f"Within-cluster sum of squares (inertia): {inertia:.2f}. Lower is better.",
        ]

        if silhouette is not None:
            explanations.append(
                f"Silhouette score: {silhouette:.3f}. "
                "Ranges from -1 to 1, where higher values indicate better-defined clusters."
            )

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(
                f"Dropped {dropped} rows with missing values before clustering."
            )

        if n_clusters >= len(X):
            warnings.append(
                "Number of clusters is equal to or greater than number of samples. "
                "Consider reducing the number of clusters."
            )

        return {
            "summary": {
                "n_clusters": n_clusters,
                "feature_columns": features,
                "total_samples": len(X),
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
