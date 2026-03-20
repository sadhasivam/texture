"""Test cases for supervised learning algorithms."""
import pytest
import pandas as pd
import numpy as np
from app.services.algorithm_registry import registry


class TestLinearRegression:
    """Tests for Linear Regression algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load linear regression algorithm."""
        return registry.get_adapter("linear_regression")

    def test_validate_correct_mapping(self, algorithm, sample_regression_data):
        """Test validation passes with correct column mapping."""
        schema = {
            "columns": [
                {"name": "feature_1", "inferred_type": "numeric"},
                {"name": "feature_2", "inferred_type": "numeric"},
                {"name": "feature_3", "inferred_type": "numeric"},
                {"name": "target", "inferred_type": "numeric"},
            ]
        }
        mapping = {
            "target_column": "target",
            "feature_columns": ["feature_1", "feature_2", "feature_3"],
        }

        errors = algorithm.validate(schema, mapping, {"test_size": 0.2})
        assert len(errors) == 0

    def test_validate_non_numeric_target(self, algorithm):
        """Test validation fails with non-numeric target."""
        schema = {
            "columns": [
                {"name": "feature_1", "inferred_type": "numeric"},
                {"name": "target", "inferred_type": "categorical"},
            ]
        }
        mapping = {
            "target_column": "target",
            "feature_columns": ["feature_1"],
        }

        errors = algorithm.validate(schema, mapping, {"test_size": 0.2})
        assert len(errors) > 0
        assert any("numeric" in err.lower() for err in errors)

    def test_run_produces_metrics(self, algorithm, sample_regression_data, sample_params_regression):
        """Test algorithm execution produces required metrics."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        assert "metrics" in result
        assert "r2" in result["metrics"]
        assert "mae" in result["metrics"]
        assert "rmse" in result["metrics"]
        assert result["metrics"]["r2"] >= -1.0
        assert result["metrics"]["mae"] >= 0
        assert result["metrics"]["rmse"] >= 0

    def test_run_produces_visualizations(self, algorithm, sample_regression_data, sample_params_regression):
        """Test algorithm execution produces visualizations."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        assert "charts" in result
        chart_names = [c["type"] for c in result["charts"]]
        assert "predicted_vs_actual" in chart_names
        assert "residual_plot" in chart_names

    def test_run_produces_tables(self, algorithm, sample_regression_data, sample_params_regression):
        """Test algorithm execution produces coefficient table."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        assert "tables" in result
        assert len(result["tables"]) > 0
        coef_table = next((t for t in result["tables"] if t["type"] == "coefficients"), None)
        assert coef_table is not None
        assert len(coef_table["rows"]) == 3  # 3 features


class TestLogisticRegression:
    """Tests for Logistic Regression algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load logistic regression algorithm."""
        # Use global registry
        return registry.get_adapter("logistic_regression")

    def test_validate_categorical_target(self, algorithm):
        """Test validation passes with categorical target."""
        schema = {
            "columns": [
                {"name": "feature_1", "inferred_type": "numeric"},
                {"name": "target", "inferred_type": "categorical"},
            ]
        }
        mapping = {
            "target_column": "target",
            "feature_columns": ["feature_1"],
        }

        errors = algorithm.validate(schema, mapping, {"test_size": 0.2})
        assert len(errors) == 0

    def test_run_produces_classification_metrics(self, algorithm, sample_classification_data, sample_params_classification):
        """Test algorithm execution produces classification metrics."""
        result = algorithm.run(
            sample_classification_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_classification,
        )

        assert "metrics" in result
        assert "accuracy" in result["metrics"]
        assert "precision" in result["metrics"]
        assert "recall" in result["metrics"]
        assert "f1" in result["metrics"]
        assert 0 <= result["metrics"]["accuracy"] <= 1
        assert 0 <= result["metrics"]["f1"] <= 1

    def test_run_produces_confusion_matrix(self, algorithm, sample_classification_data, sample_params_classification):
        """Test algorithm produces confusion matrix visualization."""
        result = algorithm.run(
            sample_classification_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_classification,
        )

        assert "charts" in result
        chart_names = [c["type"] for c in result["charts"]]
        assert "confusion_matrix" in chart_names


class TestDecisionTree:
    """Tests for Decision Tree algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load decision tree algorithm."""
        # Use global registry
        return registry.get_adapter("decision_tree")

    def test_handles_regression_task(self, algorithm, sample_regression_data, sample_params_regression):
        """Test decision tree handles regression."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        assert "metrics" in result
        assert "r2" in result["metrics"]

    def test_handles_classification_task(self, algorithm, sample_classification_data, sample_params_classification):
        """Test decision tree handles classification."""
        result = algorithm.run(
            sample_classification_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_classification,
        )

        assert "metrics" in result
        assert "accuracy" in result["metrics"]

    def test_produces_feature_importance(self, algorithm, sample_regression_data, sample_params_regression):
        """Test decision tree produces feature importance."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        assert "charts" in result
        chart_names = [c["type"] for c in result["charts"]]
        assert "feature_importance" in chart_names


class TestRandomForest:
    """Tests for Random Forest algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load random forest algorithm."""
        # Use global registry
        return registry.get_adapter("random_forest")

    def test_run_with_default_params(self, algorithm, sample_regression_data):
        """Test random forest runs with default parameters."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            {"test_size": 0.2},
        )

        assert "metrics" in result
        assert "charts" in result
        assert "summary" in result

    def test_produces_feature_importance(self, algorithm, sample_regression_data, sample_params_regression):
        """Test random forest produces feature importance."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        chart_names = [c["type"] for c in result["charts"]]
        assert "feature_importance" in chart_names


class TestGradientBoosting:
    """Tests for Gradient Boosting algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load gradient boosting algorithm."""
        # Use global registry
        return registry.get_adapter("gradient_boosting")

    def test_run_with_custom_params(self, algorithm, sample_regression_data):
        """Test gradient boosting with custom parameters."""
        params = {
            "test_size": 0.2,
            "n_estimators": 50,
            "learning_rate": 0.1,
            "max_depth": 3,
        }
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            params,
        )

        assert "metrics" in result
        assert result["metrics"]["r2"] is not None


class TestNaiveBayes:
    """Tests for Naive Bayes algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load naive bayes algorithm."""
        # Use global registry
        return registry.get_adapter("naive_bayes")

    def test_classification_task(self, algorithm, sample_classification_data, sample_params_classification):
        """Test naive bayes classification."""
        result = algorithm.run(
            sample_classification_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_classification,
        )

        assert "metrics" in result
        assert "accuracy" in result["metrics"]
        assert 0 <= result["metrics"]["accuracy"] <= 1


class TestSVM:
    """Tests for Support Vector Machine algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load SVM algorithm."""
        # Use global registry
        return registry.get_adapter("svm")

    def test_regression_task(self, algorithm, sample_regression_data, sample_params_regression):
        """Test SVM regression."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        assert "metrics" in result
        assert "r2" in result["metrics"]

    def test_classification_task(self, algorithm, sample_classification_data, sample_params_classification):
        """Test SVM classification."""
        result = algorithm.run(
            sample_classification_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_classification,
        )

        assert "metrics" in result
        assert "accuracy" in result["metrics"]


