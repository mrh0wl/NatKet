from django.db import models

from .age_rating_model import AgeRating
from .alternative_titles import AlternativeTitle
from .collection_model import Collection
from .game_model import Game
from .game_video_model import GameVideo
from .image_model import Cover, LocaleCover, Thumbnail
from .language_model import Language, LanguageSupport, SupportType, LanguageTitles
from .object_imagefield import ObjectWithImageField
from .platform_model import Platform
from .region_model import Region
from .related_model import (GameMode, Genre, Keyword, Multiplayer,
                            PlayerPerspective, Tag, Theme)
from .release_platform_model import ReleasePlatform
from .website_model import Website


class User(models.Model):
    login = models.CharField(max_length=400)
    github_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Repository(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    github_id = models.BigIntegerField()
