import pandas as pd

from app.schemas.dataset import ColumnSchema


def infer_column_type(series: pd.Series) -> str:
    """Infer the type of a pandas Series."""
    # Drop NA values for analysis
    series_clean = series.dropna()

    if len(series_clean) == 0:
        return "text"

    # Check for boolean
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    # Check for datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # Check for numeric
    if pd.api.types.is_numeric_dtype(series):
        unique_count = series_clean.nunique()

        # Binary numeric columns (2 unique values) → categorical
        if unique_count == 2:
            return "categorical"

        # Low cardinality numeric columns (3-10 unique values) might be categorical
        if 3 <= unique_count <= 10:
            # Check if all values are integers
            if series_clean.apply(lambda x: float(x).is_integer()).all():
                max_val = series_clean.max()
                min_val = series_clean.min()
                value_range = max_val - min_val

                # Classify as categorical if:
                # 1. Small range (< 20) with low cardinality, OR
                # 2. Values look like class labels (0-9 or 1-10)
                if value_range < 20 or (min_val >= 0 and max_val < 10):
                    return "categorical"

        # Everything else is numeric
        return "numeric"

    # String/object types
    unique_ratio = series_clean.nunique() / len(series_clean)

    # Low cardinality strings → categorical
    if unique_ratio < 0.05 and series_clean.nunique() < 50:
        return "categorical"

    # Medium cardinality with few unique values → categorical
    if series_clean.nunique() <= 10:
        return "categorical"

    # High uniqueness → identifier
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

        col_schema = ColumnSchema(
            name=column,
            inferred_type=inferred_type,
            missing_count=missing_count,
            unique_count=unique_count,
            sample_values=sample_values,
        )
        schema.append(col_schema)

        # Debug logging
        print(
            f"Column: {column:20s} | Type: {inferred_type:12s} | "
            f"Unique: {unique_count:4d} | Samples: {sample_values}"
        )

    return schema
