from typing import Optional, List
from djantic import ModelSchema
from pydantic import Field
from api.models import AgeRating, GameMode, Platform, PlayerPerspective, Multiplayer, ReleasePlatform


class AgeRatingSchema(ModelSchema):
    id: int = Field(example=1)
    rating: str
    organization: AgeRating.Organizations

    class Config:
        model = AgeRating
        exclude = ['game_set']


class GameModeSchema(ModelSchema):
    class Config:
        model = GameMode
        exclude = ['game_set']


class PlayerPerspectiveSchema(ModelSchema):
    class Config:
        model = PlayerPerspective
        exclude = ['game_set']


PlayerPerspectives = List[PlayerPerspectiveSchema]


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


Platforms = List[PlatformSchema]


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
