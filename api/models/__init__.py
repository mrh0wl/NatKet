from .age_rating_model import AgeRating
from .alternative_name_model import AlternativeName
from .collection_model import Collection
from .game_model import Game
from .game_video_model import GameVideo
from .image_model import Cover, PlatformLogo, Thumbnail
from .links_model import Links
from .object_imagefield import ObjectWithImageField
from .platform_model import Platform
from .region_model import LocaleCover, Region
from .release_date_model import ReleaseDate
from .related_model import Genre, Keyword, Tag, Theme

from django.db import models


class User(models.Model):
    login = models.CharField(max_length=400)
    github_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Repository(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    github_id = models.BigIntegerField()