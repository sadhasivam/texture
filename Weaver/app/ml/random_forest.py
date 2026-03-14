import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
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

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class RandomForestAdapter(AlgorithmAdapter):
    id = "random_forest"
    name = "Random Forest"
    category = "both"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            description="Builds an ensemble of decision trees for robust predictions.",
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
                    name="n_estimators",
                    type="int",
                    default=100,
                    label="Number of trees",
                ),
            ],
            outputs=AlgorithmOutputs(
                metrics=["varies by task type"],
                charts=["feature_importance"],
                tables=["performance_summary"],
            ),
            validation_rules=[
                "Target can be numeric, categorical, or boolean",
                "At least one feature column is required",
                "All features must be numeric",
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

        # Validate target is numeric, categorical, or boolean
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

        # Validate n_estimators parameter
        n_estimators = parameters.get("n_estimators", 100)
        if not isinstance(n_estimators, int) or n_estimators < 1:
            errors.append("n_estimators must be a positive integer")

        return errors

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        test_size = parameters.get("test_size", 0.2)
        n_estimators = parameters.get("n_estimators", 100)

        # Prepare data
        X = dataframe[features]
        y = dataframe[target]

        # Drop rows with missing values
        valid_mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_mask]
        y = y[valid_mask]

        # Determine if this is regression or classification
        is_regression = pd.api.types.is_numeric_dtype(y)

        # Split data
        if is_regression:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            model = RandomForestRegressor(
                n_estimators=n_estimators, random_state=42, n_jobs=-1
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            model = RandomForestClassifier(
                n_estimators=n_estimators, random_state=42, n_jobs=-1
            )

        # Train model
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Feature importance chart
        importance_data = [
            {"feature": feature, "importance": float(importance)}
            for feature, importance in zip(features, model.feature_importances_)
        ]
        importance_data.sort(key=lambda x: x["importance"], reverse=True)

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

            # Predicted vs actual chart
            predicted_vs_actual_data = [
                {"actual": float(actual), "predicted": float(pred)}
                for actual, pred in zip(y_test, y_pred)
            ]

            charts = [
                {
                    "type": "feature_importance",
                    "title": "Feature Importance",
                    "data": importance_data,
                },
                {
                    "type": "predicted_vs_actual",
                    "title": "Predicted vs Actual",
                    "data": predicted_vs_actual_data,
                },
            ]

            explanations = [
                f"The model explains about {r2*100:.1f}% of the variation in the target.",
                f"On average, predictions are off by {mae:.2f} units (MAE).",
                f"Random Forest combines {n_estimators} decision trees to reduce overfitting.",
            ]

            tables = [{"type": "performance_summary", "rows": []}]

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

            charts = [
                {
                    "type": "feature_importance",
                    "title": "Feature Importance",
                    "data": importance_data,
                },
                {
                    "type": "confusion_matrix",
                    "title": "Confusion Matrix",
                    "data": confusion_matrix_data,
                },
            ]

            explanations = [
                f"The model achieved {accuracy*100:.1f}% accuracy on the test set.",
                f"Random Forest combines {n_estimators} decision trees to improve robustness.",
                "Each tree votes on the final prediction, reducing variance.",
            ]

            tables = [{"type": "performance_summary", "rows": []}]

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(
                f"Dropped {dropped} rows with missing values before training."
            )

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
