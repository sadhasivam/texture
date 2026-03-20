# Texture Algorithm Tests

TDD test suite for all ML algorithms in the Texture framework.

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_supervised_algorithms.py -v

# Run specific test class
uv run pytest tests/test_supervised_algorithms.py::TestLinearRegression -v

# Run with coverage
uv run pytest tests/ --cov=app/ml --cov=app/services --cov-report=html

# Run only fast tests (skip slow algorithms like t-SNE)
uv run pytest tests/ -m "not slow"
```

## Test Structure

### `conftest.py`
Shared fixtures for all tests:
- `sample_regression_data`: 100-row dataset for regression algorithms
- `sample_classification_data`: 100-row binary classification dataset
- `sample_multiclass_data`: 150-row multiclass classification dataset
- `sample_clustering_data`: 100-row unlabeled dataset for clustering
- Default parameter fixtures for each algorithm type

### `test_supervised_algorithms.py`
Tests for 10 supervised learning algorithms:
- Linear Regression
- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosting
- Naive Bayes
- SVM
- KNN
- AdaBoost
- XGBoost

Each algorithm class tests:
1. **Validation** - Correct/incorrect column mappings
2. **Metrics** - Required metrics are produced
3. **Visualizations** - Expected charts are generated
4. **Tables** - Output tables match spec
5. **Parameters** - Custom parameters work correctly

### `test_unsupervised_algorithms.py`
Tests for 5 unsupervised learning algorithms:
- K-Means Clustering
- DBSCAN
- PCA (Principal Component Analysis)
- t-SNE
- Isolation Forest

Plus tests for:
- Algorithm Registry loading all 15 algorithms from YAML specs
- Metadata structure validation
- Spec-driven contract enforcement

## Writing New Tests

When adding a new algorithm:

1. Add YAML spec to `algorithms/supervised/` or `algorithms/unsupervised/`
2. Implement adapter in `app/ml/supervised/` or `app/ml/unsupervised/`
3. Add test class following existing patterns:

```python
class TestNewAlgorithm:
    """Tests for New Algorithm."""

    @pytest.fixture
    def algorithm(self):
        """Load algorithm from global registry."""
        return registry.get_adapter("new_algorithm")

    def test_validation(self, algorithm):
        """Test validation logic."""
        # Test correct mapping passes
        # Test incorrect mapping fails

    def test_produces_required_outputs(self, algorithm, sample_data):
        """Test algorithm produces all required outputs."""
        result = algorithm.run(sample_data, "target", ["features"], {})
        assert "metrics" in result
        assert "charts" in result
```

## Test Philosophy

- **Spec-driven**: Tests validate the YAML spec contract
- **Black-box**: Test public interface, not internals
- **Fast**: Use small synthetic datasets (100 rows)
- **Comprehensive**: Cover validation, execution, and outputs
- **Maintainable**: DRY principle with shared fixtures

## Coverage Goals

- **Algorithm adapters**: 90%+ coverage
- **Registry**: 100% coverage
- **Service layer**: 85%+ coverage
