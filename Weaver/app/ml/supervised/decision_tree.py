"""Spec-driven Decision Tree - minimal boilerplate."""
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, precision_score, r2_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from app.ml.spec_adapter import SpecDrivenAdapter


class DecisionTreeAdapter(SpecDrivenAdapter):
    """"Decision Tree using YAML spec for metadata."""

    spec_path = "supervised/decision-tree.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        test_size = parameters.get("test_size", 0.2)
        max_depth = parameters.get("max_depth", 5)

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
            model = DecisionTreeRegressor(max_depth=max_depth, random_state=42)
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)

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
                "Decision trees split the data based on feature values to minimize error.",
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
                f"The model achieved {accuracy*100:.1f}% accuracy on the test set.",
                "Decision trees split the data based on feature values to maximize class purity.",
                f"The tree has a maximum depth of {max_depth} levels.",
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

