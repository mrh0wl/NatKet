# app/urls.py
from django.urls import path
from .views import home
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
