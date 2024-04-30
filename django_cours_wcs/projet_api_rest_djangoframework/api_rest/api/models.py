# Importation du module models de Django
from django.db import models

class Image(models.Model):
    """
    Modèle Django pour une image.
    """
    # image = models.ImageField(upload_to='media')  # Champ pour stocker une image dans le dossier media
    image = models.ImageField()  # Champ pour stocker une image dans le dossier media
    createur = models.IntegerField()  # Champ pour stocker l'ID du créateur de l'image
    dateCreation = models.DateTimeField(auto_now=True)  # Champ pour stocker la date de création de l'image, mise à jour automatiquement à chaque sauvegarde de l'objet

class Objectif(models.Model):
    """
    Modèle Django pour un objectif.
    """
    titre = models.CharField(max_length=100)  # Champ pour stocker le titre de l'objectif, avec une longueur maximale de 100 caractères
    date = models.DateField(null=True)  # Champ pour stocker la date de l'objectif, peut être null
    statut = models.BooleanField()  # Champ pour stocker le statut de l'objectif, soit True (réalisé) soit False (non réalisé)
    priorite = models.BigIntegerField()  # Champ pour stocker la priorité de l'objectif, sous forme d'un grand nombre entier (par exemple, 1234)


class Traduction(models.Model):
    phrase=models.CharField(max_length=200)
    traduction=models.CharField(max_length=200, null=True, blank=True)
