import re
import pathlib
from os.path import exists
from typing import Any

import requests
from django.db import models
from django.conf import settings

from .creation_update_model import CreatedUpdatedAt
from .region_model import LocaleCover


class ImageBase(CreatedUpdatedAt):
    animated: bool = models.BooleanField(default=False)
    height: int = models.PositiveIntegerField()
    width: int = models.PositiveIntegerField()
    filename: str = models.SlugField(unique=True, null=True, max_length=100)
    url: str = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.url:
            folder_name = f'{self.__class__.__name__.lower()}s'
            self.url = f'http://127.0.0.1:8000/static/{folder_name}/{self.filename}.jpg'
        super(ImageBase, self).save(*args, **kwargs)

    def get_image_from_url(self, url: str, filename: str):
        pattern = r'(http|ftp|https)?:?//([\w_-]+(?:(?:.[\w_-]+)+)[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'
        reg_match = re.match(pattern, url)
        schema = reg_match[1] or 'http://'
        url_body = reg_match[2]
        class_name = self.__class__.__name__.lower()
        self.filename = f'{class_name}-{filename}'
        file_ext = pathlib.Path(url_body).suffix
        full_filename = self.filename+file_ext

        full_root = settings.STATIC_ROOT.joinpath(f'{class_name}s')
        full_root.mkdir(parents=True, exist_ok=True)
        full_root = full_root.joinpath(full_filename)

        if not exists(full_root):
            with open(full_root, 'wb') as handle:
                response = requests.get(schema+url_body, stream=True)

                if not response.ok:
                    print('Error getting:', filename)

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)
        return self


class PlatformLogo(ImageBase):
    alpha_channel = models.BooleanField(default=False)


class Cover(ImageBase):
    locale_cover: Any = models.ManyToManyField(LocaleCover)


class Thumbnail(ImageBase):
    """ Thumbnail for each game """
