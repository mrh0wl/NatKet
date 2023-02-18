from django.utils import timezone
from django.db import models
from api.fields import UCDateTimeField


class CreatedUpdatedAt(models.Model):
    created_at: timezone.datetime = UCDateTimeField(auto_now_add=True, editable=False)
    updated_at: timezone.datetime = UCDateTimeField(auto_now=True)

    class Meta:
        abstract = True
