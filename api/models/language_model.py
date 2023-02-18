from typing import Any

from django.db import models

from .creation_update_model import CreatedUpdatedAt


class Language(CreatedUpdatedAt):
    locale: str = models.CharField(max_length=10)
    name: str = models.CharField(max_length=100)
    native_ame: str = models.CharField(max_length=100)

    class Meta:
        ordering = ['locale']


class SupportType(CreatedUpdatedAt):
    name: str = models.CharField(max_length=30)


class LanguageSupport(CreatedUpdatedAt):
    language: Any = models.ForeignKey(
        Language,
        on_delete=models.CASCADE
    )
    support_type: Any = models.ForeignKey(
        SupportType,
        on_delete=models.CASCADE
    )
