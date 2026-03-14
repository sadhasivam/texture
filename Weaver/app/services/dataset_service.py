import os
import uuid
from pathlib import Path

import pandas as pd

from app.core.config import settings
from app.schemas.dataset import DatasetDetails, DatasetUploadResponse
from app.services.schema_service import infer_schema


class DatasetService:
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        # In-memory storage for dataset metadata (no DB in V1)
        self._datasets: dict[str, dict] = {}

    async def upload_dataset(self, filename: str, file_content: bytes) -> DatasetUploadResponse:
        """Upload and process a CSV file."""
        # Generate unique dataset ID
        dataset_id = f"ds_{uuid.uuid4().hex[:8]}"

        # Save file to disk
        file_path = self.upload_dir / f"{dataset_id}.csv"
        file_path.write_bytes(file_content)

        # Read CSV
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            # Clean up file on error
            file_path.unlink()
            raise ValueError(f"Failed to parse CSV: {str(e)}")

        # Infer schema
        schema = infer_schema(df)

        # Get preview rows (first 10 rows)
        preview_rows = df.head(10).to_dict(orient="records")

        # Store metadata
        self._datasets[dataset_id] = {
            "dataset_id": dataset_id,
            "filename": filename,
            "file_path": str(file_path),
            "row_count": len(df),
            "column_count": len(df.columns),
            "schema": [col.model_dump() for col in schema],
            "preview_rows": preview_rows,
        }

        return DatasetUploadResponse(
            dataset_id=dataset_id,
            filename=filename,
            row_count=len(df),
            column_count=len(df.columns),
            columns=schema,
            preview_rows=preview_rows,
        )

    def get_dataset(self, dataset_id: str) -> DatasetDetails | None:
        """Retrieve dataset details by ID."""
        metadata = self._datasets.get(dataset_id)
        if not metadata:
            return None

        # Reconstruct schema objects
        from app.schemas.dataset import ColumnSchema

        schema = [ColumnSchema(**col) for col in metadata["schema"]]

        return DatasetDetails(
            dataset_id=metadata["dataset_id"],
            filename=metadata["filename"],
            row_count=metadata["row_count"],
            column_count=metadata["column_count"],
            columns=schema,
            preview_rows=metadata["preview_rows"],
        )

    def load_dataframe(self, dataset_id: str) -> pd.DataFrame | None:
        """Load the actual DataFrame for a dataset."""
        metadata = self._datasets.get(dataset_id)
        if not metadata:
            return None

        file_path = Path(metadata["file_path"])
        if not file_path.exists():
            return None

        return pd.read_csv(file_path)

    def get_schema(self, dataset_id: str) -> list[dict] | None:
        """Get schema for a dataset."""
        metadata = self._datasets.get(dataset_id)
        if not metadata:
            return None
        return metadata["schema"]


# Global service instance
dataset_service = DatasetService()
