import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class LinearRegressionAdapter(AlgorithmAdapter):
    id = "linear_regression"
    name = "Linear Regression"
    category = "regression"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            description="Predicts a continuous numeric target from one or more features.",
            target=AlgorithmTarget(
                required=True,
                allowed_types=["numeric"],
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
                )
            ],
            outputs=AlgorithmOutputs(
                metrics=["r2", "mae", "rmse"],
                charts=["predicted_vs_actual", "residual_plot"],
                tables=["coefficients"],
            ),
            validation_rules=[
                "Target must be numeric",
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

        # Validate target is numeric
        if col_types[target] != "numeric":
            errors.append(f"Target column '{target}' must be numeric")

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

        return errors

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        test_size = parameters.get("test_size", 0.2)

        # Prepare data
        X = dataframe[features]
        y = dataframe[target]

        # Drop rows with missing values
        valid_mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_mask]
        y = y[valid_mask]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        # Prepare predicted vs actual chart data with best fit line
        # Create a combined dataset to sort together
        combined = list(zip(y_test.values, y_pred))
        # Sort by actual values to create smooth visualization
        combined.sort(key=lambda x: x[0])

        y_test_sorted = np.array([x[0] for x in combined])
        y_pred_sorted = np.array([x[1] for x in combined])

        # Calculate best fit trend line through the data
        indices = np.arange(len(y_test_sorted))
        trend_coef = np.polyfit(indices, y_test_sorted, 1)  # Linear trend through actual values
        best_fit_values = np.polyval(trend_coef, indices)

        predicted_vs_actual_data = []
        for idx, (actual, pred, fit) in enumerate(zip(y_test_sorted, y_pred_sorted, best_fit_values)):
            predicted_vs_actual_data.append({
                "actual": float(actual),
                "predicted": float(pred),
                "best_fit": float(fit)
            })

        # Prepare residual plot data
        residuals = y_test - y_pred
        residual_data = [
            {"predicted": float(pred), "residual": float(res)}
            for pred, res in zip(y_pred, residuals)
        ]

        # Prepare coefficients table
        coefficients_rows = [
            {"feature": feature, "coefficient": float(coef)}
            for feature, coef in zip(features, model.coef_)
        ]
        coefficients_rows.insert(
            0, {"feature": "intercept", "coefficient": float(model.intercept_)}
        )

        # Generate explanations
        explanations = [
            f"The model explains about {r2*100:.1f}% of the variation in the target.",
            f"On average, predictions are off by {mae:.2f} units (MAE).",
        ]

        if r2 < 0.5:
            explanations.append(
                "The R² score is relatively low, suggesting the features may not strongly predict the target."
            )

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
            "metrics": {
                "r2": float(r2),
                "mae": float(mae),
                "rmse": float(rmse),
            },
            "charts": [
                {
                    "type": "predicted_vs_actual",
                    "title": "Predicted vs Actual",
                    "data": predicted_vs_actual_data,
                },
                {
                    "type": "residual_plot",
                    "title": "Residual Plot",
                    "data": residual_data,
                },
            ],
            "tables": [
                {
                    "type": "coefficients",
                    "rows": coefficients_rows,
                }
            ],
            "explanations": explanations,
            "warnings": warnings,
        }
