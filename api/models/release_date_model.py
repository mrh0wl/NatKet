from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.fields import UCDateTimeField

from .platform_model import Platform


class ReleaseDate(models.Model):
    class Regions(models.TextChoices):
        EUROPE = 'EU', _('Europe')
        NORTH_AMERICA = 'NA', _('North America')
        AUSTRALIA = 'AU', _('Australia')
        NEW_ZEALAND = 'NZ', _('New Zealand')
        JAPAN = 'JP', _('Japan')
        CHINA = 'CH', _('China')
        ASIA = 'AS', _('Asia')
        WORLDWIDE = 'WW', _('Worldwide')
        KOREA = 'KR', _('Korea')
        BRAZIL = 'BR', _('Brazil')

    platform: int = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
    )
    date: datetime = UCDateTimeField(
        auto_created=False,
        auto_now=False,
        auto_now_add=False,
        null=True
    )
    region: str = models.CharField(
        max_length=50,
        choices=Regions.choices,
    )
