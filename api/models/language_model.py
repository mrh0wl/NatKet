from typing import Any

from django.db import models

from .creation_update_model import CreatedUpdatedAt


class Language(CreatedUpdatedAt):
    locale: str = models.CharField(max_length=10, null=True)
    name: str = models.CharField(max_length=100, null=True)
    native_name: str = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['locale']


class SupportType(CreatedUpdatedAt):
    name: str = models.CharField(max_length=30, null=True)


class LanguageSupport(CreatedUpdatedAt):
    support_type: Any = models.ForeignKey(SupportType, on_delete=models.CASCADE, related_name='support_type')
    language: Any = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='language')
    game: Any = models.ForeignKey("api.Game", on_delete=models.CASCADE, related_name="language_supports")
