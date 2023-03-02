from typing import Any, Optional, List

from fastapi import APIRouter

from api.models import Game, Platform, Genre, AgeRating
from api.schemas import GameOut, PlatformSchema, GenreSchema, ExceptionSchema, AgeRatingSchema
from main.exceptions import LimitException, SlugException, OffsetException

from utils.custom_str import String


class BaseRouter(APIRouter):
    exception_responses = {
        400: {'model': ExceptionSchema},
        403: {'model': ExceptionSchema},
        # 422: {'model': ExceptionSchema}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirect_slashes = True
        self.responses = self.exception_responses

        model_name: str = String(self.model.__name__).split_camelcase
        description_root = kwargs.get(
            'description_root') or f'Endpoint to get all __{model_name}s__ based on offset and limit values.'
        description_slug = kwargs.get('description_slug') or f'Endpoint to get a specific __{model_name}__.'
        # Add api route default
        self.add_api_route(path="",
                           endpoint=self.get_items,
                           name=f'Get all {model_name}s',
                           description=description_root,
                           response_model=List[self.schema],
                           response_model_exclude_none=True,
                           methods=["GET"]
                           )

        # Add api route by slug
        self.add_api_route(path=r"/{slug:str}",
                           endpoint=self.get_item_by_slug,
                           name=f'Get {model_name} by slug',
                           description=description_slug,
                           response_model=self.schema,
                           response_model_exclude_none=True,
                           methods=["GET"]
                           )

    def get_items(self, offset: int = 0, limit: int = 10, filter: Optional[str] = None) -> Any:
        if limit < 1 or limit > 20:
            raise LimitException(limit=limit)
        if offset < 0:
            raise OffsetException()

        query = self.model.objects.all()[offset: offset + limit]
        return self.schema.from_django(query, many=True)

    def get_item_by_slug(self, slug: str) -> Any:
        if self.model.objects.filter(slug=slug).exists():
            query = self.model.objects.get(slug=slug)
            return self.schema.from_django(query)
        else:
            raise SlugException()


class GameRouter(BaseRouter):
    model = Game
    schema = GameOut


class GenreRouter(BaseRouter):
    model = Genre
    schema = GenreSchema


class PlatformRouter(BaseRouter):
    model = Platform
    schema = PlatformSchema


class AgeRatingRouter(BaseRouter):
    model = AgeRating
    schema = AgeRatingSchema


game_router = GameRouter()
genre_router = GenreRouter()
age_rating_router = AgeRatingRouter()
platform_router = PlatformRouter()
