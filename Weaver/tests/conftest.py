"""Pytest configuration and shared fixtures for algorithm tests."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.services.spec_registry import spec_registry


@pytest.fixture(scope="session", autouse=True)
def load_algorithms():
    """Load all algorithms from YAML specs before running tests."""
    spec_registry.auto_discover_and_register()
    yield


@pytest.fixture
def sample_regression_data():
    """Sample dataset for regression algorithms."""
    np.random.seed(42)
    n_samples = 100
    X = np.random.randn(n_samples, 3)
    y = 2 * X[:, 0] + 3 * X[:, 1] - X[:, 2] + np.random.randn(n_samples) * 0.5

    df = pd.DataFrame(X, columns=["feature_1", "feature_2", "feature_3"])
    df["target"] = y
    return df


@pytest.fixture
def sample_classification_data():
    """Sample dataset for classification algorithms."""
    np.random.seed(42)
    n_samples = 100
    X = np.random.randn(n_samples, 3)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)

    df = pd.DataFrame(X, columns=["feature_1", "feature_2", "feature_3"])
    df["target"] = y.astype(str)  # Convert to string for classification
    return df


@pytest.fixture
def sample_multiclass_data():
    """Sample dataset for multiclass classification."""
    np.random.seed(42)
    n_samples = 150
    X = np.random.randn(n_samples, 4)
    y = np.random.randint(0, 3, n_samples)

    df = pd.DataFrame(X, columns=["feature_1", "feature_2", "feature_3", "feature_4"])
    df["target"] = y.astype(str)  # Convert to string for classification
    return df


@pytest.fixture
def sample_clustering_data():
    """Sample dataset for clustering algorithms."""
    np.random.seed(42)
    n_samples = 100
    X = np.random.randn(n_samples, 4)

    df = pd.DataFrame(X, columns=["feature_1", "feature_2", "feature_3", "feature_4"])
    return df


@pytest.fixture
def algorithm_specs_path():
    """Path to algorithm YAML specs."""
    return Path(__file__).parent.parent / "algorithms"


@pytest.fixture
def sample_params_regression():
    """Default parameters for regression algorithms."""
    return {"test_size": 0.2}


@pytest.fixture
def sample_params_classification():
    """Default parameters for classification algorithms."""
    return {"test_size": 0.2}


@pytest.fixture
def sample_params_clustering():
    """Default parameters for clustering algorithms."""
    return {"n_clusters": 3, "random_state": 42}
