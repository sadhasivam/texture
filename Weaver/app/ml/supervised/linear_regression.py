"""Spec-driven Linear Regression - minimal boilerplate."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from app.ml.spec_adapter import SpecDrivenAdapter


class LinearRegressionAdapter(SpecDrivenAdapter):
    """ "Linear Regression using YAML spec for metadata."""

    spec_path = "supervised/linear-regression.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        # Convert test_size from string to float if needed (gRPC sends strings)
        test_size_raw = float(parameters.get("test_size", 0.2))
        test_size = float(test_size_raw) if isinstance(test_size_raw, str) else test_size_raw

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
        for idx, (actual, pred, fit) in enumerate(
            zip(y_test_sorted, y_pred_sorted, best_fit_values)
        ):
            predicted_vs_actual_data.append(
                {"actual": float(actual), "predicted": float(pred), "best_fit": float(fit)}
            )

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
            f"The model explains about {r2 * 100:.1f}% of the variation in the target.",
            f"On average, predictions are off by {mae:.2f} units (MAE).",
        ]

        if r2 < 0.5:
            explanations.append(
                "The R² score is relatively low, suggesting the features may not strongly predict the target."
            )

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(f"Dropped {dropped} rows with missing values before training.")

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
