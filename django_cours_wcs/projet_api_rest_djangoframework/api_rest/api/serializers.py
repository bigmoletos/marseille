# Importation des modules nécessaires
from api.models import Image, Objectif, Traduction
from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Image.
    Convertit les instances de modèle Image en représentations JSON et vice versa.
    """
    class Meta:
        model = Image  # Spécifie le modèle à sérialiser
        fields = "__all__"  # Spécifie que tous les champs du modèle doivent être inclus

#    visualisation image
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        else:
            return None

class ObjectifSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Objectif.
    Convertit les instances de modèle Objectif en représentations JSON et vice versa.
    """
    class Meta:
        model = Objectif  # Spécifie le modèle à sérialiser
        # fields = "__all__"  # Spécifie que tous les champs du modèle doivent être inclus
        exclude=["id"]
    # include = (colonne1, colonne2...)  # Exemple de comment spécifier les champs à inclure
    # exclude = (colonne1, colonne2...)  # Exemple de comment spécifier les champs à exclure


class TraductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traduction  # Spécifiez le modèle ici
        # fields=["phrase"]
        fields = '__all__'  # Ou spécifiez les champs que vous voulez inclure