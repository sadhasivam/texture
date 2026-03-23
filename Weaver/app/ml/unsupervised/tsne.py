"""Spec-driven t-SNE - minimal boilerplate."""

import pandas as pd
from sklearn.manifold import TSNE as SklearnTSNE

from app.ml.spec_adapter import SpecDrivenAdapter


class TSNEAdapter(SpecDrivenAdapter):
    """ "t-SNE using YAML spec for metadata."""

    spec_path = "unsupervised/tsne.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        n_components = int(parameters.get("n_components", 2))
        perplexity = float(parameters.get("perplexity", 30.0))
        learning_rate = float(parameters.get("learning_rate", 200.0))

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
            warnings.append(f"Dropped {dropped} rows with missing values before t-SNE.")

        if perplexity != parameters.get("perplexity", 30.0):
            warnings.append(f"Perplexity adjusted to {perplexity:.0f} to fit dataset size.")

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
