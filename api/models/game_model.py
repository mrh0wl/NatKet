from typing import Any

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from api.fields import UCDateTimeField
from api.models.creation_update_model import CreatedUpdatedAt

from .age_rating_model import AgeRating
from .image_model import Cover
from .object_imagefield import unique_slugify
from .related_model import GameMode, Genre, Keyword, Tag, Theme


class Game(CreatedUpdatedAt):
    """ Model for Games """

    # Type of the current game
    class Type(models.TextChoices):
        MAINGAME = 'MainGame', _('Main Game')
        DLC = 'DLC', _('DLC Addon')
        EXPANSION = 'Expansion', _('Expansion')
        BUNDLE = 'Bundle', _('Bundle')
        STANDALONE_EX = 'StandaloneExpansion', _('Standalone Expansion')
        MOD = 'Mod', _('Mod')
        EPISODE = 'Episode', _('Episode')
        SEASON = 'Season', _('Season')
        REMAKE = 'Remake', _('Remake')
        REMASTER = 'Remaster', _('Remaster')
        EXPANDED = 'ExpandedGame', _('Expanded Game')
        PORT = 'Port', _('Port')
        FORK = 'Fork', _('Fork')
        PACK = 'Pack', _('Pack')
        UPDATE = 'Update', _('Update')

    # Status of the current game
    class Status(models.TextChoices):
        RELEASED = 'Released', _('Released')
        ALPHA = 'Alpha', _('Alpha')
        BETA = 'Beta', _('Beta')
        EARLY = 'EarlyAccess', _('Early Access')
        OFFLINE = 'Offline', _('Offline')
        CANCELLED = 'Cancelled', _('Cancelled')
        RUMORED = 'Rumored', _('Rumored')
        DELISTED = 'Delisted', _('Delisted')

    title: str = models.CharField(max_length=100)
    player_perspectives: Any = models.ManyToManyField('api.PlayerPerspective')
    summary: str = models.CharField(max_length=5000, null=True, blank=True, default=None)
    story_line: str = models.CharField(max_length=5000, null=True, blank=True, default=None)
    cover: Any = models.ForeignKey(Cover, on_delete=models.CASCADE, null=True, blank=True)
    dlcs: Any = models.ManyToManyField('self')
    similar_games: Any = models.ManyToManyField('self')
    expanded_games: Any = models.ManyToManyField('self')
    standalone_expansions: Any = models.ManyToManyField('self')
    expansions: Any = models.ManyToManyField('self')
    remakes: Any = models.ManyToManyField('self')
    remasters: Any = models.ManyToManyField('self')
    age_ratings: Any = models.ManyToManyField(AgeRating)
    game_modes: Any = models.ManyToManyField(GameMode)
    genres: Any = models.ManyToManyField(Genre)
    keywords: Any = models.ManyToManyField(Keyword)
    themes: Any = models.ManyToManyField(Theme)
    tags: Any = models.ManyToManyField(Tag)
    slug: str = models.SlugField(
        unique=True,
        verbose_name=_("slug"),
        allow_unicode=True,
        max_length=255,
    )
    first_release = UCDateTimeField(
        auto_created=False,
        auto_now=False,
        auto_now_add=False,
        null=True
    )
    type: str = models.CharField(
        max_length=50,
        choices=Type.choices,
    )
    status: str = models.CharField(
        max_length=50,
        choices=Status.choices,
    )

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ['title']

    def _create_tags(self):
        for field_name in ('genres', 'keywords', 'themes'):
            for related_obj in getattr(self, field_name).all():
                tag_obj = Tag.objects.create(
                    type_id=getattr(Tag.Type, field_name[:-1].upper()),
                    endpoint_id=related_obj.id
                )
                self.tags.add(tag_obj)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f'{unique_slugify(self, slugify(self.title, allow_unicode=True))}'

        super(Game, self).save(*args, **kwargs)

        if not self.tags.exists():
            self._create_tags()

    def __str__(self):
        return str(self.title)
