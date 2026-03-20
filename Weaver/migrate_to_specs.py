"""Migrate existing algorithm adapters to YAML specs.

This script reads existing Python algorithm adapters and generates YAML specs.
"""
import importlib
import yaml
from pathlib import Path

# Import all existing adapters
from app.ml.linear_regression import LinearRegressionAdapter
from app.ml.logistic_regression import LogisticRegressionAdapter
from app.ml.naive_bayes import NaiveBayesAdapter
from app.ml.decision_tree import DecisionTreeAdapter
from app.ml.random_forest import RandomForestAdapter
from app.ml.gradient_boosting import GradientBoostingAdapter
from app.ml.adaboost import AdaBoostAdapter
from app.ml.xgboost_adapter import XGBoostAdapter
from app.ml.svm import SVMAdapter
from app.ml.knn import KNNAdapter
from app.ml.kmeans import KMeansAdapter
from app.ml.dbscan import DBSCANAdapter
from app.ml.pca import PCAAdapter
from app.ml.tsne import TSNEAdapter
from app.ml.isolation_forest import IsolationForestAdapter


def adapter_to_yaml_spec(adapter_class, output_dir: Path):
    """Convert an adapter's metadata to YAML spec."""
    adapter = adapter_class()
    metadata = adapter.get_metadata()

    # Determine category directory
    if metadata.group == "supervised":
        category_dir = "supervised"
    elif metadata.group == "unsupervised":
        category_dir = "unsupervised"
    elif metadata.group == "anomaly_detection":
        category_dir = "unsupervised"  # Place anomaly detection with unsupervised
    else:
        category_dir = "other"

    # Build YAML spec
    spec = {
        "apiVersion": "texture.ml/v1",
        "kind": "Algorithm",
        "metadata": {
            "name": metadata.id.replace("_", "-"),
            "displayName": metadata.name,
            "namespace": f"{category_dir}-learning",
            "labels": {
                "difficulty": metadata.difficulty,
                "model-family": metadata.model_family,
                "category": metadata.category,
            },
            "annotations": {
                "texture.ml/version": "1.0.0",
            }
        },
        "spec": {
            "ontologyRef": f"base/ontology-{metadata.group}-{metadata.subgroup}.yaml",
            "dependencyRef": "base/dependencies-sklearn-base.yaml",
            "id": metadata.id,
            "description": metadata.description,
            "tags": metadata.tags,
            "difficulty": metadata.difficulty,
            "modelFamily": metadata.model_family,
            "target": {
                "required": metadata.target.required,
                "types": metadata.target.allowed_types,
                "cardinality": metadata.target.cardinality,
                "nullable": False,
            },
            "features": {
                "required": metadata.features.required,
                "types": metadata.features.allowed_types,
                "min": metadata.features.min_columns,
                "max": metadata.features.max_columns,
            },
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "default": param.default,
                    "label": param.label,
                }
                for param in metadata.parameters
            ],
            "outputs": {
                "metrics": [
                    {"name": metric}
                    for metric in metadata.outputs.metrics
                ],
                "visualizations": [
                    {
                        "name": chart,
                        "defaultChart": "scatter" if "scatter" in chart or "actual" in chart else "bar",
                        "title": chart.replace("_", " ").title(),
                    }
                    for chart in metadata.outputs.charts
                ],
                "tables": [
                    {
                        "name": table,
                        "title": table.replace("_", " ").title(),
                    }
                    for table in metadata.outputs.tables
                ],
            },
            "validationRules": metadata.validation_rules,
            "handler": {
                "module": f"app.ml.{metadata.id}",
                "class": adapter_class.__name__.replace("Adapter", "SpecAdapter"),
                "interface": "AlgorithmAdapter",
            }
        }
    }

    # Write to file
    output_path = output_dir / category_dir / f"{metadata.id.replace('_', '-')}.yaml"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✓ Generated: {output_path.relative_to(output_dir.parent)}")
    return metadata


def main():
    output_dir = Path(__file__).parent.parent / "algorithms"

    print("=" * 70)
    print("Migrating Algorithms to YAML Specs")
    print("=" * 70)
    print()

    adapters = [
        LinearRegressionAdapter,
        LogisticRegressionAdapter,
        NaiveBayesAdapter,
        DecisionTreeAdapter,
        RandomForestAdapter,
        GradientBoostingAdapter,
        AdaBoostAdapter,
        XGBoostAdapter,
        SVMAdapter,
        KNNAdapter,
        KMeansAdapter,
        DBSCANAdapter,
        PCAAdapter,
        TSNEAdapter,
        IsolationForestAdapter,
    ]

    for adapter_class in adapters:
        try:
            adapter_to_yaml_spec(adapter_class, output_dir)
        except Exception as e:
            print(f"✗ Failed {adapter_class.__name__}: {e}")

    print()
    print("=" * 70)
    print("Migration Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
