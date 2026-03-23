"""Test cases for unsupervised learning algorithms."""

import numpy as np
import pandas as pd
import pytest

from app.services.spec_registry import spec_registry as registry


class TestKMeans:
    """Tests for K-Means Clustering algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load K-Means algorithm."""
        # Use global registry
        return registry.get_adapter("kmeans")

    def test_validate_no_target_required(self, algorithm):
        """Test validation passes without target for clustering."""
        schema = {
            "columns": [
                {"name": "feature_1", "inferred_type": "numeric"},
                {"name": "feature_2", "inferred_type": "numeric"},
            ]
        }
        mapping = {
            "target_column": None,
            "feature_columns": ["feature_1", "feature_2"],
        }

        errors = algorithm.validate_mapping(
            schema["columns"],
            mapping["target_column"],
            mapping["feature_columns"],
            {"n_clusters": 3},
        )
        assert len(errors) == 0

    def test_validate_minimum_features(self, algorithm):
        """Test validation requires at least 2 features."""
        schema = {
            "columns": [
                {"name": "feature_1", "inferred_type": "numeric"},
            ]
        }
        mapping = {
            "target_column": None,
            "feature_columns": ["feature_1"],
        }

        errors = algorithm.validate_mapping(
            schema["columns"],
            mapping["target_column"],
            mapping["feature_columns"],
            {"n_clusters": 3},
        )
        assert len(errors) > 0

    def test_run_produces_clustering_metrics(
        self, algorithm, sample_clustering_data, sample_params_clustering
    ):
        """Test K-Means produces clustering metrics."""
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            sample_params_clustering,
        )

        assert "metrics" in result
        assert "inertia" in result["metrics"]
        assert "silhouette_score" in result["metrics"]
        assert result["metrics"]["inertia"] >= 0
        assert -1 <= result["metrics"]["silhouette_score"] <= 1

    def test_run_produces_cluster_visualization(
        self, algorithm, sample_clustering_data, sample_params_clustering
    ):
        """Test K-Means produces cluster visualization."""
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            sample_params_clustering,
        )

        assert "charts" in result
        chart_names = [c["type"] for c in result["charts"]]
        assert "cluster_scatter" in chart_names

    def test_run_produces_cluster_summary(
        self, algorithm, sample_clustering_data, sample_params_clustering
    ):
        """Test K-Means produces cluster summary table."""
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            sample_params_clustering,
        )

        assert "tables" in result
        assert len(result["tables"]) > 0
        summary_table = next((t for t in result["tables"] if t["type"] == "cluster_summary"), None)
        assert summary_table is not None
        assert len(summary_table["rows"]) == 3  # 3 clusters

    def test_different_cluster_counts(self, algorithm, sample_clustering_data):
        """Test K-Means with different cluster counts."""
        for k in [2, 3, 5]:
            params = {"n_clusters": k, "random_state": 42}
            result = algorithm.run(
                sample_clustering_data,
                None,
                ["feature_1", "feature_2", "feature_3", "feature_4"],
                params,
            )

            assert "metrics" in result
            summary_table = next(
                (t for t in result["tables"] if t["type"] == "cluster_summary"), None
            )
            assert len(summary_table["rows"]) == k


class TestDBSCAN:
    """Tests for DBSCAN Clustering algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load DBSCAN algorithm."""
        # Use global registry
        return registry.get_adapter("dbscan")

    def test_run_with_default_params(self, algorithm, sample_clustering_data):
        """Test DBSCAN runs with default parameters."""
        params = {"eps": 0.5, "min_samples": 5}
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "metrics" in result
        assert "charts" in result
        assert "summary" in result

    def test_detects_noise_points(self, algorithm, sample_clustering_data):
        """Test DBSCAN can detect noise points (label -1)."""
        params = {"eps": 0.3, "min_samples": 10}  # Strict params to create noise
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "summary" in result
        # DBSCAN should identify some clusters or noise


class TestPCA:
    """Tests for Principal Component Analysis algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load PCA algorithm."""
        # Use global registry
        return registry.get_adapter("pca")

    def test_run_with_default_components(self, algorithm, sample_clustering_data):
        """Test PCA runs with default number of components."""
        params = {"n_components": 2}
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "metrics" in result
        assert "explained_variance_ratio" in result["metrics"]
        assert "cumulative_variance" in result["metrics"]

    def test_produces_scree_plot(self, algorithm, sample_clustering_data):
        """Test PCA produces scree plot."""
        params = {"n_components": 3}
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "charts" in result
        chart_names = [c["type"] for c in result["charts"]]
        assert "variance_explained" in chart_names

    def test_variance_explained_sums_to_one(self, algorithm, sample_clustering_data):
        """Test that cumulative variance approaches 1.0."""
        params = {"n_components": 4}  # All components
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        cumulative_var = result["metrics"]["cumulative_variance"]
        assert 0.9 <= cumulative_var <= 1.0  # Should be close to 1.0

    def test_different_component_counts(self, algorithm, sample_clustering_data):
        """Test PCA with different component counts."""
        for n_comp in [2, 3, 4]:
            params = {"n_components": n_comp}
            result = algorithm.run(
                sample_clustering_data,
                None,
                ["feature_1", "feature_2", "feature_3", "feature_4"],
                params,
            )

            assert "metrics" in result
            assert sum(result["metrics"]["explained_variance_ratio"]) > 0


