import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB

from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class NaiveBayesAdapter(AlgorithmAdapter):
    id = "naive_bayes"
    name = "Naive Bayes"
    category = "classification"

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            id=self.id,
            name=self.name,
            category=self.category,
            description="Probabilistic classifier based on Bayes' theorem with feature independence assumption.",
            target=AlgorithmTarget(
                required=True,
                allowed_types=["categorical", "boolean"],
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
                    name="variant",
                    type="select",
                    default="gaussian",
                    label="Naive Bayes variant",
                    options=["gaussian", "multinomial", "bernoulli"],
                ),
            ],
            outputs=AlgorithmOutputs(
                metrics=["accuracy", "precision", "recall", "f1"],
                charts=["confusion_matrix", "class_distribution"],
                tables=["classification_report"],
            ),
            validation_rules=[
                "Target must be categorical or boolean",
                "At least one feature column is required",
                "All features must be numeric",
                "Assumes features are independent (may not hold in reality)",
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

        # Validate target is categorical or boolean
        if col_types[target] not in ["categorical", "boolean"]:
            errors.append(f"Target column '{target}' must be categorical or boolean")

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

        # Validate variant parameter
        variant = parameters.get("variant", "gaussian")
        if variant not in ["gaussian", "multinomial", "bernoulli"]:
            errors.append("variant must be 'gaussian', 'multinomial', or 'bernoulli'")

        return errors

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        test_size = parameters.get("test_size", 0.2)
        variant = parameters.get("variant", "gaussian")

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

        # Select Naive Bayes variant
        if variant == "gaussian":
            model = GaussianNB()
            variant_desc = "Gaussian (assumes features follow normal distribution)"
        elif variant == "multinomial":
            # Ensure non-negative values for multinomial
            if (X_train < 0).any().any() or (X_test < 0).any().any():
                # Shift to make all values non-negative
                min_val = min(X_train.min().min(), X_test.min().min())
                if min_val < 0:
                    X_train = X_train - min_val
                    X_test = X_test - min_val
            model = MultinomialNB()
            variant_desc = "Multinomial (for count/frequency data)"
        else:  # bernoulli
            model = BernoulliNB()
            variant_desc = "Bernoulli (for binary features)"

        # Train model
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Get class probabilities if available
        try:
            y_proba = model.predict_proba(X_test)
            has_proba = True
        except Exception:
            has_proba = False

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
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
            f"The model achieved {accuracy*100:.1f}% accuracy on the test set.",
            f"Overall F1-score is {f1:.3f}, balancing precision and recall.",
            f"Variant: {variant_desc}",
            "Naive Bayes assumes features are independent given the class (may not be realistic).",
        ]

        if len(classes) == 2:
            explanations.append("This is a binary classification problem with two target classes.")
        else:
            explanations.append(
                f"This is a multi-class classification problem with {len(classes)} target classes."
            )

        if has_proba:
            avg_confidence = y_proba.max(axis=1).mean()
            explanations.append(
                f"Average prediction confidence: {avg_confidence*100:.1f}%"
            )

        warnings = []
        if len(X) < len(dataframe):
            dropped = len(dataframe) - len(X)
            warnings.append(f"Dropped {dropped} rows with missing values before training.")

        if variant == "multinomial" and (X < 0).any().any():
            warnings.append(
                "Features were shifted to non-negative values for Multinomial Naive Bayes."
            )

        return {
            "summary": {
                "target_column": target,
                "feature_columns": features,
                "train_rows": len(X_train),
                "test_rows": len(X_test),
            },
            "metrics": metrics,
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
