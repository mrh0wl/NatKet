from api.endpoints import router as api_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(api_router, prefix="/games", tags=["Games"])
