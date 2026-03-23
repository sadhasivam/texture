"""Spec-driven Logistic Regression - minimal boilerplate."""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from app.ml.spec_adapter import SpecDrivenAdapter


class LogisticRegressionAdapter(SpecDrivenAdapter):
    """ "Logistic Regression using YAML spec for metadata."""

    spec_path = "supervised/logistic-regression.yaml"

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        test_size = float(parameters.get("test_size", 0.2))

        # Prepare data
        X = dataframe[features]
        y = dataframe[target]

        # Drop rows with missing values
        valid_mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_mask]
        y = y[valid_mask]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Train model
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

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

        # Build class distribution data
        class_dist = y.value_counts()
        class_distribution_data = [
            {"class": str(cls), "count": int(count)} for cls, count in class_dist.items()
        ]

        # Build classification report
        report_rows = []
        for cls in classes:
            cls_mask = y_test == cls
            pred_mask = y_pred == cls
            tp = ((cls_mask) & (pred_mask)).sum()
            fp = ((~cls_mask) & (pred_mask)).sum()
            fn = ((cls_mask) & (~pred_mask)).sum()

            cls_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            cls_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            cls_f1 = (
                2 * cls_precision * cls_recall / (cls_precision + cls_recall)
                if (cls_precision + cls_recall) > 0
                else 0
            )

            report_rows.append(
                {
                    "class": str(cls),
                    "precision": float(cls_precision),
                    "recall": float(cls_recall),
                    "f1_score": float(cls_f1),
                    "support": int(cls_mask.sum()),
                }
            )

        # Generate explanations
        explanations = [
            f"The model achieved {accuracy * 100:.1f}% accuracy on the test set.",
            f"Overall F1-score is {f1:.3f}, balancing precision and recall.",
        ]

        if len(classes) == 2:
            explanations.append("This is a binary classification problem with two target classes.")
        else:
            explanations.append(
                f"This is a multi-class classification problem with {len(classes)} target classes."
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
                "accuracy": float(accuracy),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            },
            "charts": [
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
            ],
            "tables": [
                {
                    "type": "classification_report",
                    "rows": report_rows,
                }
            ],
            "explanations": explanations,
            "warnings": warnings,
        }
