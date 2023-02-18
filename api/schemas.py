from datetime import datetime
from typing import List, Optional

from djantic import ModelSchema
from pydantic import Field, validator

from api.models import Game, Genre, Keyword, ReleaseDate, Tag, Theme, Platform, Cover


def confirm_title(value: str) -> str:
    """
    Validation to prevent empty title field.
    Called by the helper function below;
    """
    if not value:
        raise ValueError("Please provide a title.")
    return value


def confirm_slug(value: str) -> str:
    """
    Validation to prevent empty slug field.
    Called by the helper function below;
    """
    if not value:
        raise ValueError("Slug cannot be empty.")
    return value


class ThemeSchema(ModelSchema):
    """
    Base fields for theme model
    """

    class Config:
        model = Theme
        exclude = ['game_set']


class GenreSchema(ModelSchema):
    """
    Base fields for genre model
    """

    class Config:
        model = Genre
        exclude = ['game_set']


class PlatformSchema(ModelSchema):
    """
    Base fields for platform model
    """

    class Config:
        model = Platform
        exclude = ['releasedate_set']


class ReleaseDateSchema(ModelSchema):
    """
    Base fields for release date model
    """

    platform: PlatformSchema

    class Config:
        model = ReleaseDate
        exclude = ['game_set']


class KeywordSchema(ModelSchema):
    """
    Base fields for keyword model
    """

    class Config:
        model = Keyword
        exclude = ['game_set']


class TagSchema(ModelSchema):
    """
    Base fields for tag model
    """

    class Config:
        model = Tag
        include = ["created_at", "updated_at", "value"]


class CoverSchema(ModelSchema):

    class Config:
        model = Cover
        exclude = ['imagebase_ptr']


Keywords = List[KeywordSchema]
Genres = List[GenreSchema]
Themes = List[ThemeSchema]
Tags = List[TagSchema]
ReleaseDates = List[ReleaseDateSchema]


class GameBase(ModelSchema):
    """
    Base fields for game model.
    """
    title: str = Field(example="Sunshine Shuffle")
    slug: str = Field(example="sunshine-shuffle")
    created_at: datetime = Field(example="2023-02-15T21:02:36.241651+00:00")
    updated_at: datetime = Field(example="2023-02-15T21:02:36.272645+00:00")
    first_release: Optional[datetime] = Field(
        default=None, example="2020-05-12 18:00:00")
    type: Game.Type = Field(example="MG")
    _confirm_title = validator("title", allow_reuse=True)(confirm_title)

    class Config:
        model = Game
        arbitrary_types_allowed = True
        exclude = ['tags']


class CreateGame(GameBase):
    """
    Fields for creating a blog category.
    """
    ...


class UpdateGame(GameBase):
    """
    Fields for updating blog categories.
    """


class GameOut(GameBase):
    """
    Response for api game.
    """
    cover: CoverSchema
    genres: Genres
    themes: Themes
    keywords: Keywords
    # tags: Tags
    release_dates: ReleaseDates
