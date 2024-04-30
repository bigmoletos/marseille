# pylint: disable=relative-beyond-top-level
# Importation des modules nécessaires
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import seaborn
from .serializers import ImageSerializer, ObjectifSerializer, TraductionSerializer
from rest_framework import status, viewsets, serializers
from api.models import Objectif, Image, Traduction
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from  transformers import pipeline #, MarianMTModel, MarianTokenizer
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf

# impportztion du model de traduction depuis huggingFace
# modelTraduction=pipeline("translation", model="kwang123/medical-mt-fr-en")
modelTraduction = pipeline("translation_fr_to_en", model="kwang123/medical-mt-fr-en")
# modelTraduction = pipeline("translation_fr_to_en", model="kwang123/medical-mt-fr-en", from_pt=True)
# model_name = 'kwang123/medical-mt-fr-en'
# tokenizer = MarianTokenizer.from_pretrained(model_name)
# modelTraduction = MarianMTModel.from_pretrained(model_name)

class Pagination(PageNumberPagination):
    """
    Définit la pagination pour les vues qui nécessitent une division des résultats en pages.
    """
    page_size = 3

@api_view(["GET"])
def index(request):
    """
    Vue pour la requête GET à l'endpoint 'index'.
    Renvoie un jeu de données Titanic après avoir supprimé les valeurs manquantes.
    """
    data = {"Objectif": "Décrocher un job payé 10000K par mois minimum"}
    titanic = seaborn.load_dataset("titanic").dropna().to_dict(orient="records")
    # pagination_class = Pagination
    return Response(titanic)


@api_view(["GET"])
def objectif(request):
    """
    Vue pour la requête GET à l'endpoint 'objectif'.
    Récupère tous les objets du modèle Objectif, les sérialise et renvoie les données sérialisées.
    """
    donnees = Objectif.objects.all()
    serializer = ObjectifSerializer(donnees, many=True)
    pagination_class = Pagination
    return Response(serializer.data)


@api_view(["POST"])
def ajoutObjectif(request):
    """
    Vue pour la requête POST à l'endpoint 'ajoutObjectif'.
    Crée un sérialiseur pour les données de la requête, vérifie si le sérialiseur est valide,
    et si c'est le cas, sauvegarde les données et renvoie les données sérialisées.
    """
    serializer = ObjectifSerializer(data=request.data)
    pagination_class = Pagination
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def afficher_images(request):
    """
    Vue pour la requête GET à l'endpoint 'afficher_images'.
    Récupère toutes les images du modèle Image, les sérialise et renvoie les données sérialisées.
    """
    images = Image.objects.all()
    serializer = ImageSerializer(images, many=True, context={'request': request})
    pagination_class = Pagination
    return Response(serializer.data)



class ObjectifTousLesVerbesHttp(viewsets.ModelViewSet):
    """
    Vue générique pour le modèle Objectif. Permet d'effectuer des opérations CRUD sur les objectifs via l'API.
    """
    queryset = Objectif.objects.all()
    serializer_class = ObjectifSerializer
    filterset_fields = ["titre", "date", "priorite"]
    search_filters=[champ.name for champ in Objectif._meta.get_fields()]
    pagination_class = Pagination
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):

        # Votre logique pour supprimer un objectif ici
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = Objectif.objects.all()
        serializer = ObjectifSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = ObjectifSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = Objectif.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = ObjectifSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Objectif.objects.get(pk=pk)
        except Objectif.DoesNotExist:
            return Response(status=404)
        serializer = ObjectifSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    # def delete(self, request, pk=None):
    #     try:
    #         item = MonModel.objects.get(pk=pk)
    #     except MonModel.DoesNotExist:
    #         return Response(status=404)
    #     item.delete()
    #     return Response(status=204)


class ObjectifApiView(APIView):
    """
    API View pour gérer les objectifs avec les opérations CRUD.
    """
    serializer_class = ObjectifSerializer
    filterset_fields=["titre","date","priorite"]
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination

    def get(self, request):
        """
        Renvoie la liste de tous les objectifs.
        """
        donnees = Objectif.objects.all()
        serializer = ObjectifSerializer(donnees, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Ajoute un nouvel objectif à partir des données POST.
        """
        serializer = ObjectifSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Mise à jour d'un objectif. Cette implémentation est basique et nécessite d'être améliorée pour cibler un objectif spécifique.
        """
        serializer = ObjectifSerializer(data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
        # L'implémentation de la mise à jour (PUT) nécessite l'identification de l'objet spécifique à mettre à jour.
        return Response({"error": "Méthode PUT non implémentée."}, status=status.HTTP_501_NOT_IMPLEMENTED)





# ------
class TraductionApiView(APIView):
    """
    Vue API pour la gestion des traductions.
    Permet de récupérer la liste des traductions, d'ajouter une nouvelle traduction et de mettre à jour une traduction existante.
    """
    serializer_class = TraductionSerializer
    permission_classes = [IsAuthenticated,]
    pagination_class = Pagination

    def get(self, request):
        """
        Récupère et renvoie toutes les traductions enregistrées dans la base de données.
        """
        donnees = Traduction.objects.all()
        serializer = TraductionSerializer(donnees, many=True)
        # if serializer.is_valid():
        #     pass
        return Response(serializer.data)

    def post(self, request):
        """
        Crée une nouvelle traduction à partir des données fournies et enregistre la traduction dans la base de données.
        """
        serializer = TraductionSerializer(data=request.data)
        if serializer.is_valid():
            phrase = serializer.validated_data["phrase"]
            # Supposons l'existence de modelTraduction, une fonction ou méthode qui effectue la traduction.
            traduction = modelTraduction(phrase)[0]["translation_text"]
            # Création et enregistrement de la nouvelle traduction dans la base de données.
            traduction_instance = Traduction(phrase=phrase, traduction=traduction)
            traduction_instance.save()

            # Sérialisation de la nouvelle instance de Traduction pour la réponse HTTP.
            serializer = TraductionSerializer(traduction_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Si les données ne sont pas valides, renvoie les erreurs de sérialisation.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Met à jour une traduction existante. Cette méthode nécessite une logique supplémentaire pour identifier la traduction à mettre à jour.
        """
        serializer = ObjectifSerializer(data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
        # La mise à jour (PUT) d'une traduction spécifique nécessite l'identification de celle-ci via un identifiant ou un autre critère.
        return Response({"error": "Méthode PUT non implémentée."}, status=status.HTTP_501_NOT_IMPLEMENTED)