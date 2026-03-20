"""Spec-driven PCA (Principal Component Analysis) - minimal boilerplate."""
import pandas as pd
from sklearn.decomposition import PCA as SklearnPCA

from app.ml.spec_adapter import SpecDrivenAdapter


class PCASpecAdapter(SpecDrivenAdapter):
    """"PCA (Principal Component Analysis) using YAML spec for metadata."""

    spec_path = "unsupervised/pca.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        n_components = parameters.get("n_components", 2)

        # Ensure n_components doesn't exceed features
        n_components = min(n_components, len(features))

        # Prepare data
        X = dataframe[features]

        # Drop rows with missing values
        X = X.dropna()

        # Fit PCA
        pca = SklearnPCA(n_components=n_components)
        X_transformed = pca.fit_transform(X)

        # Explained variance
        explained_variance_ratio = [
            float(var) for var in pca.explained_variance_ratio_
        ]
        cumulative_variance = []
        cumsum = 0
        for var in explained_variance_ratio:
            cumsum += var
            cumulative_variance.append(float(cumsum))

        metrics = {
            "explained_variance_ratio": explained_variance_ratio,
            "cumulative_variance": cumulative_variance[-1],
        }

        # PCA scatter plot (2D or 3D depending on components)
        scatter_data = []
        for i, row in enumerate(X_transformed):
            point = {
                "PC1": float(row[0]),
            }
            if n_components >= 2:
                point["PC2"] = float(row[1])
            if n_components >= 3:
                point["PC3"] = float(row[2])

            # Add target value if provided (for coloring)
            if target and target in dataframe.columns:
                point["target"] = str(dataframe.iloc[X.index[i]][target])

            scatter_data.append(point)

        # Variance explained bar chart
        variance_data = [
            {
                "component": f"PC{i+1}",
                "variance": float(explained_variance_ratio[i] * 100),
                "cumulative": float(cumulative_variance[i] * 100),
            }
            for i in range(n_components)
        ]

        charts = [
            {
                "type": "pca_scatter",
                "title": f"PCA Projection ({n_components}D)",
                "data": scatter_data,
            },
            {
                "type": "variance_explained",
                "title": "Variance Explained by Components",
                "data": variance_data,
            },
        ]

        # Component loadings (how much each feature contributes to each PC)
        loadings = pca.components_
        loading_table = []
        for i, feature in enumerate(features):
            row = {"feature": feature}
            for j in range(n_components):
                row[f"PC{j+1}"] = float(loadings[j][i])
            loading_table.append(row)

        tables = [
            {
                "type": "component_loadings",
                "rows": loading_table,
            }
        ]

        explanations = [
            f"PCA reduced {len(features)} features to {n_components} principal components.",
            f"The first {n_components} components explain {cumulative_variance[-1]*100:.1f}% of the total variance.",
        ]

        if n_components >= 1:
            explanations.append(
                f"PC1 alone explains {explained_variance_ratio[0]*100:.1f}% of the variance."
            )

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(
                f"Dropped {dropped} rows with missing values before PCA."
            )

        if n_components > len(features):
            warnings.append(
                f"Number of components ({n_components}) reduced to match number of features ({len(features)})."
            )

        return {
            "summary": {
                "n_components": n_components,
                "feature_columns": features,
                "total_samples": len(X),
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }

