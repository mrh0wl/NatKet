from typing import Any

from django.db import models


class AlternativeName(models.Model):
    name: str = models.CharField(max_length=100)
    game: Any = models.ForeignKey("api.Game", on_delete=models.CASCADE)
    description: str = models.CharField(max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.id)
