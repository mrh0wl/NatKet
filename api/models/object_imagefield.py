import contextlib
from urllib.request import urlopen

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models

from .creation_update_model import CreatedUpdatedAt


def unique_slugify(instance, slug: str):
    model = instance.__class__
    unique_slug = slug
    if model.objects.filter(slug=unique_slug).exists():
        unique_slug, last_char = (slug.split('--')[0], slug.split('--')[-1])
        try:
            i = int(last_char)
            unique_slug += f'{i+1}'
        except ValueError:
            unique_slug += '--1'
    return unique_slug


class ObjectWithImageField(models.Model):
    image: str = models.ImageField(upload_to='static/{}', null=True, blank=True)
    image_url: str = models.URLField(blank=True, null=True)

    def get_image_from_url(self, url):
        img_tmp = NamedTemporaryFile(delete=True)
        with urlopen(url) as uo:
            assert uo.status == 200
            img_tmp.write(uo.read())
            img_tmp.flush()
        img = File(img_tmp)
        self.image.save(img_tmp.name, img)
        self.image_url = url
