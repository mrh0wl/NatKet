from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .meta_schema import FilterSchema, LinksSchema, MetaSchema


class ResponseSchema(BaseModel):
    data: List[Dict[str, Any]]
    links: Optional[LinksSchema]
    meta: Optional[MetaSchema]

    def __init__(self, raw_filters: Optional[str], data: List[Dict[str, Any]], route_name: str, offset: Optional[int], limit: Optional[int], max_count: Optional[int], **filters):
        super().__init__(data=data)
        base_url = f"http://127.0.0.1:8000/api/v1/{route_name}"

        self.links = LinksSchema()
        self.meta = MetaSchema()
        fixed_filters = [
            FilterSchema(
                field=k.split('__')[0],
                type=k.split('__')[1].removeprefix('i') if k.split('__')[1] != 'isnull' else k.split('__')[1],
                query=v
            )
            for k, v in filters.items()]
        last_offset = max_count - (max_count % limit)
        self.links.last = f"{base_url}?{raw_filters}{self.query_params(last_offset, limit)}"
        self.links.first = f"{base_url}?{raw_filters}{self.query_params(0, limit)}"
        if offset - limit >= 0:
            self.links.prev = f"{base_url}?{raw_filters}{self.query_params(offset - limit, limit)}"
        if offset + limit < max_count:
            self.links.next = f"{base_url}?{raw_filters}{self.query_params(offset + limit, limit)}"

        self.meta = MetaSchema(
            total_count=max_count,
            offset=offset,
            limit=limit,
            filters=fixed_filters or None,
        )

    def query_params(self, offset: int, limit: int) -> str:
        return f"offset={offset}&limit={limit}"

    class Config:
        arbitrary_types_allowed = True
