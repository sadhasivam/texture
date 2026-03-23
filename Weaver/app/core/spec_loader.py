"""Kubernetes-style YAML spec loader for algorithms."""

from pathlib import Path
from typing import Any

import yaml


class SpecLoader:
    """Load and parse algorithm YAML specifications."""

    def __init__(self, base_path: str | None = None):
        if base_path is None:
            # Auto-discover: algorithms dir is at texture root (sibling to Weaver/)
            # __file__ is in Weaver/app/core/spec_loader.py
            # Weaver dir is 2 levels up: ../../
            # Texture root is 3 levels up: ../../../
            current_file = Path(__file__).resolve()
            weaver_root = current_file.parent.parent.parent
            texture_root = weaver_root.parent
            base_path = str(texture_root / "algorithms")

        self.base_path = Path(base_path)
        self._cache: dict[str, dict[str, Any]] = {}

    def load_algorithm(self, spec_path: str) -> dict[str, Any]:
        """Load an algorithm spec from YAML file."""
        full_path = self.base_path / spec_path

        if not full_path.exists():
            raise FileNotFoundError(f"Algorithm spec not found: {full_path}")

        # Check cache
        cache_key = str(full_path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        with open(full_path) as f:
            spec = yaml.safe_load(f)

        # Validate kind
        if spec.get("kind") != "Algorithm":
            raise ValueError(f"Expected kind 'Algorithm', got: {spec.get('kind')}")

        # Resolve references
        if "ontologyRef" in spec.get("spec", {}):
            spec["ontology"] = self._load_ontology(spec["spec"]["ontologyRef"])

        if "dependencyRef" in spec.get("spec", {}):
            spec["dependencies"] = self._load_dependencies(spec["spec"]["dependencyRef"])

        # Cache and return
        self._cache[cache_key] = spec
        return spec

    def _load_ontology(self, ref_path: str) -> dict[str, Any]:
        """Load ontology spec."""
        full_path = self.base_path / ref_path

        if not full_path.exists():
            raise FileNotFoundError(f"Ontology spec not found: {full_path}")

        with open(full_path) as f:
            ontology = yaml.safe_load(f)

        if ontology.get("kind") != "Ontology":
            raise ValueError(f"Expected kind 'Ontology', got: {ontology.get('kind')}")

        return ontology

    def _load_dependencies(self, ref_path: str) -> dict[str, Any]:
        """Load dependencies spec."""
        full_path = self.base_path / ref_path

        if not full_path.exists():
            raise FileNotFoundError(f"Dependencies spec not found: {full_path}")

        with open(full_path) as f:
            deps = yaml.safe_load(f)

        if deps.get("kind") != "Dependencies":
            raise ValueError(f"Expected kind 'Dependencies', got: {deps.get('kind')}")

        return deps

    def discover_algorithms(self) -> list[str]:
        """Discover all algorithm specs in the base path."""
        algorithm_specs = []

        # Search supervised and unsupervised directories
        for category_dir in ["supervised", "unsupervised"]:
            category_path = self.base_path / category_dir
            if category_path.exists():
                for yaml_file in category_path.glob("*.yaml"):
                    # Load and verify it's an Algorithm kind
                    try:
                        with open(yaml_file) as f:
                            spec = yaml.safe_load(f)
                        if spec.get("kind") == "Algorithm":
                            # Store relative path
                            rel_path = yaml_file.relative_to(self.base_path)
                            algorithm_specs.append(str(rel_path))
                    except Exception:
                        # Skip invalid files
                        continue

        return algorithm_specs


# Global loader instance
spec_loader = SpecLoader()
