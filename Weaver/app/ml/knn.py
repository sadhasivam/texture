import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import StandardScaler

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class KNNAdapter(AlgorithmAdapter):
    id = "knn"
    name = "K-Nearest Neighbors"
    category = "both"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            description="Classifies or predicts based on the k closest data points in feature space.",
            target=AlgorithmTarget(
                required=True,
                allowed_types=["numeric", "categorical", "boolean"],
                cardinality="single",
            ),
            features=AlgorithmFeatures(
                required=True,
                min_columns=1,
                max_columns=None,
                allowed_types=["numeric"],
            ),
            parameters=[
                AlgorithmParameter(
                    name="test_size",
                    type="float",
                    default=0.2,
                    label="Test size",
                ),
                AlgorithmParameter(
                    name="n_neighbors",
                    type="int",
                    default=5,
                    label="Number of neighbors (k)",
                ),
                AlgorithmParameter(
                    name="weights",
                    type="select",
                    default="uniform",
                    label="Weight function",
                    options=["uniform", "distance"],
                ),
            ],
            outputs=AlgorithmOutputs(
                metrics=["varies by task type"],
                charts=["varies by task type"],
                tables=["performance_summary"],
            ),
            validation_rules=[
                "Target can be numeric, categorical, or boolean",
                "At least one feature column is required",
                "All features must be numeric",
                "Features are automatically scaled for KNN",
            ],
        )

    def validate_mapping(
        self,
        schema: list[dict],
        target: str,
        features: list[str],
        parameters: dict,
    ) -> list[str]:
        errors = []

        # Create column type lookup
        col_types = {col["name"]: col["inferred_type"] for col in schema}

        # Validate target exists
        if target not in col_types:
            errors.append(f"Target column '{target}' not found in dataset")
            return errors

        # Validate target type
        if col_types[target] not in ["numeric", "categorical", "boolean"]:
            errors.append(
                f"Target column '{target}' must be numeric, categorical, or boolean"
            )

        # Validate features exist
        for feature in features:
            if feature not in col_types:
                errors.append(f"Feature column '{feature}' not found in dataset")

        # Validate features are numeric
        for feature in features:
            if feature in col_types and col_types[feature] != "numeric":
                errors.append(f"Feature column '{feature}' must be numeric")

        # Validate target not in features
        if target in features:
            errors.append("Target column cannot also be a feature")

        # Validate at least one feature
        if len(features) == 0:
            errors.append("At least one feature column is required")

        # Validate test_size parameter
        test_size = parameters.get("test_size", 0.2)
        if not isinstance(test_size, (int, float)) or test_size <= 0 or test_size >= 1:
            errors.append("test_size must be between 0 and 1")

        # Validate n_neighbors parameter
        n_neighbors = parameters.get("n_neighbors", 5)
        if not isinstance(n_neighbors, int) or n_neighbors < 1:
            errors.append("n_neighbors must be a positive integer")

        # Validate weights parameter
        weights = parameters.get("weights", "uniform")
        if weights not in ["uniform", "distance"]:
            errors.append("weights must be 'uniform' or 'distance'")

        return errors

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        test_size = parameters.get("test_size", 0.2)
        n_neighbors = parameters.get("n_neighbors", 5)
        weights = parameters.get("weights", "uniform")

        # Prepare data
        X = dataframe[features]
        y = dataframe[target]

        # Drop rows with missing values
        valid_mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_mask]
        y = y[valid_mask]

        # Determine if this is regression or classification
        is_regression = pd.api.types.is_numeric_dtype(y)

        # Scale features (important for distance-based algorithms)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Split data
        if is_regression:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=42
            )
            model = KNeighborsRegressor(n_neighbors=n_neighbors, weights=weights)
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=42, stratify=y
            )
            model = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights)

        # Train model (KNN just stores the data)
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        if is_regression:
            # Regression metrics
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)

            metrics = {
                "r2": float(r2),
                "mae": float(mae),
                "rmse": float(rmse),
            }

            # Prepare predicted vs actual chart data with best fit line
            combined = list(zip(y_test.values, y_pred))
            combined.sort(key=lambda x: x[0])

            y_test_sorted = np.array([x[0] for x in combined])
            y_pred_sorted = np.array([x[1] for x in combined])

            # Calculate best fit trend line
            indices = np.arange(len(y_test_sorted))
            trend_coef = np.polyfit(indices, y_test_sorted, 1)
            best_fit_values = np.polyval(trend_coef, indices)

            predicted_vs_actual_data = []
            for idx, (actual, pred, fit) in enumerate(
                zip(y_test_sorted, y_pred_sorted, best_fit_values)
            ):
                predicted_vs_actual_data.append(
                    {"actual": float(actual), "predicted": float(pred), "best_fit": float(fit)}
                )

            charts = [
                {
                    "type": "predicted_vs_actual",
                    "title": "Predicted vs Actual",
                    "data": predicted_vs_actual_data,
                },
            ]

            explanations = [
                f"The model explains about {r2*100:.1f}% of the variation in the target.",
                f"On average, predictions are off by {mae:.2f} units (MAE).",
                f"KNN uses the {n_neighbors} nearest neighbors to predict values.",
                f"Weight function: {weights}",
            ]

            tables = [
                {
                    "type": "performance_summary",
                    "rows": [
                        {"metric": "K (neighbors)", "value": str(n_neighbors)},
                        {"metric": "Weight function", "value": weights},
                    ],
                }
            ]

        else:
            # Classification metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(
                y_test, y_pred, average="weighted", zero_division=0
            )
            recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

            metrics = {
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            }

            # Build confusion matrix data
            classes = sorted(y.unique())
            confusion_matrix_data = []
            for true_class in classes:
                for pred_class in classes:
                    count = ((y_test == true_class) & (y_pred == pred_class)).sum()
                    confusion_matrix_data.append(
                        {
                            "true": str(true_class),
                            "predicted": str(pred_class),
                            "count": int(count),
                        }
                    )

            # Class distribution
            class_dist = y.value_counts()
            class_distribution_data = [
                {"class": str(cls), "count": int(count)} for cls, count in class_dist.items()
            ]

            charts = [
                {
                    "type": "confusion_matrix",
                    "title": "Confusion Matrix",
                    "data": confusion_matrix_data,
                },
                {
                    "type": "class_distribution",
                    "title": "Class Distribution",
                    "data": class_distribution_data,
                },
            ]

            explanations = [
                f"The model achieved {accuracy*100:.1f}% accuracy on the test set.",
                f"KNN uses the {n_neighbors} nearest neighbors to classify each point.",
                f"Weight function: {weights} (distance gives closer neighbors more influence).",
                "KNN is a lazy learner - it stores all training data and decides at prediction time.",
            ]

            tables = [
                {
                    "type": "performance_summary",
                    "rows": [
                        {"metric": "K (neighbors)", "value": str(n_neighbors)},
                        {"metric": "Weight function", "value": weights},
                    ],
                }
            ]

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(f"Dropped {dropped} rows with missing values before training.")

        warnings.append("Features were automatically scaled using StandardScaler for KNN.")

        return {
            "summary": {
                "target_column": target,
                "feature_columns": features,
                "train_rows": len(X_train),
                "test_rows": len(X_test),
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
