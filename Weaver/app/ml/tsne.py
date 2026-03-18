"""t-SNE (t-Distributed Stochastic Neighbor Embedding) algorithm adapter."""

import pandas as pd
from sklearn.manifold import TSNE as SklearnTSNE

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class TSNEAdapter(AlgorithmAdapter):
    id = "tsne"
    name = "t-SNE"
    category = "dimensionality_reduction"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            group="unsupervised",
            subgroup="dimensionality_reduction",
            description="Non-linear dimensionality reduction optimized for visualization by preserving local structure.",
            target=AlgorithmTarget(
                required=False,
                allowed_types=["numeric", "categorical", "boolean"],
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
                    name="n_components",
                    type="int",
                    default=2,
                    label="Number of dimensions",
                ),
                AlgorithmParameter(
                    name="perplexity",
                    type="float",
                    default=30.0,
                    label="Perplexity",
                ),
                AlgorithmParameter(
                    name="learning_rate",
                    type="float",
                    default=200.0,
                    label="Learning rate",
                ),
            ],
            outputs=AlgorithmOutputs(
                metrics=["kl_divergence"],
                charts=["tsne_scatter"],
                tables=[],
            ),
            validation_rules=[
                "At least 2 feature columns required",
                "All features must be numeric",
                "Perplexity must be less than number of samples",
            ],
        )

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        n_components = parameters.get("n_components", 2)
        perplexity = parameters.get("perplexity", 30.0)
        learning_rate = parameters.get("learning_rate", 200.0)

        # Prepare data
        X = dataframe[features]

        # Drop rows with missing values
        X = X.dropna()

        # Adjust perplexity if needed
        max_perplexity = len(X) - 1
        if perplexity >= max_perplexity:
            perplexity = max(5.0, max_perplexity / 2)

        # Apply t-SNE
        tsne = SklearnTSNE(
            n_components=n_components,
            perplexity=perplexity,
            learning_rate=learning_rate,
            random_state=42,
        )
        X_transformed = tsne.fit_transform(X)

        # KL divergence (lower is better)
        kl_divergence = float(tsne.kl_divergence_)

        metrics = {
            "kl_divergence": kl_divergence,
        }

        # t-SNE scatter plot
        scatter_data = []
        for i, row in enumerate(X_transformed):
            point = {
                "x": float(row[0]),
            }
            if n_components >= 2:
                point["y"] = float(row[1])
            if n_components >= 3:
                point["z"] = float(row[2])

            # Add target value if provided (for coloring)
            if target and target in dataframe.columns:
                original_idx = X.index[i]
                point["target"] = str(dataframe.loc[original_idx, target])

            scatter_data.append(point)

        charts = [
            {
                "type": "tsne_scatter",
                "title": f"t-SNE Embedding ({n_components}D)",
                "data": scatter_data,
            }
        ]

        tables = []

        explanations = [
            f"t-SNE reduced {len(features)} features to {n_components} dimensions for visualization.",
            f"KL divergence: {kl_divergence:.2f}. Lower values indicate better preservation of structure.",
            f"Perplexity: {perplexity:.0f}. Controls the balance between local and global structure.",
            "t-SNE is excellent for visualization but not for general-purpose dimensionality reduction.",
        ]

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(
                f"Dropped {dropped} rows with missing values before t-SNE."
            )

        if perplexity != parameters.get("perplexity", 30.0):
            warnings.append(
                f"Perplexity adjusted to {perplexity:.0f} to fit dataset size."
            )

        if len(X) < 50:
            warnings.append(
                "t-SNE works best with larger datasets (100+ samples). "
                "Results may be less meaningful with small datasets."
            )

        return {
            "summary": {
                "n_components": n_components,
                "feature_columns": features,
                "total_samples": len(X),
                "perplexity": perplexity,
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
