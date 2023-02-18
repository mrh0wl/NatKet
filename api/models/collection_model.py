from django.db import models

from .game_model import Game
from .creation_update_model import CreatedUpdatedAt


class Collection(CreatedUpdatedAt):
    games = models.ForeignKey(Game, on_delete=models.CASCADE)
    slug: str = models.SlugField(unique=True)
    url: str = models.URLField(max_length=250)

    def __str__(self):
        return str(self.url)
