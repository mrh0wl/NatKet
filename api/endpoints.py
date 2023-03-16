from api.models import (Game, Genre, Keyword, Language, Platform,
                        PlayerPerspective, Theme)
from api.schemas import (GameSchema, GenreSchema,
                         KeywordSchema, LanguageSchema, PlatformSchema,
                         PlayerPerspectiveSchema, ThemeSchema)

from .services import BaseRouter


class GameRouter(BaseRouter):
    model = Game
    schema = GameSchema


class GenreRouter(BaseRouter):
    model = Genre
    schema = GenreSchema


class KeywordRouter(BaseRouter):
    model = Keyword
    schema = KeywordSchema


class ThemeRouter(BaseRouter):
    model = Theme
    schema = ThemeSchema


class LanguageRouter(BaseRouter):
    model = Language
    schema = LanguageSchema
    path_slug = r"/{locale:str}"
    name_slug = "Get Language by locale"


class PlayerPerspectiveRouter(BaseRouter):
    model = PlayerPerspective
    schema = PlayerPerspectiveSchema


class PlatformRouter(BaseRouter):
    model = Platform
    schema = PlatformSchema


game_router = GameRouter()
genre_router = GenreRouter()
keyword_router = KeywordRouter()
theme_router = ThemeRouter()
language_router = LanguageRouter()
player_perspective_router = PlayerPerspectiveRouter()
platform_router = PlatformRouter()
