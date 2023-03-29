from django.db import models
from .creation_update_model import CreatedUpdatedAt


class AgeRating(CreatedUpdatedAt):
    """ Age Rating according to various rating organizations """
    class Organizations(models.TextChoices):
        ESRB = 'ESRB', 'ESRB'
        PEGI = 'PEGI', 'PEGI'
        CERO = 'CERO', 'CERO'
        USK = 'USK', 'USK'
        GRAC = 'GRAC', 'GRAC'
        CLASSIND = 'CLASSIND', 'CLASSIND'
        ACB = 'ACB', 'ACB'

    rating = models.CharField(max_length=8)
    organization = models.CharField(
        max_length=8,
        choices=Organizations.choices,
        default=Organizations.ESRB,
    )

    class Meta:
        ordering = ['rating']

    def __str__(self):
        return f'{self.organization} {self.rating}'

    def __repr__(self):
        return f'<Age Rating: {self.organization} {self.rating}>'
