from fastapi import APIRouter, HTTPException

from app.schemas.algorithm import AlgorithmMetadata, AlgorithmSummary
from app.services.spec_registry import spec_registry as registry

router = APIRouter()


@router.get("", response_model=list[AlgorithmSummary])
async def list_algorithms():
    """Get list of all available algorithms."""
    return registry.get_all_summaries()


@router.get("/{algorithm_id}", response_model=AlgorithmMetadata)
async def get_algorithm_metadata(algorithm_id: str):
    """Get full metadata for a specific algorithm."""
    metadata = registry.get_metadata(algorithm_id)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Algorithm '{algorithm_id}' not found")
    return metadata
