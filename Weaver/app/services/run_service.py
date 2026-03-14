import uuid

from app.schemas.run import RunRequest, RunResponse, RunSummary
from app.services.algorithm_registry import registry
from app.services.dataset_service import dataset_service


class RunService:
    def __init__(self):
        # In-memory storage for run results (no DB in V1)
        self._runs: dict[str, dict] = {}

    async def execute_run(self, request: RunRequest) -> RunResponse:
        """Execute an algorithm run."""
        # Get algorithm adapter
        adapter = registry.get_adapter(request.algorithm_id)
        if not adapter:
            raise ValueError(f"Algorithm '{request.algorithm_id}' not found")

        # Load dataset
        dataframe = dataset_service.load_dataframe(request.dataset_id)
        if dataframe is None:
            raise ValueError(f"Dataset '{request.dataset_id}' not found")

        # Get dataset schema
        schema = dataset_service.get_schema(request.dataset_id)
        if schema is None:
            raise ValueError(f"Schema for dataset '{request.dataset_id}' not found")

        # Validate mapping
        validation_errors = adapter.validate_mapping(
            schema,
            request.target_column,
            request.feature_columns,
            request.parameters,
        )

        if validation_errors:
            raise ValueError(f"Validation failed: {'; '.join(validation_errors)}")

        # Run algorithm
        try:
            result = adapter.run(
                dataframe,
                request.target_column,
                request.feature_columns,
                request.parameters,
            )
        except Exception as e:
            raise ValueError(f"Algorithm execution failed: {str(e)}")

        # Generate run ID
        run_id = f"run_{uuid.uuid4().hex[:8]}"

        # Build response
        from app.schemas.run import ChartData, TableData

        response = RunResponse(
            run_id=run_id,
            status="success",
            summary=RunSummary(**result["summary"]),
            metrics=result["metrics"],
            charts=[ChartData(**chart) for chart in result["charts"]],
            tables=[TableData(**table) for table in result["tables"]],
            explanations=result["explanations"],
            warnings=result["warnings"],
        )

        # Store run result
        self._runs[run_id] = response.model_dump()

        return response

    def get_run(self, run_id: str) -> RunResponse | None:
        """Retrieve run result by ID."""
        run_data = self._runs.get(run_id)
        if not run_data:
            return None
        return RunResponse(**run_data)


# Global service instance
run_service = RunService()
