import contextlib
from typing import Any, Optional

import requests
from django.db import models
from django.utils.translation import gettext_lazy as _
from langcodes import Language as Lang

from .creation_update_model import CreatedUpdatedAt


class Language(CreatedUpdatedAt):
    locale: str = models.CharField(max_length=10, null=True, unique=True)
    name: str = models.CharField(max_length=100, null=True, unique=True)
    native_name: str = models.CharField(max_length=100, null=True)

    def save(self, language: Optional[str] = None, *args, **kwargs):
        if language and not self.locale:
            language = language.split()[0]
            if language.capitalize() not in ['Spanish', 'English']:
                with contextlib.suppress(Exception):
                    lang_code = Lang.find(language).language

                    req = requests.get(f'https://restcountries.com/v3.1/lang/{language}')
                    res = req.json()
                    country_code = res[0]
                    self.locale = f'{lang_code}-{country_code}'
        if not self.native_name and self.locale:
            self.native_name = Lang.get(self.locale).autonym()
        if (not self.name or ('-' in self.locale and '(' not in self.name)) and self.locale:
            lang = Lang.get(self.locale)
            self.name = lang.display_name()

        super(Language, self).save(*args, **kwargs)

    class Meta:
        ordering = ['locale']


class SupportType(CreatedUpdatedAt):
    class Enum(models.TextChoices):
        AUDIO = 'Audio', _('Audio')
        SUBTITLES = 'Subtitles', _('Subtitles')
        INTERFACE = 'Interface', _('Interface')

    name: str = models.CharField(max_length=30, choices=Enum.choices)


class LanguageSupport(CreatedUpdatedAt):
    cover: Any = models.OneToOneField("api.LocaleCover", on_delete=models.CASCADE, null=True, blank=True)
    game: Any = models.ForeignKey("api.Game", on_delete=models.CASCADE, related_name="language_supports")
    support_types: Any = models.ManyToManyField("api.SupportType")
    language: Any = models.ForeignKey("api.Language", on_delete=models.CASCADE, null=True)


class LanguageTitle(CreatedUpdatedAt):
    title: str = models.CharField(max_length=100, null=True)
    description: str = models.CharField(max_length=100, null=True)
    language_support: Any = models.ForeignKey("api.LanguageSupport", on_delete=models.CASCADE, related_name="language_titles")
