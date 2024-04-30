from django.contrib import admin
from django.urls import path
from api.views import index, objectif, ajoutObjectif, afficher_images
from api.views import ObjectifApiView, ObjectifTousLesVerbesHttp, TraductionApiView
from api.views_api import predictionImage

from django.conf import settings
from django.conf.urls.static import static
from django_filters import rest_framework as filters

"""
URL configuration for api_rest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("index/", index, name="index"),
    path("", index, name="index"),
    path("objectif/", objectif, name="objectif"),
    path("ajoutObjectif/", ajoutObjectif, name="ajoutObjectif"),
    path('images/', afficher_images, name='afficher_images'),
    path('ObjectifTousLesVerbesHttp/', ObjectifTousLesVerbesHttp.as_view(
        {'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'delete'})),
    # path('ObjectifApiView/', ObjectifApiView.as_view(
    #     {'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'delete'}), name='ObjectifApiView'),
    # path('TraductionApiView/', TraductionApiView.as_view(
    #     {'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'delete'}), name='TraductionApiView'),
    path('ObjectifApiView/', ObjectifApiView.as_view(),name='ObjectifApiView'),
    path('TraductionApiView/', TraductionApiView.as_view(),name='TraductionApiView'),
    path('predictionImage/', predictionImage ,name='predictionImage'),
]

# Si nous sommes en mode DEBUG (c'est-à-dire en développement),
# nous ajoutons les URL pour servir les fichiers média statiques.
# 'settings.MEDIA_URL' est l'URL qui sera utilisée pour accéder aux fichiers média.
# 'settings.MEDIA_ROOT' est le répertoire où les fichiers média sont stockés.
# 'static' est une fonction helper qui renvoie un pattern d'URL pour servir les fichiers statiques.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

