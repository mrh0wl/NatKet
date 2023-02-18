from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .creation_update_model import CreatedUpdatedAt


class Links(CreatedUpdatedAt):
    class Websites(models.IntegerChoices):
        OFFICIAL = 0, _('Official Website')
        WIKIA = 1, _('Fandom Wiki')
        WIKIPEDIA = 2, 'Wikipedia'
        FACEBOOK = 3, 'Facebook'
        TWITTER = 4, 'Twitter'
        TWITCH = 5, 'Twitch'
        INSTAGRAM = 7, 'Instagram'
        YOUTUBE = 8, 'Youtube'
        IPHONE = 9, 'App Store (iPhone)'
        IPAD = 10, 'App Store (iPad)'
        ANDROID = 11, 'Google Play'
        STEAM = 12, 'Steam'
        REDDIT = 13, 'Subreddit'
        ITCH = 14, 'Itch.io'
        EPICGAMES = 15, 'Epic Games'
        GOG = 16, 'GoG'
        DISCORD = 17, _('Official Discord')

    game: Any = models.ForeignKey('api.Game', on_delete=models.CASCADE)
    category: int = models.IntegerField(choices=Websites.choices)
    trusted: bool = models.BooleanField(default=False)
    url: str = models.URLField(max_length=200)
