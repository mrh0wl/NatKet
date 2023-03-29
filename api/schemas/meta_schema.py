from pydantic import BaseModel
from typing import Optional, List


class LinksSchema(BaseModel):
    prev: Optional[str] = None
    next: Optional[str] = None
    first: Optional[str] = None
    last: Optional[str] = None


class FilterSchema(BaseModel):
    field: str
    type: str
    query: str


Filters = List[FilterSchema]


class MetaSchema(BaseModel):
    total_count: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    filters: Optional[Filters] = None
