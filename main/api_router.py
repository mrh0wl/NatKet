from fastapi import APIRouter

from api.endpoints import game_router, genre_router, platform_router, age_rating_router

router = APIRouter()

router.include_router(game_router, prefix="/games", tags=["Games"])
router.include_router(genre_router, prefix="/genres", tags=['Genres'])
router.include_router(platform_router, prefix="/platforms", tags=['Platforms'])
router.include_router(age_rating_router, prefix="/age-ratings", tags=['Age Rating'])
