from datetime import datetime
from typing import Any, Dict, List, Optional

from djantic import ModelSchema
from pydantic import BaseModel, Field

from api.models import (AgeRating, AlternativeTitle, Cover, Game, GameMode,
                        GameVideo, Genre, Keyword, Language, LanguageSupport,
                        LanguageTitle, Multiplayer, Platform,
                        PlayerPerspective, ReleasePlatform, SupportType, Tag,
                        Theme, Thumbnail)


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


class GameModeSchema(ModelSchema):
    class Config:
        model = GameMode
        exclude = ['game_set']


class PlayerPerspectiveSchema(ModelSchema):
    class Config:
        model = PlayerPerspective
        exclude = ['game_set']


class MultiplayerModeSchema(ModelSchema):
    class Config:
        model = Multiplayer
        exclude = ['releaseplatform_set']


class PlatformSchema(ModelSchema):
    """
    Base fields for platform model
    """
    id: int = Field(example=1)

    class Config:
        model = Platform
        exclude = ['releaseplatform_set']


class ReleasePlatformSchema(ModelSchema):
    """
    Base fields for release date model
    """
    id: int = Field(example=1)
    platform: PlatformSchema
    multiplayer_modes: Optional[MultiplayerModeSchema]

    class Config:
        model = ReleasePlatform
        exclude = ['game']


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


class ThumbnailSchema(ModelSchema):
    id: int = Field(example=1)
    animated: Optional[bool] = Field(example=False)

    class Config:
        model = Thumbnail
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
        exclude = ['game']


class LanguageTitleSchema(ModelSchema):
    class Config:
        model = LanguageTitle
        exclude = ['languagesupport']


LanguageTitles = List[LanguageTitleSchema]


class LanguageSupportSchema(ModelSchema):
    id: int = Field(example=1)
    cover: Optional[CoverSchema]
    support_types: Optional[List[SupportTypeSchema]]
    language: Optional[LanguageSchema]
    language_titles: LanguageTitles

    class Config:
        model = LanguageSupport
        exclude = ['game']


class VideoSchema(ModelSchema):
    id: int = Field(example=1)

    class Config:
        model = GameVideo


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
GameModesList = List[GameModeSchema]
Thumbnails = List[ThumbnailSchema]


class GameBase(ModelSchema):
    """
    Base fields for game model.
    """
    id: int = Field(example=1)
    player_perspectives: Optional[PlayerPerspectives] = []
    thumbnails: Optional[Thumbnails] = []
    alternative_titles: Optional[AlternativeTitles] = Field(default=None)
    title: str
    slug: str
    created_at: datetime
    updated_at: datetime
    first_release: Optional[datetime] = None
    type: Game.Type
    videos: Optional[Videos] = []
    age_ratings: Optional[AgeRatings] = []
    language_supports: Optional[LanguageSupports] = []
    cover: Optional[CoverSchema]
    genres: Optional[Genres] = []
    themes: Optional[Themes] = []
    keywords: Optional[Keywords] = []
    game_modes: Optional[GameModesList] = []
    tags: Optional[Tags] = []
    release_platforms: Optional[ReleasePlatforms] = []
    dlcs: Optional[Any] = []
    similar_games: Optional[Any] = []
    expanded_games: Optional[Any] = []
    standalone_expansions: Optional[Any] = []
    expansions: Optional[Any] = []
    remakes: Optional[Any] = []
    remasters: Optional[Any] = []

    class Config:
        model = Game
        arbitrary_types_allowed = True
        exclude = ['game_cover', 'game_videos']


class LinksResponse(BaseModel):
    prev: Optional[str] = None
    next: Optional[str] = None
    first: Optional[str] = None
    last: Optional[str] = None


class MetaResponse(BaseModel):
    total_count: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    filters: Optional[List[Dict]] = None


class ResultResponse(BaseModel):
    data: List[dict]
    links: LinksResponse = LinksResponse()
    meta: MetaResponse = MetaResponse()

    def __init__(self, raw_filters: str, data: List[dict], route_name: str, offset: int, limit: int, max_count: int, **filters):
        super().__init__(data=data)
        base_url = f"http://127.0.0.1:8000/api/v1/{route_name}"

        fixed_filters = [{'field': k.split('__')[0], 'type': k.split(
            '__')[1].removeprefix('i') if k.split('__')[1] != 'isnull' else k.split('__')[1], 'query': v} for k, v in filters.items()]
        last_offset = max_count - (max_count % limit)
        self.links.last = f"{base_url}?{raw_filters}{self.query_params(last_offset, limit)}"
        self.links.first = f"{base_url}?{raw_filters}{self.query_params(0, limit)}"
        if offset - limit >= 0:
            self.links.prev = f"{base_url}?{raw_filters}{self.query_params(offset - limit, limit)}"
        if offset + limit < max_count:
            self.links.next = f"{base_url}?{raw_filters}{self.query_params(offset + limit, limit)}"

        self.meta = MetaResponse(
            total_count=max_count,
            offset=offset,
            limit=limit,
            filters=fixed_filters or None,
        )

    def query_params(self, offset: int, limit: int) -> str:
        # print('&filter'+''.join([f'[{item["field"]}]={item["query"]}' for item in filters]))
        return f"offset={offset}&limit={limit}"


class PaginatedResponse(BaseModel):
    message: str
    result: ResultResponse

    def __init__(self, raw_filters: str, message: str, data: List[dict], route_name: str, offset: int, limit: int, max_count: int, **filters):
        super().__init__(message=message, result=ResultResponse(raw_filters, data, route_name, offset, limit, max_count, **filters))


class CreateGame(GameBase):
    """
    Fields for creating a blog category.
    """
    ...


class UpdateGame(GameBase):
    """
    Fields for updating blog categories.
    """


class GameSchema(GameBase):
    """
    Response for api game.
    """


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
