from datetime import datetime
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.fields import UCDateTimeField


class ReleasePlatform(models.Model):
    class Regions(models.TextChoices):
        EUROPE = 'EU', _('Europe')
        ES = 'ES', _('Spanish')
        LAT = 'LAT', _('Spanish (LATAM)')
        NORTH_AMERICA = 'NA', _('North America')
        AUSTRALIA = 'AU', _('Australia')
        NEW_ZEALAND = 'NZ', _('New Zealand')
        JAPAN = 'JP', _('Japan')
        CHINA = 'CH', _('China')
        ASIA = 'AS', _('Asia')
        WORLDWIDE = 'WW', _('Worldwide')
        KOREA = 'KR', _('Korea')
        BRAZIL = 'BR', _('Brazil')

    game: Any = models.ForeignKey("api.Game", on_delete=models.CASCADE, related_name='release_platforms')
    platform: int = models.ForeignKey('api.Platform', on_delete=models.CASCADE)
    multiplayer_modes: Any = models.ForeignKey('api.Multiplayer', on_delete=models.CASCADE, null=True)
    release_date: datetime = UCDateTimeField(
        auto_created=False,
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True
    )
    region: str = models.CharField(
        max_length=3,
        choices=Regions.choices,
    )
