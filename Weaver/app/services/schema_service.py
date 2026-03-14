import pandas as pd

from app.schemas.dataset import ColumnSchema


def infer_column_type(series: pd.Series) -> str:
    """Infer the type of a pandas Series."""
    # Check for boolean
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    # Check for numeric
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    # Check for datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # Check if it's a categorical-like column (low cardinality string)
    unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
    if unique_ratio < 0.05 and series.nunique() < 50:
        return "categorical"

    # Check for identifier-like patterns (high uniqueness)
    if unique_ratio > 0.95:
        return "identifier"

    # Default to text
    return "text"


def infer_schema(dataframe: pd.DataFrame) -> list[ColumnSchema]:
    """Infer schema for all columns in a DataFrame."""
    schema = []

    for column in dataframe.columns:
        series = dataframe[column]

        # Get basic stats
        missing_count = int(series.isna().sum())
        unique_count = int(series.nunique())

        # Infer type
        inferred_type = infer_column_type(series)

        # Get sample values (non-null)
        sample_values = series.dropna().head(3).tolist()

        # Convert numpy types to Python types for JSON serialization
        sample_values = [
            (
                int(val)
                if isinstance(val, (pd.Int64Dtype, pd.Int32Dtype))
                or (isinstance(val, (int, float)) and float(val).is_integer())
                else float(val)
                if isinstance(val, (float, pd.Float64Dtype))
                else str(val)
            )
            for val in sample_values
        ]

        schema.append(
            ColumnSchema(
                name=column,
                inferred_type=inferred_type,
                missing_count=missing_count,
                unique_count=unique_count,
                sample_values=sample_values,
            )
        )

    return schema
