from datetime import datetime
from typing import List, Optional

from djantic import ModelSchema
from pydantic import BaseModel, Field

from api.models import (AgeRating, Cover, Game, Genre, Keyword, Language,
                        LanguageSupport, Platform, ReleaseDate, SupportType,
                        Tag, Theme, AlternativeTitle)


class AgeRatingSchema(ModelSchema):
    id: int = Field(example=1)
    rating: str
    organization: AgeRating.Organizations

    class Config:
        model = AgeRating
        exclude = ['game_set']


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


class PlatformSchema(ModelSchema):
    """
    Base fields for platform model
    """
    id: int = Field(example=1)

    class Config:
        model = Platform
        exclude = ['releasedate_set', 'multiplayer_set']


class ReleaseDateSchema(ModelSchema):
    """
    Base fields for release date model
    """
    id: int = Field(example=1)
    platform: PlatformSchema

    class Config:
        model = ReleaseDate
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


class CoverSchema(ModelSchema):
    id: int = Field(example=1)
    animated: Optional[bool] = Field(example=False)

    class Config:
        model = Cover
        exclude = ['imagebase_ptr', 'game_set']


class LanguageSchema(ModelSchema):
    class Config:
        model = Language
        exclude = ['languagesupport_set']


class SupportTypeSchema(ModelSchema):
    class Config:
        model = SupportType
        exclude = ['languagesupport_set']


class AlternativeTitleSchema(ModelSchema):
    class Config:
        model = AlternativeTitle


class LanguageSupportSchema(ModelSchema):
    id: int = Field(example=1)
    cover: Optional[CoverSchema]
    support_types: Optional[List[SupportTypeSchema]]
    language: Optional[LanguageSchema]

    class Config:
        model = LanguageSupport
        exclude = ['game']


AgeRatings = List[AgeRatingSchema]
Keywords = List[KeywordSchema]
Genres = List[GenreSchema]
Themes = List[ThemeSchema]
Tags = List[TagSchema]
ReleaseDates = List[ReleaseDateSchema]
LanguageSupports = List[LanguageSupportSchema]
AlternativeTitles = List[AlternativeTitleSchema]


class GameBase(ModelSchema):
    """
    Base fields for game model.
    """
    id: int = Field(example=1)
    alternative_titles: AlternativeTitles
    title: str
    slug: str
    created_at: datetime
    updated_at: datetime
    first_release: Optional[datetime]
    type: Game.Type

    class Config:
        model = Game
        arbitrary_types_allowed = True
        exclude = ['game_cover', 'game_videos']


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


class GameOut(GameBase):
    """
    Response for api game.
    """
    age_ratings: Optional[AgeRatings]
    language_supports: Optional[LanguageSupports]
    cover: CoverSchema
    genres: Genres
    themes: Themes
    keywords: Keywords
    tags: Tags
    release_dates: ReleaseDates
    dlcs: Optional[Games]
    similar_games: Optional[Games]
    expanded_games: Optional[Games]
    standalone_expansions: Optional[Games]
    expansions: Optional[Games]
    remakes: Optional[Games]
    remasters: Optional[Games]


class DetailsExceptionSchema(BaseModel):
    cause: str
    message: str

    class Config:
        orm_mode = True


class ExceptionSchema(BaseModel):
    status_code: int
    status_msg: str
    details: DetailsExceptionSchema

    class Config:
        orm_mode = True
