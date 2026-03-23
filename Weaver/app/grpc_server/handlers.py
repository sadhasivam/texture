"""gRPC service handlers for Weaver."""

import io
import sys
from typing import Any

import grpc
import pandas as pd

from app.pb import common_pb2, weaver_pb2, weaver_pb2_grpc
from app.services.spec_registry import spec_registry


class WeaverServiceHandler(weaver_pb2_grpc.WeaverServiceServicer):
    """Implementation of WeaverService gRPC service."""

    def HealthCheck(self, request, context):
        """Health check endpoint."""
        algorithms = [algo.id for algo in spec_registry.get_all_summaries()]

        return weaver_pb2.HealthResponse(
            status="ok",
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            available_algorithms=algorithms,
        )

    def InferSchema(self, request, context):
        """Infer schema from CSV data."""
        try:
            # Parse CSV data
            try:
                df = pd.read_csv(io.BytesIO(request.dataset_csv))
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Invalid CSV data: {str(e)}")
                return weaver_pb2.InferSchemaResponse()

            # Infer column schemas
            columns = []
            for col_name in df.columns:
                col_data = df[col_name]

                # Infer type
                inferred_type = self._infer_column_type(col_data)

                # Get stats
                missing_count = int(col_data.isna().sum())
                unique_count = int(col_data.nunique())

                # Get sample values (non-null, first 3)
                sample_values = [str(val) for val in col_data.dropna().head(3).tolist()]

                columns.append(
                    weaver_pb2.ColumnSchema(
                        name=col_name,
                        inferred_type=inferred_type,
                        missing_count=missing_count,
                        unique_count=unique_count,
                        sample_values=sample_values,
                    )
                )

            # Get preview rows (first 5 rows)
            preview_rows = []
            for _, row in df.head(5).iterrows():
                cells = {col: str(val) for col, val in row.items()}
                preview_rows.append(weaver_pb2.PreviewRow(cells=cells))

            return weaver_pb2.InferSchemaResponse(
                dataset_id=request.dataset_id,
                filename="uploaded.csv",
                row_count=len(df),
                column_count=len(df.columns),
                columns=columns,
                preview_rows=preview_rows,
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return weaver_pb2.InferSchemaResponse()

    def _infer_column_type(self, col_data: pd.Series) -> str:
        """Infer the type of a column."""
        # Drop NaN values for type inference
        col_data = col_data.dropna()

        if len(col_data) == 0:
            return "unknown"

        # Check if numeric
        if pd.api.types.is_numeric_dtype(col_data):
            # Check if integer
            if pd.api.types.is_integer_dtype(col_data):
                # Check if looks like an identifier (high cardinality)
                if col_data.nunique() / len(col_data) > 0.95:
                    return "identifier"
                return "numeric"
            return "numeric"

        # Check if boolean
        if pd.api.types.is_bool_dtype(col_data):
            return "boolean"

        # Check if datetime
        try:
            pd.to_datetime(col_data.head(10))
            return "datetime"
        except:
            pass

        # Check if categorical (low cardinality)
        unique_ratio = col_data.nunique() / len(col_data)
        if unique_ratio < 0.05:
            return "categorical"

        # Default to text
        return "text"

    def ValidateRun(self, request, context):
        """Validate if a run can be executed."""
        try:
            # Get algorithm adapter
            adapter = spec_registry.get_adapter(request.algorithm_id)
            if not adapter:
                return weaver_pb2.ValidateRunResponse(
                    is_valid=False,
                    errors=[f"Algorithm '{request.algorithm_id}' not found"],
                )

            # Build column schema
            columns = [
                {"name": name, "inferred_type": col_type}
                for name, col_type in zip(request.column_names, request.column_types)
            ]

            # Convert parameters
            parameters = dict(request.parameters)

            # Validate mapping
            errors = adapter.validate_mapping(
                columns=columns,
                target_column=request.target_column if request.target_column else None,
                feature_columns=list(request.feature_columns),
                parameters=parameters,
            )

            return weaver_pb2.ValidateRunResponse(
                is_valid=len(errors) == 0,
                errors=errors,
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return weaver_pb2.ValidateRunResponse(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
            )

    def ExecuteRun(self, request, context):
        """Execute an algorithm run."""
        try:
            # Get algorithm adapter
            adapter = spec_registry.get_adapter(request.algorithm_id)
            if not adapter:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Algorithm '{request.algorithm_id}' not found")
                return weaver_pb2.ExecuteRunResponse(
                    status="error",
                    error_message=f"Algorithm '{request.algorithm_id}' not found",
                )

            # Parse CSV data
            try:
                df = pd.read_csv(io.BytesIO(request.dataset_csv))
            except Exception as e:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Invalid CSV data: {str(e)}")
                return weaver_pb2.ExecuteRunResponse(
                    status="error",
                    error_message=f"Invalid CSV data: {str(e)}",
                )

            # Convert parameters
            parameters = dict(request.parameters)

            # Execute algorithm - use correct parameter names for adapter interface
            result = adapter.run(
                dataframe=df,
                target=request.target_column if request.target_column else None,
                features=list(request.feature_columns),
                parameters=parameters,
            )

            # Convert result to protobuf
            response = self._convert_result_to_proto(result, request)
            return response

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return weaver_pb2.ExecuteRunResponse(
                status="error",
                error_message=f"Execution failed: {str(e)}",
            )

    def _convert_result_to_proto(
        self, result: dict[str, Any], request
    ) -> weaver_pb2.ExecuteRunResponse:
        """Convert algorithm result to protobuf message."""
        # Build summary
        summary = weaver_pb2.RunSummary(
            target_column=request.target_column,
            feature_columns=list(request.feature_columns),
            train_rows=result.get("summary", {}).get("train_rows", 0),
            test_rows=result.get("summary", {}).get("test_rows", 0),
            parameters=dict(request.parameters),
        )

        # Convert metrics
        metrics = {k: float(v) for k, v in result.get("metrics", {}).items()}

        # Convert charts
        charts = []
        for chart_data in result.get("charts", []):
            data_points = []
            for point in chart_data.get("data", []):
                data_point = common_pb2.DataPoint(
                    values={k: float(v) for k, v in point.items() if isinstance(v, (int, float))}
                )
                data_points.append(data_point)

            chart = common_pb2.Chart(
                type=chart_data.get("type", ""),
                title=chart_data.get("title", ""),
                data=data_points,
                options={k: str(v) for k, v in chart_data.get("options", {}).items()},
            )
            charts.append(chart)

        # Convert tables
        tables = []
        for table_data in result.get("tables", []):
            rows = []
            for row_data in table_data.get("rows", []):
                row = common_pb2.Row(cells={k: str(v) for k, v in row_data.items()})
                rows.append(row)

            table = common_pb2.Table(
                type=table_data.get("type", ""),
                columns=table_data.get("columns", []),
                rows=rows,
            )
            tables.append(table)

        return weaver_pb2.ExecuteRunResponse(
            status="success",
            summary=summary,
            metrics=metrics,
            charts=charts,
            tables=tables,
            explanations=result.get("explanations", []),
            warnings=result.get("warnings", []),
        )
