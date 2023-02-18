from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .creation_update_model import CreatedUpdatedAt


class Region(CreatedUpdatedAt):
    class Type(models.TextChoices):
        CONTINENT = 'continent', _('Continent')
        LOCALE = 'locale', _('Locale')

    locale: str = models.CharField(max_length=10)
    name: str = models.CharField(
        max_length=70,
        default=settings.LANGUAGE_CODE
    )
    type: str = models.CharField(
        max_length=10,
        choices=Type.choices,
    )


class LocaleCover(Region):
    game: Any = models.ForeignKey(
        'api.Game',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='game_cover'
    )
