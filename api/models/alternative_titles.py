from typing import Any

from django.db import models

from api.models.creation_update_model import CreatedUpdatedAt


class AlternativeTitle(CreatedUpdatedAt):
    title: str = models.CharField(max_length=100)
    type: str = models.CharField(max_length=100)
    game: Any = models.ForeignKey("api.Game", on_delete=models.CASCADE, related_name="alternative_titles")

    def save(self, *args, **kwargs):
        self.type = self.type.split()[0].capitalize()
        super(AlternativeTitle, self).save(*args, **kwargs)
