from fastapi import APIRouter

from memorycore.api.schemas import HealthResponse

VERSION = "0.1.0"

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """CHeck if everything is working"""
    return HealthResponse(status="ok", version=VERSION)