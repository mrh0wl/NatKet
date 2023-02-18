from typing import Any, Union

from django.db import models

from api.models import Game


class RatingOrg(models.IntegerChoices):
    ESRB = 1, 'ESRB'
    PEGI = 2, 'PEGI'
    CERO = 3, 'CERO'
    USK = 4, 'USK'
    GRAC = 5, 'GRAC'
    CLASS_IND = 6, 'CLASSIND'
    ACB = 7, 'ACB'


class PlatformType(models.IntegerChoices):
    CONSOLE = 1
    ARCADE = 2
    PLATFORM = 3
    OPERATING_SYSTEM = 4
    PORTABLE_CONSOLE = 5
    COMPUTER = 6


class Rating(models.IntegerChoices):
    THREE = 1, '3'
    SEVEN = 2, '7'
    TWELVE = 3, '12'
    SIXTEEN = 4, '16'
    EIGHTEEN = 5, '18'
    RP = 6, 'RP'
    EC = 7, 'EC'
    E = 8, 'E'
    E10 = 9, 'E10+'
    T = 10, 'T'
    M = 11, 'M'
    AO = 12, 'AO'
    CERO_A = 13, 'A'
    CERO_B = 14, 'B'
    CERO_C = 15, 'C'
    CERO_D = 16, 'D'
    CERO_Z = 17, 'Z'
    USK_0 = 18, '0'
    USK_6 = 19, '6'
    USK_12 = 20, '12'
    USK_18 = 21, '18'
    GRAC_ALL = 22, 'ALL'
    GRAC_TWELVE = 23, '12'
    GRAC_FIFTEEN = 24, '15'
    GRAC_EIGHTEEN = 25, '18'
    GRAC_TESTING = 26, 'TESTING'
    CLASS_IND_L = 27, 'L'
    CLASS_IND_TEN = 28, '10'
    CLASS_IND_TWELVE = 29, '12'
    CLASS_IND_FOURTEEN = 30, '14'
    CLASS_IND_SIXTEEN = 31, '16'
    CLASS_IND_EIGHTEEN = 32, '18'
    ACB_G = 33, 'G'
    ACB_PG = 34, 'PG'
    ACB_M = 35, 'M'
    ACB_MA15 = 36, 'MA15'
    ACB_R18 = 37, 'R18'
    ACB_RC = 38, 'RC'


class Regions(models.IntegerChoices):
    EUROPE = 1, 'EU'
    NORTH_AMERICA = 2, 'NA'
    AUSTRALIA = 3, 'AU'
    NEW_ZEALAND = 4, 'NZ'
    JAPAN = 5, 'JP'
    CHINA = 6, 'CH'
    ASIA = 7, 'AS'
    WORLDWIDE = 8, 'WW'
    KOREA = 9, 'KR'
    BRAZIL = 10, 'BR'


class Categories(models.IntegerChoices):
    MAINGAME = 0, 'MG'
    DLC = 1, 'DLC'
    EXPANSION = 2, 'EXP'
    BUNDLE = 3, 'BD'
    STANDALONE_EX = 4, 'SEXP'
    MOD = 5, 'MOD'
    EPISODE = 6, 'EP'
    SEASON = 7, 'S'
    REMAKE = 8, 'RM'
    REMASTER = 9, 'RMA'
    EXPANDED = 10, 'EG'
    PORT = 11, 'P'
    FORK = 12, 'F'
    PACK = 13, 'PCK'
    UPDATE = 14, 'U'


class Status(models.IntegerChoices):
    RELEASED = 0, 'F'
    ALPHA = 2, 'A'
    BETA = 3, 'B'
    EARLY = 4, 'E'
    OFFLINE = 5, 'O'
    CANCELLED = 6, 'C'
    RUMORED = 7, 'R'
    DELISTED = 8, 'D'


class AgeRating(models.Model):
    category: str = models.TextField(max_length=8)
    rating: str = models.TextField(max_length=8)

    def __str__(self):
        return f'{self.category} {self.rating}'


class BaseTags(models.Model):
    name: str = models.TextField(max_length=100)
    slug: str = models.SlugField(unique=True)
    url: str = models.URLField(max_length=250)

    class Meta:
        abstract = True


class Genres(BaseTags):
    """ Genres of the game """


class Category(BaseTags):
    """ Categories of the game """


class Theme(BaseTags):
    """ Themes of the game """


class Game(models.Model):
    name: str = models.TextField(max_length=100, blank=True)
    slug: str = models.SlugField(unique=True, blank=True)
    genres: Any = models.ManyToManyField(Genres)
    themes: Any = models.ManyToManyField(Theme)
    category: str = models.TextField(
        max_length=4,
        choices=Game.Type.choices,
        default=Game.Type.MAINGAME
    )
    age_ratings: Union[str] = models.ManyToManyField(AgeRating)

    def __str__(self):
        return self.name
