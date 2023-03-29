from typing import Optional
from djantic import ModelSchema
from pydantic import Field
from api.models import Cover, Thumbnail, GameVideo


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
        exclude = ['imagebase_ptr', 'game']


class VideoSchema(ModelSchema):
    id: int = Field(example=1)

    class Config:
        model = GameVideo
