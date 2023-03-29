import re
from http.client import responses
from operator import attrgetter
from typing import Any, Dict, List, Optional

from django.core.exceptions import FieldError
from django.utils.html import escape
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from api.schemas import PaginatedResponse, ResponseSchema
from api.schemas.exception_schema import BadRequestSchema, ForbiddenSchema, NotFoundSchema, ValidationErrorSchema
from main.utils.exceptions import FilterException, LimitException, OffsetException, SlugException, SortException
from utils import String

example_field = "?filters[field]"
filters_examples = {
    "normal": {
        "summary": "Filter exact words. (<QUERY>)",
        "value": {
            example_field: "query"
        },
    },
    "contains": {
        "summary": "Filter words that are in. (*<QUERY>*)",
        "value": {
            example_field: "*query*"
        },
    },
    "endswith": {
        "summary": "Filter words that end with. (*<QUERY>)",
        "value": {
            example_field: "*query"
        },
    },
    "startswith": {
        "summary": "Filter words that start with. (<QUERY>*)",
        "value": {
            example_field: "query*"
        },
    },
    "not-null": {
        "summary": "Filter fields that are not null. (!!<FIELD>)",
        "value": {
            "?filters[!!field]": ""
        },
    },
    "not-null-search": {
        "summary": "Filter field that is not null and search query. (!<FIELD>)",
        "value": {
            "?filters[!field]": "*fantasy*"
        },
    },
    "combined": {
        "summary": "Filter not null field and search query for the other one.",
        "value": {
            "?filters[!!field1,field2]": "*query*"
        },
    },
}


class RootQueryParams:
    def __init__(
        self,
        filters: str = Query(
            default=None,
            description="Allows advanced filtering of the data adding extra logic in request.",
            examples=filters_examples
        ),
        offset: int = Query(
            default=0,
            description="Position in the dataset of a particular record.",
            example={"?offset": 15}
        ),
        limit: int = Query(
            default=10,
            description="Amount of total data that can access per request."
        ),
        sort: Optional[str] = Query(
            default=None,
            description="Allows to order the results by field, in ascending or descending order."),
    ):
        self.filters = filters
        self.offset = offset
        self.limit = limit
        self.sort = sort