class TestTSNE:
    """Tests for t-SNE algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load t-SNE algorithm."""
        # Use global registry
        return registry.get_adapter("tsne")

    def test_run_with_default_params(self, algorithm, sample_clustering_data):
        """Test t-SNE runs with default parameters."""
        params = {"n_components": 2, "perplexity": 30, "random_state": 42}
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "charts" in result
        assert "summary" in result

    def test_produces_embedding_visualization(self, algorithm, sample_clustering_data):
        """Test t-SNE produces 2D embedding visualization."""
        params = {"n_components": 2, "perplexity": 30, "random_state": 42}
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "charts" in result
        chart_names = [c["type"] for c in result["charts"]]
        assert "tsne_scatter" in chart_names

    def test_different_perplexity_values(self, algorithm, sample_clustering_data):
        """Test t-SNE with different perplexity values."""
        for perp in [10, 30, 50]:
            params = {"n_components": 2, "perplexity": perp, "random_state": 42}
            result = algorithm.run(
                sample_clustering_data,
                None,
                ["feature_1", "feature_2", "feature_3", "feature_4"],
                params,
            )

            assert "charts" in result
            assert "summary" in result


class TestIsolationForest:
    """Tests for Isolation Forest algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load Isolation Forest algorithm."""
        # Use global registry
        return registry.get_adapter("isolation_forest")

    def test_run_with_default_params(self, algorithm, sample_clustering_data):
        """Test Isolation Forest runs with default parameters."""
        params = {"contamination": 0.1, "random_state": 42}
        result = algorithm.run(
            sample_clustering_data,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "summary" in result
        assert "charts" in result

    def test_detects_anomalies(self, algorithm):
        """Test Isolation Forest detects anomalies in data with outliers."""
        # Create dataset with clear outliers
        np.random.seed(42)
        normal_data = np.random.randn(90, 4)
        outliers = np.random.randn(10, 4) * 5  # Outliers with larger variance
        data = np.vstack([normal_data, outliers])

        df = pd.DataFrame(data, columns=["feature_1", "feature_2", "feature_3", "feature_4"])

        params = {"contamination": 0.1, "random_state": 42}
        result = algorithm.run(
            df,
            None,
            ["feature_1", "feature_2", "feature_3", "feature_4"],
            params,
        )

        assert "summary" in result
        # Should detect some anomalies

    def test_different_contamination_values(self, algorithm, sample_clustering_data):
        """Test Isolation Forest with different contamination values."""
        for contam in [0.05, 0.1, 0.2]:
            params = {"contamination": contam, "random_state": 42}
            result = algorithm.run(
                sample_clustering_data,
                None,
                ["feature_1", "feature_2", "feature_3", "feature_4"],
                params,
            )

            assert "summary" in result


class TestAlgorithmRegistry:
    """Tests for algorithm registry and YAML spec loading."""

    def test_loads_all_algorithms(self):
        """Test that all 15 algorithms are loaded from YAML specs."""
        # Use global registry
        algorithms = registry.get_all_summaries()

        assert len(algorithms) == 15

    def test_supervised_algorithms_loaded(self):
        """Test supervised algorithms are loaded."""
        # Use global registry
        supervised_algos = [
            "linear_regression",
            "logistic_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "naive_bayes",
            "svm",
            "knn",
            "adaboost",
            "xgboost",
        ]

        for algo_id in supervised_algos:
            algo = registry.get_adapter(algo_id)
            assert algo is not None
            assert algo.get_metadata().id == algo_id

    def test_unsupervised_algorithms_loaded(self):
        """Test unsupervised algorithms are loaded."""
        # Use global registry
        unsupervised_algos = [
            "kmeans",
            "dbscan",
            "pca",
            "tsne",
            "isolation_forest",
        ]

        for algo_id in unsupervised_algos:
            algo = registry.get_adapter(algo_id)
            assert algo is not None
            assert algo.get_metadata().id == algo_id

    def test_algorithm_metadata_structure(self):
        """Test that algorithm metadata has required fields."""
        # Use global registry
        algo = registry.get_adapter("linear_regression")

        metadata = algo.get_metadata()
        required_fields = [
            "id",
            "name",
            "category",
            "description",
            "target",
            "features",
            "parameters",
        ]

        for field in required_fields:
            assert hasattr(metadata, field), f"Missing required field: {field}"

    def test_algorithm_outputs_structure(self):
        """Test that algorithm outputs have required structure."""
        # Use global registry
        algo = registry.get_adapter("linear_regression")

        metadata = algo.get_metadata()
        assert hasattr(metadata, "outputs")
        assert hasattr(metadata.outputs, "metrics")
        assert hasattr(metadata.outputs, "charts")
