"""Test all algorithms end-to-end with real data."""
import pandas as pd
import numpy as np
from app.services.spec_registry import spec_registry

# Initialize registry
spec_registry.auto_discover_and_register()

def create_regression_data():
    """Create sample regression dataset."""
    np.random.seed(42)
    n = 100
    X1 = np.random.randn(n)
    X2 = np.random.randn(n)
    y = 2 * X1 + 3 * X2 + np.random.randn(n) * 0.5
    return pd.DataFrame({'feature1': X1, 'feature2': X2, 'target': y})

def create_classification_data():
    """Create sample classification dataset."""
    np.random.seed(42)
    n = 100
    X1 = np.random.randn(n)
    X2 = np.random.randn(n)
    y_int = (X1 + X2 > 0).astype(int)
    y = pd.Categorical(y_int)  # Categorical type from integers
    return pd.DataFrame({'feature1': X1, 'feature2': X2, 'target': y})

def create_clustering_data():
    """Create sample clustering dataset."""
    np.random.seed(42)
    n = 100
    X1 = np.random.randn(n)
    X2 = np.random.randn(n)
    return pd.DataFrame({'feature1': X1, 'feature2': X2})

def test_algorithm(algo_id, dataframe, target, features, parameters):
    """Test a single algorithm."""
    try:
        adapter = spec_registry.get_adapter(algo_id)
        if not adapter:
            return f"✗ {algo_id}: Not found in registry"

        # Validate - infer schema from actual dtypes
        metadata = adapter.get_metadata()
        schema = []
        for col in dataframe.columns:
            dtype = dataframe[col].dtype
            if pd.api.types.is_categorical_dtype(dtype):
                inferred_type = 'categorical'
            elif pd.api.types.is_bool_dtype(dtype):
                inferred_type = 'boolean'
            elif pd.api.types.is_numeric_dtype(dtype):
                inferred_type = 'numeric'
            else:
                inferred_type = 'text'
            schema.append({'name': col, 'inferred_type': inferred_type})

        if target:  # Supervised
            errors = adapter.validate_mapping(schema, target, features, parameters)
            if errors:
                return f"✗ {algo_id}: Validation failed: {errors[0]}"

        # Run
        result = adapter.run(dataframe, target, features, parameters)

        # Verify result structure
        if 'summary' not in result:
            return f"✗ {algo_id}: Missing 'summary' in result"
        if 'metrics' not in result:
            return f"✗ {algo_id}: Missing 'metrics' in result"
        if 'explanations' not in result:
            return f"✗ {algo_id}: Missing 'explanations' in result"

        metrics_str = ', '.join([f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                                 for k, v in list(result['metrics'].items())[:2]])
        return f"✓ {algo_id}: {metrics_str}"

    except Exception as e:
        return f"✗ {algo_id}: {str(e)}"

def main():
    print("=" * 80)
    print("Testing ALL Algorithms with Real Data")
    print("=" * 80)
    print()

    # Prepare datasets
    regression_df = create_regression_data()
    classification_df = create_classification_data()
    clustering_df = create_clustering_data()

    results = []

    # Regression algorithms
    print("REGRESSION ALGORITHMS:")
    print("-" * 80)
    regression_algos = ['linear_regression']
    for algo_id in regression_algos:
        result = test_algorithm(
            algo_id,
            regression_df,
            'target',
            ['feature1', 'feature2'],
            {'test_size': 0.2}
        )
        results.append(result)
        print(result)
    print()

    # Classification algorithms
    print("CLASSIFICATION ALGORITHMS:")
    print("-" * 80)
    classification_algos = ['logistic_regression', 'naive_bayes']
    for algo_id in classification_algos:
        result = test_algorithm(
            algo_id,
            classification_df,
            'target',
            ['feature1', 'feature2'],
            {'test_size': 0.2}
        )
        results.append(result)
        print(result)
    print()

    # Both (regression/classification) algorithms
    print("VERSATILE ALGORITHMS (testing with classification):")
    print("-" * 80)
    both_algos = ['decision_tree', 'random_forest', 'gradient_boosting',
                  'adaboost', 'xgboost', 'svm', 'knn']
    for algo_id in both_algos:
        result = test_algorithm(
            algo_id,
            classification_df,
            'target',
            ['feature1', 'feature2'],
            {'test_size': 0.2}
        )
        results.append(result)
        print(result)
    print()

    # Clustering algorithms (unsupervised)
    print("CLUSTERING ALGORITHMS:")
    print("-" * 80)
    clustering_algos = ['kmeans', 'dbscan']
    for algo_id in clustering_algos:
        params = {'n_clusters': 3} if algo_id == 'kmeans' else {'eps': 0.5, 'min_samples': 5}
        result = test_algorithm(
            algo_id,
            clustering_df,
            '',  # No target for unsupervised
            ['feature1', 'feature2'],
            params
        )
        results.append(result)
        print(result)
    print()

    # Dimensionality reduction
    print("DIMENSIONALITY REDUCTION:")
    print("-" * 80)
    dim_reduction_algos = ['pca', 'tsne']
    for algo_id in dim_reduction_algos:
        result = test_algorithm(
            algo_id,
            clustering_df,
            '',
            ['feature1', 'feature2'],
            {'n_components': 2}
        )
        results.append(result)
        print(result)
    print()

    # Anomaly detection
    print("ANOMALY DETECTION:")
    print("-" * 80)
    anomaly_algos = ['isolation_forest']
    for algo_id in anomaly_algos:
        result = test_algorithm(
            algo_id,
            clustering_df,
            '',
            ['feature1', 'feature2'],
            {'contamination': 0.1}
        )
        results.append(result)
        print(result)
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    passed = sum(1 for r in results if r.startswith('✓'))
    failed = sum(1 for r in results if r.startswith('✗'))
    print(f"Total: {len(results)} algorithms")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if failed > 0:
        print("FAILED ALGORITHMS:")
        for r in results:
            if r.startswith('✗'):
                print(f"  {r}")
        print()
        exit(1)
    else:
        print("✅ ALL ALGORITHMS PASSED!")
        print()

if __name__ == "__main__":
    main()
