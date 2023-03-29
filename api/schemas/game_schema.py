from datetime import datetime
from typing import List, Optional

from djantic import ModelSchema
from pydantic import Field

from api.models import Game

from .gameplay_schema import (AgeRatingSchema, GameModeSchema,
                              PlayerPerspectiveSchema, ReleasePlatformSchema)
from .language_schema import AlternativeTitleSchema, LanguageSupportSchema
from .media_schema import CoverSchema, ThumbnailSchema, VideoSchema
from .related_schema import GenreSchema, KeywordSchema, TagSchema, ThemeSchema

AgeRatings = List[AgeRatingSchema]
Keywords = List[KeywordSchema]
Genres = List[GenreSchema]
Themes = List[ThemeSchema]
Tags = List[TagSchema]
ReleasePlatforms = List[ReleasePlatformSchema]
LanguageSupports = List[LanguageSupportSchema]
AlternativeTitles = List[AlternativeTitleSchema]
PlayerPerspectives = List[PlayerPerspectiveSchema]
Videos = List[VideoSchema]
GameModes = List[GameModeSchema]
Thumbnails = List[ThumbnailSchema]


class GameBase(ModelSchema):
    """
    Base fields for game model.
    """
    id: int = Field(example=1)
    player_perspectives: Optional[PlayerPerspectives]
    thumbnails: Optional[Thumbnails]
    alternative_titles: Optional[AlternativeTitles]
    title: str
    slug: str
    created_at: datetime
    updated_at: datetime
    first_release: Optional[datetime] = None
    type: Game.Type
    videos: Optional[Videos]
    status: Game.Status
    age_ratings: Optional[AgeRatings]
    language_supports: Optional[LanguageSupports]
    cover: Optional[CoverSchema]
    genres: Optional[Genres]
    themes: Optional[Themes]
    keywords: Optional[Keywords]
    game_modes: Optional[GameModes]
    tags: Optional[Tags]
    release_platforms: Optional[ReleasePlatforms]

    class Config:
        model = Game
        arbitrary_types_allowed = True


class CreateGame(GameBase):
    """
    Fields for creating a blog category.
    """
    ...


class UpdateGame(GameBase):
    """
    Fields for updating blog categories.
    """


Games = List[GameBase]
GamesDefault = ["List of Games"]


class GameSchema(GameBase):
    """
    Response for api game.
    """
    collection: Optional[Games] = Field(default=GamesDefault)
    dlcs: Optional[Games] = Field(default=GamesDefault)
    similar_games: Optional[Games] = Field(default=GamesDefault)
    expanded_games: Optional[Games] = Field(default=GamesDefault)
    standalone_expansions: Optional[Games] = Field(default=GamesDefault)
    expansions: Optional[Games] = Field(default=GamesDefault)
    remakes: Optional[Games] = Field(default=GamesDefault)
    remasters: Optional[Games] = Field(default=GamesDefault)