class TestKNN:
    """Tests for K-Nearest Neighbors algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load KNN algorithm."""
        # Use global registry
        return registry.get_adapter("knn")

    def test_with_different_k_values(self, algorithm, sample_classification_data):
        """Test KNN with different k values."""
        for k in [3, 5, 7]:
            params = {"test_size": 0.2, "n_neighbors": k}
            result = algorithm.run(
                sample_classification_data,
                "target",
                ["feature_1", "feature_2", "feature_3"],
                params,
            )

            assert "metrics" in result
            assert "accuracy" in result["metrics"]


class TestAdaBoost:
    """Tests for AdaBoost algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load AdaBoost algorithm."""
        # Use global registry
        return registry.get_adapter("adaboost")

    def test_classification_task(self, algorithm, sample_classification_data, sample_params_classification):
        """Test AdaBoost classification."""
        result = algorithm.run(
            sample_classification_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_classification,
        )

        assert "metrics" in result
        assert "accuracy" in result["metrics"]


class TestXGBoost:
    """Tests for XGBoost algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load XGBoost algorithm."""
        # Use global registry
        return registry.get_adapter("xgboost")

    def test_regression_task(self, algorithm, sample_regression_data, sample_params_regression):
        """Test XGBoost regression."""
        result = algorithm.run(
            sample_regression_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_regression,
        )

        assert "metrics" in result
        assert "r2" in result["metrics"]

    def test_classification_task(self, algorithm, sample_classification_data, sample_params_classification):
        """Test XGBoost classification."""
        result = algorithm.run(
            sample_classification_data,
            "target",
            ["feature_1", "feature_2", "feature_3"],
            sample_params_classification,
        )

        assert "metrics" in result
        assert "accuracy" in result["metrics"]
