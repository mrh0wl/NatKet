import json
import re
from typing import Any, Dict, List, Optional

from django.core.exceptions import FieldError
from django.utils.html import escape
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from http.client import responses

from api.models import AgeRating, Game, Genre, Platform
from api.schemas import (AgeRatingSchema, ExceptionSchema, GameSchema,
                         GenreSchema, PaginatedResponse, PlatformSchema)
from main.exceptions import (FilterException, LimitException, OffsetException,
                             SlugException, SortException)
from utils.custom_str import String


class BaseRouter(APIRouter):
    description_root = None
    description_slug = None
    exception_responses = {
        400: {'model': ExceptionSchema},
        403: {'model': ExceptionSchema},
        404: {'model': ExceptionSchema},
        # 422: {'model': ExceptionSchema}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirect_slashes = True
        self.responses = self.exception_responses
        self.model_name = self.model.__name__

        self._add_routes()

    def _add_routes(self):
        default_description_root = f'Endpoint to get all {self.model_name}s based on offset and limit values.'
        default_description_slug = f'Endpoint to get a specific {self.model_name}.'
        description_root = self.description_root or default_description_root
        description_slug = self.description_slug or default_description_slug

        self.add_api_route(
            path="",
            endpoint=self.get_items,
            name=f'Get all {self.model_name}s',
            description=description_root,
            response_model=PaginatedResponse,
            response_model_exclude_none=True,
            methods=["GET"],
        )

        self.add_api_route(
            path=r"/{slug:str}",
            endpoint=self.get_item_by_slug,
            name=f'Get {self.model_name} by slug',
            description=description_slug,
            response_model=PaginatedResponse,
            response_model_exclude_none=True,
            methods=["GET"]
        )

    def get_items(self, request: Request, offset: int = 0, limit: int = 10, sort: Optional[str] = None) -> Any:
        filters = {}
        q_params = request.query_params._dict
        filter_re = re.compile(r'^filters?(?=\[([\w_,]+)?\]|)')
        filter_items = [
            (filter_re.search(k.strip().replace(' ', ''))[1], v)
            for k, v in q_params.items()
        ]
        if filter_items and filter_items[0]:
            self._filtering_data(filter_items, filters)
        sort_sanitized = self.sanitize_sort(sort)
        self.validate_limit(limit)
        self.validate_offset(offset)

        try:
            query = self.model.objects.all().filter(**filters).order_by(sort_sanitized)[offset: offset + limit]
            count = self.model.objects.count()
            response = PaginatedResponse(message=responses[200], data=self.schema.from_django(query, many=True),
                                         route_name=f'{self.model_name.lower()}s', offset=offset, limit=limit, max_count=count, **filters)
            return JSONResponse(content=jsonable_encoder(response))
        except FieldError as e:
            self.handle_sort_exception(e)

    def _filtering_data(self, filter_items: List, filters: Dict[str, str]):
        filter_key, filter_value = filter_items[0]
        if not filter_key:
            raise FilterException(code=1)

        if len(filter_key.split()) != 1:
            raise FilterException(code=2)

        if not hasattr(self.model, filter_key.lower()):
            raise FilterException(code=0, key=filter_key.lower(), model=self.model_name)

        if re.search(r'(?<=\*)(.*)(?=\*)', filter_value):
            filter_key += '__icontains'
        elif re.search(r'(?<=\*)(\w+)$', filter_value):
            filter_key += '__iendswith'
        elif re.search(r'^(\w+)(?=\*)', filter_value):
            filter_key += '__istartswith'
        else:
            filter_key += '__iexact'
        filters[filter_key] = filter_value.strip('*')

    def sanitize_sort(self, sort: Optional[str]) -> str:
        if not sort:
            return ', '.join(self.model._meta.ordering)
        sort_sanitized = ', '.join(re.sub(r'[^-?A-Za-z0-9]+,?\s?', ' ', sort).split())
        return escape(sort_sanitized)

    def validate_limit(self, limit: int) -> None:
        if limit < 1 or limit > 20:
            raise LimitException(limit=limit)

    def validate_offset(self, offset: int) -> None:
        if offset < 0:
            raise OffsetException()

    def handle_sort_exception(self, e: FieldError) -> None:
        raise SortException(e.args[0].split('Choices are:')[1])

    def get_item_by_slug(self, slug: str) -> Any:
        if self.model.objects.filter(slug=slug).exists():
            query = self.model.objects.get(slug=slug)
            return self.schema.from_django(query)
        else:
            raise SlugException()


class GameRouter(BaseRouter):
    model = Game
    schema = GameSchema
    description_root = 'THIS IS A TEST'


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
