from pydantic import BaseModel


class RunRequest(BaseModel):
    algorithm_id: str
    dataset_id: str
    target_column: str
    feature_columns: list[str]
    parameters: dict[str, float | int | str | bool] = {}


class RunSummary(BaseModel):
    model_config = {"extra": "allow"}

    target_column: str | None = None
    feature_columns: list[str]
    train_rows: int | None = None
    test_rows: int | None = None


class ChartData(BaseModel):
    type: str
    title: str
    data: list[dict[str, str | int | float]]


class TableData(BaseModel):
    type: str
    rows: list[dict[str, str | int | float]]


class RunResponse(BaseModel):
    run_id: str
    status: str
    summary: RunSummary
    metrics: dict[str, float]
    charts: list[ChartData]
    tables: list[TableData]
    explanations: list[str]
    warnings: list[str]
