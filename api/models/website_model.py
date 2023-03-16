from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .creation_update_model import CreatedUpdatedAt


class Website(CreatedUpdatedAt):
    class Link(models.TextChoices):
        OFFICIAL = "Official", _('Official Website')
        WIKIA = "Wikia", _('Fandom Wiki')
        WIKIPEDIA = "Wikipedia", 'Wikipedia'
        FACEBOOK = "Facebook", 'Facebook'
        TWITTER = "Twitter", 'Twitter'
        TWITCH = "Twitch", 'Twitch'
        INSTAGRAM = "Instagram", 'Instagram'
        YOUTUBE = "Youtube", 'Youtube'
        IPHONE = "Iphone", 'App Store (iPhone)'
        IPAD = "Ipad", 'App Store (iPad)'
        ANDROID = "Android", 'Google Play'
        STEAM = "Steam", 'Steam'
        REDDIT = "Reddit", 'Subreddit'
        ITCH = "Itch", 'Itch.io'
        EPICGAMES = "Epicgames", 'Epic Games'
        GOG = "Gog", 'GoG'
        DISCORD = "Discord", _('Official Discord')

    game: Any = models.ForeignKey('api.Game', on_delete=models.CASCADE, related_name='websites')
    category: int = models.CharField(max_length=100, choices=Link.choices)
    trusted: bool = models.BooleanField(default=False)
    url: str = models.URLField(max_length=500)
