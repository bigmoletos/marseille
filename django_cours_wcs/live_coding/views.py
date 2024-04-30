# from django.contrib import admin
# from django.urls import path
# from api.views import index

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import seaborn
from .serializers import ImageSerializer, ObjectifSerializer
from rest_framework import status

@api_view(["GET"])
def index(request):
    data = {"Objectif": "Décrocher un job payé 4000K par mois minimum"}
    titanic = seaborn.load_dataset(
        "titanic").dropna().to_dict(orient="records")
    return Response(titanic)

@api_view(["GET"])
def objectif(request):
    donnees = Objectif.objects.all()
    serializer = ObjectifSerializer(donnees, many=True)
    return Response(serializer.data)

@api_view(["POST"])
def ajoutObjectif(request):
    serializer = ObjectifSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

