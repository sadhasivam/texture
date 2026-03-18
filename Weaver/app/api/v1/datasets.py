from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.dataset import DatasetDetails, DatasetUploadResponse
from app.services.dataset_service import dataset_service

router = APIRouter()


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV dataset."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    # Read file content
    content = await file.read()

    try:
        response = await dataset_service.upload_dataset(file.filename, content)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process dataset: {str(e)}") from e


@router.get("/{dataset_id}", response_model=DatasetDetails)
async def get_dataset(dataset_id: str):
    """Get dataset details by ID."""
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")
    return dataset
