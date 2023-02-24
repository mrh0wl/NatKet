from django.db import models
from django.utils.text import slugify

from .creation_update_model import CreatedUpdatedAt
from .game_model import Game
from .object_imagefield import unique_slugify


class Collection(CreatedUpdatedAt):
    name: str = models.CharField(max_length=150)
    games = models.ManyToManyField(Game, related_name='collection')
    slug: str = models.SlugField(unique=True)
    url: str = models.URLField(max_length=250)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'{slugify(self.name, allow_unicode=True)}{unique_slugify(self, self.slug)}'

        if not self.url:
            self.url = f'http://127.0.0.1:8000/collection/{self.slug}'
        super(Collection, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.url)
