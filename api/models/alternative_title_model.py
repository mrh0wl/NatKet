from typing import Any

from django.db import models

from .creation_update_model import CreatedUpdatedAt


class AlternativeTitle(CreatedUpdatedAt):
    title: str = models.CharField(max_length=100)
    game: Any = models.ForeignKey("api.Game", related_name='alternative_titles', on_delete=models.CASCADE, null=True, blank=True)
    description: str = models.CharField(max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.id)
