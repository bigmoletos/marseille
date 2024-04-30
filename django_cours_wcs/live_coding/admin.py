from django.contrib import admin
from api.models import Image, Objectif

class champsImage(admin.ModelAdmin):
    list_display = [champ.name for champ in Image._meta.get_fields()]

class champsObjectif(admin.ModelAdmin):
    list_display = [champ.name for champ in Objectif._meta.get_fields()]

admin.site.register(Image, champsImage)
admin.site.register(Objectif, champsObjectif)