class BaseRouter(APIRouter):
    name_root = None
    name_slug = None
    path_slug = r"/{slug:str}"
    description_root = None
    description_slug = None
    custom_responses = {
        400: {'model': BadRequestSchema},
        403: {'model': ForbiddenSchema},
        404: {'model': NotFoundSchema},
        422: {'model': ValidationErrorSchema, 'description': 'Validation Error'}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirect_slashes = True
        self.responses = self.custom_responses
        self.model_name = String(self.model.__name__).split_camelcase
        self.prefix = f'/{"-".join(self.model_name.lower().strip().split())}s'
        self.param_name = re.search(r"{(\w+):?.*}", self.path_slug)[1]
        self.name_root = self.name_slug or f'Get All {self.model_name}s'
        self.name_slug = self.name_slug or f'Get {self.model_name}'
        self.description_root = self.description_root or f'Endpoint to get all {self.model_name}s based on offset and limit values.'
        self.description_slug = self.description_slug or f'Endpoint to get a specific {self.model_name}.'
        self.tags = [f'{self.model_name}s']

        self._add_routes()

    def _add_routes(self):
        """Add routes"""
        self.add_api_route(
            path="",
            status_code=200,
            endpoint=self.get_items,
            name=self.name_root or f'Get all {self.model_name}s',
            description=self.description_root,
            response_model=PaginatedResponse,
            response_model_exclude_none=True,
            methods=["GET"],
        )

        self.add_api_route(
            path=self.path_slug,
            status_code=200,
            endpoint=self.get_specific_item,
            name=self.name_slug or f'Get {self.model_name}',
            description=self.description_slug,
            response_model=PaginatedResponse,
            response_model_exclude_none=True,
            methods=["GET"],
            openapi_extra={
                'parameters': [
                    {
                        "required": True,
                        'schema': {'title': self.param_name.capitalize(), 'type': 'string'},
                        'name': self.param_name,
                        'in': 'path'
                    }
                ]
            },
        )

    def get_items(self, request: Request, params: RootQueryParams = Depends()) -> Any:
        sort, offset, limit = attrgetter('sort', 'offset', 'limit')(params)
        filters = {}
        q_params = request.query_params._dict
        filter_re = re.compile(r'^filters?\[(.*)\]$')
        filter_items = [
            (filter_re.search(k.strip().replace(' ', ''))[1], v)
            for k, v in q_params.items() if filter_re.search(k.strip().replace(' ', ''))
        ]
        if filter_items and filter_items[0]:
            self._filtering_data(filter_items, filters)
        elif 'filter' in q_params.keys():
            raise FilterException(code=1)
        sort_sanitized = self.sanitize_sort(sort)
        self.validate_limit(limit)
        self.validate_offset(offset)

        try:
            ordered_and_filtered = self.model.objects.all().filter(**filters).order_by(sort_sanitized)
            query = ordered_and_filtered[offset: offset + limit]
            count = ordered_and_filtered.count()
            raw_filters = f'filters[{filter_items[0][0]}]={filter_items[0][1]}&' if filter_items else ''
            result = ResponseSchema(raw_filters=raw_filters, data=self.schema.from_django(query, many=True),
                                    route_name=f'{self.model_name.lower()}s', offset=offset, limit=limit, max_count=count, **filters)
            response = PaginatedResponse(message=responses[200], result=result)
            return JSONResponse(content=jsonable_encoder(response.dict()))
        except FieldError as e:
            self.handle_sort_exception(e)

    def _filtering_data(self, filter_items: List, filters: Dict[str, str]):
        filter_keys, filter_value = filter_items[0]
        filter_list = self._check_filter_list_length(filter_keys)

        for filter_key in filter_list:
            filter_key, is_nullable = self._set_isnull_filter(filters, filter_key)
            self._check_filter_key(filter_key)
            self._check_filter_key_exists(filter_key.lower())
            if is_nullable:
                self._set_filter(filters, filter_key, filter_value)

    def _check_filter_key(self, filter_key: str):
        if not filter_key:
            raise FilterException(code=1)

    def _check_filter_list_length(self, filter_keys):
        filter_list = re.split(r'[|,]', filter_keys)
        if len(filter_list) > 2:
            raise FilterException(code=2, key=filter_keys)
        return filter_list

    def _check_filter_key_exists(self, filter_key_lower: str):
        if not hasattr(self.model, filter_key_lower):
            raise FilterException(code=0, key=filter_key_lower, model=self.model_name)

    def _set_filter(self, filters: Dict[str, Any], filter_key: str, filter_value: str):
        stripped_filter_value = filter_value.strip('*')
        it_starts = filter_value.startswith('*')
        it_ends = filter_value.endswith('*')
        if it_starts and it_ends:
            filters[f'{filter_key}__icontains'] = stripped_filter_value
        elif it_ends:
            filters[f'{filter_key}__istartswith'] = stripped_filter_value
        elif it_starts:
            filters[f'{filter_key}__iendswith'] = stripped_filter_value
        else:
            filters[f'{filter_key}__iexact'] = filter_value

    def _set_isnull_filter(self, filters, filter_key):
        is_nullable = filter_key.count('!') < 2
        if filter_key.startswith('!'):
            filter_key = filter_key.strip('!')
            filters[f'{filter_key}__isnull'] = False
        return filter_key, is_nullable

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

    def get_specific_item(self, request: Request) -> Any:
        param_value = request['path_params'][self.param_name]
        filter_query = {self.param_name: param_value}
        if self.model.objects.filter(**filter_query).exists():
            query = self.model.objects.get(**filter_query)
            result = ResponseSchema(raw_filters=None, data=self.schema.from_django(query),
                                    route_name=f'{self.model_name.lower()}s', offset=None, limit=None, max_count=None)
            response = PaginatedResponse(message=responses[200], result=result)
            return JSONResponse(content=jsonable_encoder(response.dict(exclude_none=True)))
        else:
            raise SlugException()
