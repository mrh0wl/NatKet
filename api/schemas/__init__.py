from .exception_schema import ExceptionSchema
from .gameplay_schema import AgeRatingSchema, GameModeSchema, PlatformSchema, PlayerPerspectiveSchema, ReleasePlatformSchema, Platforms, PlayerPerspectives
from .language_schema import LanguageSchema, SupportTypeSchema, AlternativeTitleSchema, LanguageSupportSchema, LanguageTitleSchema, Languages, LanguageTitles
from .media_schema import CoverSchema, VideoSchema, ThumbnailSchema
from .meta_schema import LinksSchema, MetaSchema, FilterSchema
from .related_schema import KeywordSchema, GenreSchema, ThemeSchema, TagSchema
from .response_schema import ResponseSchema
from .game_schema import GameSchema, GameBase, Games, Keywords, Genres, Themes
from pydantic import Field, BaseModel
from typing import List, TypeVar


class GamesResponse(ResponseSchema):
    data: Games


class GameResponse(ResponseSchema):
    data: GameSchema = Field(alias="Game")


class PPsResponse(ResponseSchema):
    data: PlayerPerspectives


class PPResponse(ResponseSchema):
    data: PlayerPerspectiveSchema = Field(alias="PlayerPerspective")


class GenresResponse(ResponseSchema):
    data: Genres


class GenreResponse(ResponseSchema):
    data: GenreSchema = Field(alias="Genre")


class KeywordsResponse(ResponseSchema):
    data: Keywords


class KeywordResponse(ResponseSchema):
    data: KeywordSchema = Field(alias="Keyword")


class ThemesResponse(ResponseSchema):
    data: Themes


class ThemeResponse(ResponseSchema):
    data: ThemeSchema = Field(alias="Theme")


class PlatformsResponse(ResponseSchema):
    data: Platforms


class PlatformResponse(ResponseSchema):
    data: PlatformSchema = Field(alias="Platform")


class LanguagesResponse(ResponseSchema):
    data: Languages


class LanguageResponse(ResponseSchema):
    data: LanguageSchema = Field(alias="Language")


class PaginatedResponse(BaseModel):
    message: str
    result: ResponseSchema

    def __init__(self, message: str, result: ResponseSchema):
        super().__init__(message=message, result=result)
