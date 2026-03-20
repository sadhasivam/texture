"""Spec-driven algorithm registry that loads from YAML.

This registry automatically discovers and loads algorithms from YAML specs,
eliminating the need to manually import and register each adapter.
"""
import importlib
from pathlib import Path

from app.core.spec_loader import spec_loader
from app.services.algorithm_registry import AlgorithmRegistry


class SpecDrivenRegistry(AlgorithmRegistry):
    """Registry that auto-loads algorithms from YAML specs."""

    def auto_discover_and_register(self):
        """
        Discover all algorithm YAML specs and register their adapters.

        This replaces manual registration in main.py.
        """
        print("Auto-discovering algorithms from YAML specs...")

        # Get all algorithm spec paths
        spec_paths = spec_loader.discover_algorithms()

        for spec_path in spec_paths:
            try:
                # Load spec
                spec = spec_loader.load_algorithm(spec_path)
                handler = spec["spec"]["handler"]

                # Dynamically import the adapter class
                module_name = handler["module"]
                class_name = handler["class"]

                # Import module
                module = importlib.import_module(module_name)

                # Get adapter class
                adapter_class = getattr(module, class_name)

                # Instantiate and register
                adapter = adapter_class()
                self.register(adapter)

                print(f"  ✓ Registered: {adapter.id} ({class_name})")

            except Exception as e:
                print(f"  ✗ Failed to load {spec_path}: {e}")

        print(f"Total algorithms registered: {len(self._algorithms)}")


# Global spec-driven registry
spec_registry = SpecDrivenRegistry()
