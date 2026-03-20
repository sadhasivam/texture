"""Generate minimal spec-driven adapters from existing implementations.

This extracts only the run() method from existing adapters and creates
new spec-driven versions.
"""
import ast
import inspect
from pathlib import Path

# Import existing adapters
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


def extract_run_method(adapter_class):
    """Extract the run() method source code from an adapter."""
    source = inspect.getsource(adapter_class.run)
    # Remove the first line (def run) and dedent
    lines = source.split('\n')[1:]  # Skip def line
    # Find minimum indentation
    min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
    # Dedent
    dedented = '\n'.join(line[min_indent:] if len(line) > min_indent else line for line in lines)
    return dedented


def generate_spec_adapter(adapter_class, output_dir: Path):
    """Generate a minimal spec-driven adapter."""
    adapter = adapter_class()
    metadata = adapter.get_metadata()

    # Determine spec path
    if metadata.group == "supervised":
        spec_path = f"supervised/{metadata.id.replace('_', '-')}.yaml"
    elif metadata.group == "unsupervised":
        spec_path = f"unsupervised/{metadata.id.replace('_', '-')}.yaml"
    elif metadata.group == "anomaly_detection":
        spec_path = f"unsupervised/{metadata.id.replace('_', '-')}.yaml"
    else:
        spec_path = f"other/{metadata.id.replace('_', '-')}.yaml"

    # Get original file to extract imports and run method
    original_file = Path(inspect.getfile(adapter_class))
    with open(original_file, 'r') as f:
        original_code = f.read()

    # Parse to extract imports
    tree = ast.parse(original_code)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and not node.module.startswith('app.schemas'):
                names = ', '.join(alias.name for alias in node.names)
                imports.append(f"from {node.module} import {names}")

    # Remove duplicate imports
    imports = list(dict.fromkeys(imports))

    # Extract run method
    run_method_source = inspect.getsource(adapter_class.run)

    # Build new file content
    content = f'''"""Spec-driven {metadata.name} - minimal boilerplate."""
{chr(10).join(imports)}

from app.ml.spec_adapter import SpecDrivenAdapter


class {adapter_class.__name__.replace('Adapter', 'SpecAdapter')}(SpecDrivenAdapter):
    """"{metadata.name} using YAML spec for metadata."""

    spec_path = "{spec_path}"

{run_method_source}
'''

    # Write file
    output_path = output_dir / f"{metadata.id}_spec.py"
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✓ Generated: {output_path.name}")


def main():
    output_dir = Path(__file__).parent / "app" / "ml"

    print("=" * 70)
    print("Generating Spec-Driven Adapters")
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
            generate_spec_adapter(adapter_class, output_dir)
        except Exception as e:
            print(f"✗ Failed {adapter_class.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 70)
    print("Generation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
