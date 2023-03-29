from django.db import models
from django.utils.translation import gettext_lazy as _
from .creation_update_model import CreatedUpdatedAt


class Platform(CreatedUpdatedAt):
    class Type(models.TextChoices):
        CONSOLE = 'CONSOLE', _('Console')
        ARCADE = 'ARCADE', _('Arcade')
        PLATFORM = 'PLATFORM', _('Platform')
        OPERATING_SYSTEM = 'OPERATING_SYSTEM', _('Operating System')
        PORTABLE_CONSOLE = 'PORTABLE_CONSOLE', _('Portable Console')
        COMPUTER = 'COMPUTER', _('Computer')
        UNDEFINED = 'UNDEFINED', _('Undefined')

    name: str = models.CharField(max_length=100, unique=True)
    abbreviation: str = models.CharField(max_length=20, null=True)
    alternative_name: str = models.CharField(max_length=100, null=True)
    type: str = models.CharField(
        max_length=100,
        choices=Type.choices,
    )

    class Meta:
        verbose_name = 'Platform'
        verbose_name_plural = 'Platforms'
        ordering = ['name']
