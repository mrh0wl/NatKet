from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .creation_update_model import CreatedUpdatedAt


class Links(CreatedUpdatedAt):
    class Websites(models.TextChoices):
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

    game: Any = models.ForeignKey('api.Game', on_delete=models.CASCADE, related_name='links')
    category: int = models.IntegerField(choices=Websites.choices)
    trusted: bool = models.BooleanField(default=False)
    url: str = models.URLField(max_length=200)
