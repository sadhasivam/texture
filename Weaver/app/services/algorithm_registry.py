from app.ml.base import AlgorithmAdapter
from app.schemas.algorithm import AlgorithmMetadata, AlgorithmSummary


class AlgorithmRegistry:
    def __init__(self):
        self._algorithms: dict[str, AlgorithmAdapter] = {}

    def register(self, adapter: AlgorithmAdapter) -> None:
        """Register an algorithm adapter."""
        self._algorithms[adapter.id] = adapter

    def get_all_summaries(self) -> list[AlgorithmSummary]:
        """Get summary list of all algorithms."""
        summaries = []
        for adapter in self._algorithms.values():
            metadata = adapter.get_metadata()
            summaries.append(
                AlgorithmSummary(
                    id=metadata.id,
                    name=metadata.name,
                    category=metadata.category,
                    description=metadata.description,
                )
            )
        return summaries

    def get_metadata(self, algorithm_id: str) -> AlgorithmMetadata | None:
        """Get full metadata for a specific algorithm."""
        adapter = self._algorithms.get(algorithm_id)
        if adapter:
            return adapter.get_metadata()
        return None

    def get_adapter(self, algorithm_id: str) -> AlgorithmAdapter | None:
        """Get algorithm adapter by ID."""
        return self._algorithms.get(algorithm_id)


# Global registry instance
registry = AlgorithmRegistry()
