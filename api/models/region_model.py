from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .creation_update_model import CreatedUpdatedAt


class Region(CreatedUpdatedAt):
    locale: str = models.CharField(max_length=10)
    name: str = models.CharField(
        max_length=70,
        default=settings.LANGUAGE_CODE
    )
