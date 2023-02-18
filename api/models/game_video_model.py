from typing import Any

from django.db import models

from .creation_update_model import CreatedUpdatedAt


class GameVideo(CreatedUpdatedAt):
    name: str = models.CharField(max_length=100)
    game: Any = models.ForeignKey("api.Game", on_delete=models.CASCADE)
    video_id: str = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)
