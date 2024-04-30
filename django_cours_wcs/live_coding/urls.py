from django.contrib import admin
from django.urls import path
from api.views import index, objectif, ajoutObjectif

urlpatterns = [
    path("admin/", admin.site.urls),
    path("index/", index, name="index"),
    path("objectif/", objectif, name="objectif"),
    path("ajoutObjectif/", ajoutObjectif, name="ajoutObjectif"),
]
