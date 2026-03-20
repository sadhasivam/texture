"""Spec-driven algorithm adapter that builds metadata from YAML."""
from typing import Any

import pandas as pd

from app.core.spec_loader import spec_loader
from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import (
    AlgorithmFeatures,
    AlgorithmMetadata,
    AlgorithmOutputs,
    AlgorithmParameter,
    AlgorithmTarget,
)


class SpecDrivenAdapter(AlgorithmAdapter):
    """
    Base adapter that loads metadata from YAML spec.

    Subclasses only need to implement:
    - __init__: Set spec_path
    - run: ML execution logic
    """

    spec_path: str  # Path to algorithm YAML spec (e.g., "supervised/linear-regression.yaml")
    _spec: dict[str, Any] | None = None

    def __init__(self):
        if not hasattr(self, "spec_path"):
            raise ValueError(
                f"{self.__class__.__name__} must set 'spec_path' attribute"
            )
        # Load spec on initialization
        self._load_spec()

    def _load_spec(self) -> None:
        """Load algorithm spec from YAML."""
        self._spec = spec_loader.load_algorithm(self.spec_path)
        spec_data = self._spec["spec"]

        # Set adapter attributes from spec
        self.id = spec_data["id"]
        self.name = self._spec["metadata"]["displayName"]
        self.category = self._spec["metadata"]["labels"]["category"]

    def get_metadata(self) -> AlgorithmMetadata:
        """Build metadata from YAML spec."""
        if not self._spec:
            self._load_spec()

        metadata = self._spec["metadata"]
        spec = self._spec["spec"]
        ontology = self._spec.get("ontology", {}).get("spec", {})

        # Build target config
        target_spec = spec["target"]
        target = AlgorithmTarget(
            required=target_spec["required"],
            allowed_types=target_spec["types"],
            cardinality=target_spec["cardinality"],
        )

        # Build features config
        features_spec = spec["features"]
        features = AlgorithmFeatures(
            required=features_spec["required"],
            min_columns=features_spec["min"],
            max_columns=features_spec["max"],
            allowed_types=features_spec["types"],
        )

        # Build parameters
        parameters = [
            AlgorithmParameter(
                name=param["name"],
                type=param["type"],
                default=param["default"],
                label=param.get("label", param["name"]),
            )
            for param in spec.get("parameters", [])
        ]

        # Build outputs
        output_spec = spec["outputs"]
        outputs = AlgorithmOutputs(
            metrics=[m["name"] for m in output_spec.get("metrics", [])],
            charts=[v["name"] for v in output_spec.get("visualizations", [])],
            tables=[t["name"] for t in output_spec.get("tables", [])],
        )

        # Build validation rules (convert from spec format to strings)
        validation_rules = spec.get("validationRules", [])

        # Get ontology data if available
        classification = ontology.get("classification", {})

        return AlgorithmMetadata(
            id=spec["id"],
            name=metadata["displayName"],
            category=metadata["labels"]["category"],
            group=classification.get("group", metadata["labels"].get("category")),
            subgroup=classification.get(
                "subgroup", metadata["labels"].get("category")
            ),
            description=spec["description"],
            tags=spec.get("tags", []),
            difficulty=spec.get("difficulty", "beginner"),
            model_family=spec.get("modelFamily", "unknown"),
            target=target,
            features=features,
            parameters=parameters,
            outputs=outputs,
            validation_rules=validation_rules,
        )

    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        """Must be implemented by subclass."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run() method"
        )
