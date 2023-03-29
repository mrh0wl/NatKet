from djantic import ModelSchema
from pydantic import Field
from api.models import Genre, Keyword, Tag, Theme


class ThemeSchema(ModelSchema):
    """
    Base fields for theme model
    """
    id: int = Field(example=1)

    class Config:
        model = Theme
        exclude = ['game_set']


class GenreSchema(ModelSchema):
    """
    Base fields for genre model
    """
    id: int = Field(example=1)

    class Config:
        model = Genre
        exclude = ['game_set']


class KeywordSchema(ModelSchema):
    """
    Base fields for keyword model
    """
    id: int = Field(example=1)

    class Config:
        model = Keyword
        exclude = ['game_set']


class TagSchema(ModelSchema):
    """
    Base fields for tag model
    """
    id: int = Field(example=1)

    class Config:
        model = Tag
        include = ["created_at", "updated_at", "value"]
