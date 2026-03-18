"""Metadata-driven validation for algorithm mappings."""

from app.schemas.algorithm import AlgorithmMetadata


class MetadataDrivenValidator:
    """Generic validator that uses algorithm metadata to validate mappings."""

    @staticmethod
    def validate(
        metadata: AlgorithmMetadata,
        schema: list[dict],
        target: str,
        features: list[str],
        parameters: dict,
    ) -> list[str]:
        """
        Validate algorithm mapping using metadata configuration.

        Args:
            metadata: Algorithm metadata with validation rules
            schema: Dataset schema (list of column definitions)
            target: Target column name
            features: List of feature column names
            parameters: Algorithm parameters

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Create column type lookup
        col_types = {col["name"]: col["inferred_type"] for col in schema}

        # Validate target
        errors.extend(
            MetadataDrivenValidator._validate_target(target, col_types, metadata)
        )

        # Validate features
        errors.extend(
            MetadataDrivenValidator._validate_features(
                features, col_types, target, metadata
            )
        )

        # Validate parameters
        errors.extend(
            MetadataDrivenValidator._validate_parameters(parameters, metadata)
        )

        return errors

    @staticmethod
    def _validate_target(
        target: str, col_types: dict[str, str], metadata: AlgorithmMetadata
    ) -> list[str]:
        """Validate target column based on metadata."""
        errors = []

        # Check if target exists
        if target not in col_types:
            errors.append(f"Target column '{target}' not found in dataset")
            return errors  # Can't continue validation without valid target

        # Check if target is required
        if metadata.target.required and not target:
            errors.append("Target column is required")

        # Check target type
        target_type = col_types[target]
        allowed_types = metadata.target.allowed_types

        if target_type not in allowed_types:
            if len(allowed_types) == 1:
                errors.append(
                    f"Target column '{target}' must be {allowed_types[0]}, "
                    f"but found {target_type}"
                )
            else:
                types_str = ", ".join(allowed_types)
                errors.append(
                    f"Target column '{target}' must be one of: {types_str}, "
                    f"but found {target_type}"
                )

        return errors

    @staticmethod
    def _validate_features(
        features: list[str],
        col_types: dict[str, str],
        target: str,
        metadata: AlgorithmMetadata,
    ) -> list[str]:
        """Validate feature columns based on metadata."""
        errors = []

        # Check if features are required
        if metadata.features.required and len(features) == 0:
            errors.append("At least one feature column is required")
            return errors

        # Check minimum feature count
        if (
            metadata.features.min_columns
            and len(features) < metadata.features.min_columns
        ):
            errors.append(
                f"At least {metadata.features.min_columns} feature column(s) required, "
                f"but only {len(features)} selected"
            )

        # Check maximum feature count
        if (
            metadata.features.max_columns
            and len(features) > metadata.features.max_columns
        ):
            errors.append(
                f"Maximum {metadata.features.max_columns} feature column(s) allowed, "
                f"but {len(features)} selected"
            )

        # Check if features exist
        for feature in features:
            if feature not in col_types:
                errors.append(f"Feature column '{feature}' not found in dataset")

        # Check feature types
        allowed_types = metadata.features.allowed_types
        for feature in features:
            if feature in col_types:
                feature_type = col_types[feature]
                if feature_type not in allowed_types:
                    if len(allowed_types) == 1:
                        errors.append(
                            f"Feature column '{feature}' must be {allowed_types[0]}, "
                            f"but found {feature_type}"
                        )
                    else:
                        types_str = ", ".join(allowed_types)
                        errors.append(
                            f"Feature column '{feature}' must be one of: {types_str}, "
                            f"but found {feature_type}"
                        )

        # Check target not in features
        if target in features:
            errors.append("Target column cannot also be a feature")

        return errors

    @staticmethod
    def _validate_parameters(
        parameters: dict, metadata: AlgorithmMetadata
    ) -> list[str]:
        """Validate algorithm parameters based on metadata."""
        errors = []

        # Validate each parameter defined in metadata
        for param_meta in metadata.parameters:
            param_name = param_meta.name
            param_value = parameters.get(param_name, param_meta.default)

            # Type validation
            if param_meta.type == "float":
                if not isinstance(param_value, (int, float)):
                    errors.append(
                        f"Parameter '{param_name}' must be a number, "
                        f"but got {type(param_value).__name__}"
                    )
                    continue

                # Range validation for test_size (common parameter)
                if param_name == "test_size":
                    if param_value <= 0 or param_value >= 1:
                        errors.append(
                            f"Parameter '{param_name}' must be between 0 and 1, "
                            f"but got {param_value}"
                        )

            elif param_meta.type == "int":
                if not isinstance(param_value, int):
                    errors.append(
                        f"Parameter '{param_name}' must be an integer, "
                        f"but got {type(param_value).__name__}"
                    )
                    continue

                # Range validation for common integer parameters
                if param_name in ["n_neighbors", "max_depth", "n_estimators"]:
                    if param_value <= 0:
                        errors.append(
                            f"Parameter '{param_name}' must be positive, "
                            f"but got {param_value}"
                        )

            elif param_meta.type == "string":
                if not isinstance(param_value, str):
                    errors.append(
                        f"Parameter '{param_name}' must be a string, "
                        f"but got {type(param_value).__name__}"
                    )

            elif param_meta.type == "select":
                # Validate that value is one of the allowed options
                if param_meta.options and param_value not in param_meta.options:
                    options_str = ", ".join(f"'{opt}'" for opt in param_meta.options)
                    errors.append(
                        f"Parameter '{param_name}' must be one of: {options_str}, "
                        f"but got '{param_value}'"
                    )

        return errors
