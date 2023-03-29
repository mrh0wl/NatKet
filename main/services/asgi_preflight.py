import os

from django.apps import apps
from django.conf import settings

# Export Django settings env variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

apps.populate(settings.INSTALLED_APPS)
