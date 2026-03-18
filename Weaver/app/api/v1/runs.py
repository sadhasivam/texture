from fastapi import APIRouter, HTTPException

from app.schemas.run import RunRequest, RunResponse
from app.services.run_service import run_service

router = APIRouter()


@router.post("", response_model=RunResponse)
async def create_run(request: RunRequest):
    """Execute an algorithm run."""
    try:
        response = await run_service.execute_run(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Run execution failed: {str(e)}") from e


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str):
    """Get run result by ID."""
    run_result = run_service.get_run(run_id)
    if not run_result:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return run_result
