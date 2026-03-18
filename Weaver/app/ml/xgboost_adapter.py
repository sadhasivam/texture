"""XGBoost algorithm adapter."""

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
from xgboost import XGBClassifier, XGBRegressor

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class XGBoostAdapter(AlgorithmAdapter):
    id = "xgboost"
    name = "XGBoost"
    category = "both"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            group="supervised",
            subgroup="both",
            description="Extreme Gradient Boosting - highly optimized gradient boosting implementation.",
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
                    label="Number of boosting rounds",
                ),
                AlgorithmParameter(
                    name="learning_rate",
                    type="float",
                    default=0.1,
                    label="Learning rate (eta)",
                ),
                AlgorithmParameter(
                    name="max_depth",
                    type="int",
                    default=6,
                    label="Maximum depth of trees",
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

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        test_size = parameters.get("test_size", 0.2)
        n_estimators = parameters.get("n_estimators", 100)
        learning_rate = parameters.get("learning_rate", 0.1)
        max_depth = parameters.get("max_depth", 6)

        # Prepare data
        X = dataframe[features]
        y = dataframe[target]

        # Drop rows with missing values
        valid_mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_mask]
        y = y[valid_mask]

        # Determine if regression or classification
        is_regression = pd.api.types.is_numeric_dtype(y)

        # Split data
        if is_regression:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            model = XGBRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                max_depth=max_depth,
                random_state=42,
                verbosity=0,
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            model = XGBClassifier(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                max_depth=max_depth,
                random_state=42,
                verbosity=0,
            )

        # Train
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)

        # Feature importance
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

            # Predicted vs actual
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
                f"XGBoost trained {n_estimators} trees using gradient boosting.",
                f"The model explains {r2*100:.1f}% of the variation in the target.",
                "XGBoost is highly optimized and often outperforms other algorithms.",
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

            # Class distribution
            class_dist = y.value_counts()
            class_distribution_data = [
                {"class": str(cls), "count": int(count)}
                for cls, count in class_dist.items()
            ]

            charts = [
                {
                    "type": "feature_importance",
                    "title": "Feature Importance",
                    "data": importance_data,
                },
                {
                    "type": "class_distribution",
                    "title": "Class Distribution",
                    "data": class_distribution_data,
                },
            ]

            explanations = [
                f"XGBoost achieved {accuracy*100:.1f}% accuracy on the test set.",
                "XGBoost handles imbalanced data and missing values well.",
                "Often used in Kaggle competitions due to high performance.",
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
                "n_estimators": n_estimators,
            },
            "metrics": metrics,
            "charts": charts,
            "tables": tables,
            "explanations": explanations,
            "warnings": warnings,
        }
