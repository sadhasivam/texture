"""Enrich algorithm YAML specs with detailed chart specifications."""
import yaml
from pathlib import Path

# Chart specifications for each algorithm
CHART_SPECS = {
    "linear_regression": {
        "metrics": [
            {"name": "r2", "displayName": "R² Score", "description": "Proportion of variance explained", "range": [-999, 1.0], "higherIsBetter": True},
            {"name": "mae", "displayName": "Mean Absolute Error", "description": "Average absolute difference", "range": [0, 999999], "higherIsBetter": False},
            {"name": "rmse", "displayName": "Root Mean Squared Error", "description": "Square root of average squared errors", "range": [0, 999999], "higherIsBetter": False},
        ],
        "visualizations": [
            {"name": "predicted_vs_actual", "defaultChart": "scatter", "title": "Predicted vs Actual", "description": "Compare predictions to actual values", "dataFields": {"x": "actual", "y": "predicted", "trend": "best_fit"}, "availableCharts": ["scatter", "line"]},
            {"name": "residual_plot", "defaultChart": "scatter", "title": "Residual Plot", "description": "Distribution of prediction errors", "dataFields": {"x": "predicted", "y": "residual"}, "availableCharts": ["scatter", "histogram"]},
        ],
        "tables": [
            {"name": "coefficients", "title": "Feature Coefficients", "description": "Linear coefficients for each feature", "columns": [{"name": "feature", "type": "string"}, {"name": "coefficient", "type": "float"}]},
        ],
    },
    "logistic_regression": {
        "metrics": [
            {"name": "accuracy", "displayName": "Accuracy", "description": "Proportion of correct predictions", "range": [0, 1], "higherIsBetter": True},
            {"name": "precision", "displayName": "Precision", "description": "Precision score", "range": [0, 1], "higherIsBetter": True},
            {"name": "recall", "displayName": "Recall", "description": "Recall score", "range": [0, 1], "higherIsBetter": True},
            {"name": "f1", "displayName": "F1 Score", "description": "Harmonic mean of precision and recall", "range": [0, 1], "higherIsBetter": True},
        ],
        "visualizations": [
            {"name": "confusion_matrix", "defaultChart": "heatmap", "title": "Confusion Matrix", "description": "Classification results matrix", "dataFields": {"matrix": "confusion"}, "availableCharts": ["heatmap", "table"]},
            {"name": "class_distribution", "defaultChart": "bar", "title": "Class Distribution", "description": "Distribution of predicted classes", "dataFields": {"x": "class", "y": "count"}, "availableCharts": ["bar", "pie"]},
        ],
        "tables": [
            {"name": "coefficients", "title": "Feature Coefficients", "description": "Logistic regression coefficients", "columns": [{"name": "feature", "type": "string"}, {"name": "coefficient", "type": "float"}]},
        ],
    },
    "decision_tree": {
        "visualizations": [
            {"name": "feature_importance", "defaultChart": "bar", "title": "Feature Importance", "description": "Relative importance of each feature", "dataFields": {"x": "feature", "y": "importance"}, "availableCharts": ["bar", "horizontal-bar"]},
        ],
    },
    "kmeans": {
        "metrics": [
            {"name": "inertia", "displayName": "Inertia", "description": "Within-cluster sum of squares", "range": [0, 999999], "higherIsBetter": False},
            {"name": "silhouette_score", "displayName": "Silhouette Score", "description": "How well-separated clusters are", "range": [-1, 1], "higherIsBetter": True},
        ],
        "visualizations": [
            {"name": "cluster_scatter", "defaultChart": "scatter", "title": "Cluster Visualization", "description": "Data points colored by cluster", "dataFields": {"x": "feature_0", "y": "feature_1", "cluster": "cluster_id", "centers": "cluster_centers"}, "availableCharts": ["scatter", "3d-scatter"]},
        ],
        "tables": [
            {"name": "cluster_summary", "title": "Cluster Summary", "description": "Size and percentage of each cluster", "columns": [{"name": "cluster", "type": "int"}, {"name": "size", "type": "int"}, {"name": "percentage", "type": "float"}]},
        ],
    },
    "pca": {
        "metrics": [
            {"name": "explained_variance_ratio", "displayName": "Explained Variance Ratio", "description": "Proportion of variance per component", "range": [0, 1], "higherIsBetter": True},
            {"name": "cumulative_variance", "displayName": "Cumulative Variance", "description": "Total variance explained", "range": [0, 1], "higherIsBetter": True},
        ],
        "visualizations": [
            {"name": "scree_plot", "defaultChart": "line", "title": "Scree Plot", "description": "Variance explained by each component", "dataFields": {"x": "component", "y": "variance"}, "availableCharts": ["line", "bar"]},
            {"name": "biplot", "defaultChart": "scatter", "title": "PCA Biplot", "description": "Data projected onto principal components", "dataFields": {"x": "pc1", "y": "pc2"}, "availableCharts": ["scatter"]},
        ],
    },
}

def enrich_spec(spec_path: Path):
    """Enrich a single algorithm YAML with chart specs."""
    with open(spec_path, 'r') as f:
        spec = yaml.safe_load(f)

    algo_id = spec['spec']['id']

    # Check if we have chart specs for this algorithm
    if algo_id in CHART_SPECS:
        chart_spec = CHART_SPECS[algo_id]

        # Update metrics if provided
        if 'metrics' in chart_spec:
            spec['spec']['outputs']['metrics'] = chart_spec['metrics']

        # Update visualizations if provided
        if 'visualizations' in chart_spec:
            # Merge with existing or replace
            spec['spec']['outputs']['visualizations'] = chart_spec['visualizations']

        # Update tables if provided
        if 'tables' in chart_spec:
            spec['spec']['outputs']['tables'] = chart_spec['tables']

        # Write back
        with open(spec_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"✓ Enriched: {spec_path.name}")
        return True
    else:
        print(f"- Skipped: {spec_path.name} (no chart spec defined)")
        return False

def main():
    base_path = Path("algorithms")

    print("=" * 70)
    print("Enriching Algorithm YAMLs with Chart Specifications")
    print("=" * 70)
    print()

    enriched = 0
    skipped = 0

    for category in ["supervised", "unsupervised"]:
        category_path = base_path / category
        if category_path.exists():
            for yaml_file in sorted(category_path.glob("*.yaml")):
                if enrich_spec(yaml_file):
                    enriched += 1
                else:
                    skipped += 1

    print()
    print("=" * 70)
    print(f"Enriched: {enriched} algorithms")
    print(f"Skipped: {skipped} algorithms (no spec defined yet)")
    print("=" * 70)

if __name__ == "__main__":
    main()
