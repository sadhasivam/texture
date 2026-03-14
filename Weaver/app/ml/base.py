from abc import ABC, abstractmethod

import pandas as pd

from app.schemas.algorithm import AlgorithmMetadata


class AlgorithmAdapter(ABC):
    id: str
    name: str
    category: str

    @abstractmethod
    def get_metadata(self) -> AlgorithmMetadata:
        """Return full algorithm metadata for UI rendering."""
        pass

    @abstractmethod
    def validate_mapping(
        self,
        schema: list[dict],
        target: str,
        features: list[str],
        parameters: dict,
    ) -> list[str]:
        """Validate column mapping and parameters. Return list of error messages."""
        pass

    @abstractmethod
    def run(
        self,
        dataframe: pd.DataFrame,
        target: str,
        features: list[str],
        parameters: dict,
    ) -> dict:
        """
        Execute the algorithm and return results.

        Returns dict with:
        - summary: dict with train/test split info
        - metrics: dict of metric name to value
        - charts: list of chart data
        - tables: list of table data
        - explanations: list of plain-language explanations
        - warnings: list of warnings
        """
        pass
