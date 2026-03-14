from pydantic import BaseModel


class ColumnSchema(BaseModel):
    name: str
    inferred_type: str
    missing_count: int
    unique_count: int
    sample_values: list[str | int | float]


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    row_count: int
    column_count: int
    columns: list[ColumnSchema]
    preview_rows: list[dict[str, str | int | float | None]]


class DatasetDetails(BaseModel):
    dataset_id: str
    filename: str
    row_count: int
    column_count: int
    columns: list[ColumnSchema]
    preview_rows: list[dict[str, str | int | float | None]]
