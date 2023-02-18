from typing import Any

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from api.fields import UCDateTimeField
from api.models.creation_update_model import CreatedUpdatedAt

from .age_rating_model import AgeRating
from .image_model import Cover
from .language_model import LanguageSupport
from .object_imagefield import unique_slugify
from .related_model import GameModes, Genre, Keyword, Tag, Theme
from .release_date_model import ReleaseDate


class Game(CreatedUpdatedAt):
    """ Model for Games """

    # Type of the current game
    class Type(models.TextChoices):
        MAINGAME = 'MG', _('Main Game')
        DLC = 'DLC', _('DLC Addon')
        EXPANSION = 'EXP', _('Expansion')
        BUNDLE = 'BD', _('Bundle')
        STANDALONE_EX = 'SEXP', _('Standalone Expansion')
        MOD = 'MOD', _('Mod')
        EPISODE = 'EP', _('Episode')
        SEASON = 'S', _('Season')
        REMAKE = 'RM', _('Remake')
        REMASTER = 'RMA', _('Remaster')
        EXPANDED = 'EG', _('Expanded Game')
        PORT = 'P', _('Port')
        FORK = 'F', _('Fork')
        PACK = 'PCK', _('Pack')
        UPDATE = 'U', _('Update')

    # Status of the current game
    class Status(models.TextChoices):
        RELEASED = 'F', _('Released')
        ALPHA = 'A', _('Alpha')
        BETA = 'B', _('Beta')
        EARLY = 'E', _('Early')
        OFFLINE = 'O', _('Offline')
        CANCELLED = 'C', _('Cancelled')
        RUMORED = 'R', _('Rumored')
        DELISTED = 'D', _('Delisted')

    title: str = models.CharField(max_length=100)
    summary: str = models.CharField(max_length=1500, null=True, blank=True, default=None)
    story_line: str = models.CharField(max_length=1500, null=True, blank=True, default=None)
    cover: Any = models.OneToOneField(Cover, on_delete=models.CASCADE, null=True, blank=True)
    # dlcs: Any = models.ForeignKey('self', on_delete=models.CASCADE, related_name='dlc')
    # similar_games: Any = models.ForeignKey('self', on_delete=models.CASCADE, related_name='similar_game')
    # expanded_games: Any = models.ForeignKey('self', on_delete=models.CASCADE, related_name='expanded_game')
    # standalone_expansions: Any = models.ForeignKey('self', on_delete=models.CASCADE, related_name='standalone_expansion')
    # expansions: Any = models.ForeignKey('self', on_delete=models.CASCADE, related_name='expansion')
    # remakes: Any = models.ForeignKey('self', on_delete=models.CASCADE, related_name='remake')
    # remasters: Any = models.ForeignKey('self', on_delete=models.CASCADE, related_name='remaster')
    age_ratings: Any = models.ManyToManyField(AgeRating)
    # game_modes: Any = models.ManyToManyField(GameModes)
    # language_supports: Any = models.ManyToManyField(LanguageSupport)
    release_dates: Any = models.ManyToManyField(ReleaseDate)
    genres: Any = models.ManyToManyField(Genre)
    keywords: Any = models.ManyToManyField(Keyword)
    themes: Any = models.ManyToManyField(Theme)
    tags: Any = models.ManyToManyField(Tag)
    slug: str = models.SlugField(
        unique=False,
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
        max_length=4,
        choices=Type.choices,
    )
    status: str = models.CharField(
        max_length=4,
        choices=Status.choices,
    )

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ['-first_release']

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
            self.slug = f'{slugify(self.title, allow_unicode=True)}{unique_slugify(self, self.slug)}'

        super(Game, self).save(*args, **kwargs)

        if not self.tags.exists():
            self._create_tags()

    def __str__(self):
        return str(self.title)
