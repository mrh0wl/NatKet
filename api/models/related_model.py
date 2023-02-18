from typing import Any

from django.db import models

from .creation_update_model import CreatedUpdatedAt
from .platform_model import Platform
from .object_imagefield import unique_slugify


class RelatedBase(CreatedUpdatedAt):
    name: str = models.TextField(max_length=100)
    slug: str = models.SlugField(unique=True)
    url: str = models.URLField(max_length=250)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.slug)

        super(RelatedBase, self).save(*args, **kwargs)


class Genre(RelatedBase):
    """ Genres of the game """


class Keyword(RelatedBase):
    """ Keywords of the game """


class Theme(RelatedBase):
    """ Themes of the game """


class Multiplayer(CreatedUpdatedAt):
    campaign_coop: bool = models.BooleanField()
    drop_in: bool = models.BooleanField()
    lan_coop: bool = models.BooleanField()
    offline_coop: bool = models.BooleanField()
    offline_coop_players: bool = models.BooleanField()
    offline_players: int = models.PositiveIntegerField()
    online_coop: bool = models.BooleanField()
    online_coop_players: int = models.PositiveIntegerField()
    online_players: int = models.PositiveIntegerField()
    platform: Any = models.ForeignKey(Platform, on_delete=models.CASCADE)
    splitscreen: bool = models.BooleanField()


class PlayerPerspective(RelatedBase):
    """ Perspective interaction that the player has"""


class GameModes(RelatedBase):
    """ Game Modes of the game """
    multiplayer: Any = models.ForeignKey(Multiplayer, on_delete=models.CASCADE)
    player_perspective: Any = models.ManyToManyField(PlayerPerspective)


class Tag(CreatedUpdatedAt):
    class Type(models.IntegerChoices):
        THEME = 0
        GENRE = 1
        KEYWORD = 2
        GAME = 3

    type_id: int = models.PositiveIntegerField(choices=Type.choices)
    endpoint_id: int = models.PositiveIntegerField()
    value: int = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['value']

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.__gen_value()
        super(Tag, self).save(*args, **kwargs)

    def __gen_value(self):
        res = self.type_id << 28
        res |= self.endpoint_id
        return res

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'<Tag: {self.Type(self.type_id).label}>'
