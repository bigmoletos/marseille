# Importation des modules nécessaires
from django.contrib import admin
from api.models import Image, Objectif

class champsImage(admin.ModelAdmin):
    """
    Classe d'administration pour le modèle Image.
    Elle permet de personnaliser l'affichage du modèle Image dans l'interface d'administration de Django.
    """
    # Affiche tous les champs du modèle Image dans l'interface d'administration
    list_display = [champ.name for champ in Image._meta.get_fields()]

class champsObjectif(admin.ModelAdmin):
    """
    Classe d'administration pour le modèle Objectif.
    Elle permet de personnaliser l'affichage du modèle Objectif dans l'interface d'administration de Django.
    """
    # Affiche tous les champs du modèle Objectif dans l'interface d'administration
    list_display = [champ.name for champ in Objectif._meta.get_fields()]

# Enregistrement des modèles Image et Objectif dans l'interface d'administration de Django
admin.site.register(Image, champsImage)
admin.site.register(Objectif, champsObjectif)

