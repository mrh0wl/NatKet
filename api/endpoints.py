from typing import Any, List

from fastapi import APIRouter

from api.models import Game
from api.schemas import GameOut
from main.exceptions import LimitException

router = APIRouter()


@router.get("/", response_model=List[GameOut], include_in_schema=False)
@router.get("", response_model=List[GameOut])
def get_games(offset: int = 0, limit: int = 10) -> Any:
    """
        Endpoint to get all games based on offset and limit values.
    """
    if limit < 1 or limit > 20:
        raise LimitException(limit=limit)
    query = Game.objects.select_related('cover').prefetch_related(
        'tags', 'themes', 'keywords', 'genres', 'release_dates', 'age_ratings').all()[offset: offset + limit]
    return GameOut.from_django(query, many=True)


@router.get("/{slug:str}", response_model=GameOut)
def get_game(slug: str) -> Any:
    """
        Endpoint to get specific game
    """
    query = Game.objects.prefetch_related(
        'tags', 'themes', 'keywords', 'genres', 'release_dates', 'age_ratings').get(slug=slug)
    return GameOut.from_django(query)
