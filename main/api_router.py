from fastapi import APIRouter

from api.endpoints import (game_router, genre_router, keyword_router,
                           language_router, platform_router,
                           player_perspective_router, theme_router)

router = APIRouter()

router.include_router(game_router, prefix="/games", tags=["Games"])
router.include_router(player_perspective_router, prefix="/player-perspectives", tags=['Player Perspectives'])
router.include_router(genre_router, prefix="/genres", tags=['Genres'])
router.include_router(keyword_router, prefix="/keywords", tags=['Keywords'])
router.include_router(theme_router, prefix="/themes", tags=['Themes'])
router.include_router(platform_router, prefix="/platforms", tags=['Platforms'])
router.include_router(language_router, prefix="/languages", tags=['Languages'])
