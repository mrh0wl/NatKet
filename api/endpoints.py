from typing import Any, List, Optional

from fastapi import APIRouter

from api.models import Game, Platform, Genre, AgeRating
from api.schemas import GameOut, PlatformSchema, GenreSchema, ExceptionSchema, AgeRatingSchema
from main.exceptions import LimitException, SlugException

exception_responses = {
    400: {'model': ExceptionSchema},
    403: {'model': ExceptionSchema},
    422: {'model': ExceptionSchema}
}

game_router = APIRouter(responses=exception_responses)
genre_router = APIRouter(responses=exception_responses)
age_rating_router = APIRouter(responses=exception_responses)
platform_router = APIRouter(responses=exception_responses)


@game_router.get("/", response_model=List[GameOut], include_in_schema=False, response_model_exclude_none=True, response_model_exclude_unset=True)
@game_router.get("", response_model=List[GameOut], response_model_exclude_none=True, response_model_exclude_unset=True)
def get_games(offset: int = 0, limit: int = 10, filter: Optional[str] = None) -> Any:
    """
        Endpoint to get all games based on offset and limit values.
    """
    if limit < 1 or limit > 20:
        raise LimitException(limit=limit)
    game_selection = Game.objects.select_related('cover')
    game_prefetch = game_selection.prefetch_related(
        'age_ratings', 'tags', 'themes', 'keywords', 'genres', 'release_dates', 'age_ratings', 'dlcs', 'similar_games', 'remakes'
    )
    query = game_prefetch.all()[offset: offset + limit]
    return GameOut.from_django(query, many=True)


@game_router.get("/{slug:str}", response_model=GameOut, response_model_exclude_none=True, response_model_exclude_unset=True)
def get_game(slug: str) -> Any:
    """
        Endpoint to get specific game
    """
    if Game.objects.filter(slug=slug).exists():
        game_prefetch = Game.objects.prefetch_related(
            'age_ratings', 'tags', 'themes', 'keywords', 'genres', 'release_dates', 'age_ratings', 'dlcs', 'similar_games', 'remakes')
        query = game_prefetch.get(slug=slug)
        return GameOut.from_django(query)

    else:
        raise SlugException()


@genre_router.get("/", response_model=List[GenreSchema], include_in_schema=False, response_model_exclude_none=True, response_model_exclude_unset=True)
@genre_router.get("", response_model=List[GenreSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
def get_genres(offset: int = 0, limit: int = 10) -> Any:
    """
        Endpoint to get all the platforms based on offset and limit values.
    """
    if limit < 1 or limit > 20:
        raise LimitException(limit=limit)
    query = Genre.objects.all()[offset: offset + limit]
    return GenreSchema.from_django(query, many=True)


@genre_router.get("/{slug:str}", response_model=GenreSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
def get_genre(slug: str) -> Any:
    """
        Endpoint to get all the platforms based on offset and limit values.
    """
    query = Genre.objects.get(slug=slug)
    return GenreSchema.from_django(query)


@platform_router.get("/", response_model=List[PlatformSchema], include_in_schema=False, response_model_exclude_none=True, response_model_exclude_unset=True)
@platform_router.get("", responses={}, response_model=List[PlatformSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
def get_platforms(offset: int = 0, limit: int = 10) -> Any:
    """
        Endpoint to get all the platforms based on offset and limit values.
    """
    if limit < 1 or limit > 20:
        raise LimitException(limit=limit)
    query = Platform.objects.all()[offset: offset + limit]
    return PlatformSchema.from_django(query, many=True)


@platform_router.get("/{id:int}", response_model=PlatformSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
def get_platform(id: int) -> Any:
    """
        Endpoint to get all the platforms based on offset and limit values.
    """
    query = Platform.objects.get(id=id)
    return PlatformSchema.from_django(query)


@age_rating_router.get("/", response_model=List[AgeRatingSchema], include_in_schema=False, response_model_exclude_none=True, response_model_exclude_unset=True)
@age_rating_router.get("", responses={}, response_model=List[AgeRatingSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
def get_age_ratings(offset: int = 0, limit: int = 10) -> Any:
    """
        Endpoint to get all the age ratings based on offset and limit values.
    """
    if limit < 1 or limit > 20:
        raise LimitException(limit=limit)
    query = AgeRating.objects.all()[offset: offset + limit]
    return AgeRatingSchema.from_django(query, many=True)
