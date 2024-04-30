from api.models import Image, Objectif
from rest_framework import serializers

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"

class ObjectifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objectif
        fields = "__all__"
    # include = (colonne1, colonne2...)
    # exclude = (colonne1, colonne2...)
