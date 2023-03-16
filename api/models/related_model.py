from django.db import models
from django.utils.text import slugify

from .creation_update_model import CreatedUpdatedAt
from .object_imagefield import unique_slugify


class RelatedBase(CreatedUpdatedAt):
    name: str = models.TextField(max_length=200)
    slug: str = models.SlugField(max_length=150, unique=True)
    url: str = models.URLField(max_length=250)

    class Meta:
        abstract = True
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'{slugify(self.name)}{unique_slugify(self, self.slug)}'

        super(RelatedBase, self).save(*args, **kwargs)


class Genre(RelatedBase):
    """ Genres of the game """


class Keyword(RelatedBase):
    """ Keywords of the game """


class Theme(RelatedBase):
    """ Themes of the game """


class Multiplayer(CreatedUpdatedAt):
    campaign_coop: bool = models.BooleanField(default=False)
    drop_in: bool = models.BooleanField(default=False)
    lan_coop: bool = models.BooleanField(default=False)
    offline_coop: bool = models.BooleanField(default=False)
    offline_coop_players: int = models.PositiveIntegerField(default=None, null=True, blank=True)
    offline_players: int = models.PositiveIntegerField(default=None, null=True, blank=True)
    online_coop: bool = models.BooleanField(default=False)
    online_coop_players: int = models.PositiveIntegerField(default=None, null=True, blank=True)
    online_players: int = models.PositiveIntegerField(default=None, null=True, blank=True)
    splitscreen: bool = models.BooleanField(default=False)
    splitscreen_online: bool = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.splitscreen_online:
            self.splitscreen_online = False
        super(Multiplayer, self).save(*args, **kwargs)


class PlayerPerspective(RelatedBase):
    """ Perspective interaction that the player has"""


class GameMode(RelatedBase):
    """ Game Modes of the game """


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
