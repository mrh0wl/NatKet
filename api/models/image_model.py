import re
import pathlib
from os.path import exists
from typing import Any, Union

import requests
from django.db import models
from django.conf import settings

from .creation_update_model import CreatedUpdatedAt
from django.core.files.images import get_image_dimensions


class ImageBase(CreatedUpdatedAt):
    animated: bool = models.BooleanField(default=False, null=True)
    height: int = models.PositiveIntegerField(blank=True, null=True)
    width: int = models.PositiveIntegerField(blank=True, null=True)
    filename: str = models.SlugField(null=True, blank=True, max_length=100)
    url: str = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if 'http://127.0.0.1:8000/static/' not in self.url:
            self._get_image_from_url(url=self.url, filename=self.filename)
        else:
            self.filename = None
        folder_name = f'{self.__class__.__name__.lower()}s'
        self.url = f'http://127.0.0.1:8000/static/{folder_name}/{self.filename}.jpg'
        super(ImageBase, self).save(*args, **kwargs)

    def _get_image_from_url(self, url: Union[str, None], filename: str):
        pattern = r'(http|ftp|https)?:?//([\w_-]+(?:(?:.[\w_-]+)+)[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'
        reg_match = re.match(pattern, url)
        schema = f'{reg_match[1]}://' if reg_match[1] else 'https://'
        url_body = reg_match[2].replace('t_thumb', 't_cover_big')
        class_name = self.__class__.__name__.lower()
        self.filename = f'{filename}'
        file_ext = pathlib.Path(url_body).suffix
        full_filename = self.filename+file_ext

        full_root = pathlib.Path(settings.STATIC_ROOT).joinpath(f'{class_name}s')
        full_root.mkdir(parents=True, exist_ok=True)
        full_root = full_root.joinpath(full_filename)

        if not exists(full_root):
            with open(full_root, 'wb') as handle:
                response = requests.get(schema+url_body)

                if not response.ok:
                    print('Error getting:', response.url, f'for {class_name} image ({response.status_code})')
                    return

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

        self.width, self.height = get_image_dimensions(full_root)


class LocaleCover(ImageBase):
    """ Locale Cover for each alternative title"""


class Cover(ImageBase):
    """ Cover for each game"""


class Thumbnail(ImageBase):
    """ Thumbnail for each game """
    game: Any = models.ForeignKey("api.Game", on_delete=models.CASCADE, related_name='thumbnails')
