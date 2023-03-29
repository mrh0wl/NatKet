from fastapi import APIRouter

from api.endpoints import (game_router, genre_router, keyword_router,
                           language_router, platform_router,
                           player_perspective_router, theme_router)

router = APIRouter()

router.include_router(game_router)
router.include_router(player_perspective_router)
router.include_router(genre_router)
router.include_router(keyword_router)
router.include_router(theme_router)
router.include_router(platform_router)
router.include_router(language_router)
