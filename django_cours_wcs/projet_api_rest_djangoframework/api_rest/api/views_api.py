from django.shortcuts import render
from django.conf import settings
from api.models import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from googletrans import Translator
import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import tensorflow as tf

tf.compat.v1.logging.set_verbosity  # Pour masquer les avertissements de TensorFlow
import logging

logging.getLogger("tensorflow").setLevel(
    logging.ERROR
)  # Pour masquer les avertissements de Keras


def vgg16(file_path, top=5):
    """
    Utilise le modèle VGG16 pré-entraîné pour prédire les étiquettes d'une image donnée.

    Args:
        imageURL: URL de l'image à analyser.
        top: Nombre de meilleures prédictions à retourner.

    Returns:
        Un dictionnaire contenant les identifiants, noms et probabilités des meilleures prédictions.
    """

    # from googletrans import Translator
    from keras.preprocessing.image import load_img, img_to_array
    from keras.applications.vgg16 import preprocess_input, decode_predictions
    import pandas as pd
    from keras.applications.vgg16 import VGG16

    # file_path   ='./sleepy_siberian_tiger.jpg'
    # file_path = os.path.join(settings.BASE_DIR, "C:/programmation/IA\Projet_Méteo/projet_meteo/Projet_Meteo/django/projet_api_rest_djangoframework/api_rest/api/sleepy_siberian_tiger.jpg")

    # Chargement du modèle VGG16 pré-entraîné.
    modelVGG16 = VGG16()
    # Chargement et préparation de l'image.
    print(f"depuis VGG16 file_path   {file_path} ")
    # charge l’image du chemin du fichier spécifié, et redimensionne l’image à une taille de (224, 224).
    image = load_img(file_path, target_size=(224, 224))
    # convertit l’image chargée en un tableau numpy
    imageArray = img_to_array(image)
    # redimensionne le tableau de l’image pour qu’il ait une dimension supplémentaire au début. C’est nécessaire parce que le modèle VGG16 s’attend à recevoir plusieurs images à la fois (sous forme de tableau 4D)
    imageReshape = imageArray.reshape(
        1, imageArray.shape[0], imageArray.shape[1], imageArray.shape[2]
    )
    # prétraitement nécessaire sur l’image avant de la passer au modèle VGG16
    imagePreprocess = preprocess_input(imageReshape)
    # Prédiction des étiquettes pour l'image.
    # label = decode_predictions(modelVGG16.predict(imagePreprocess), top=top)
    # prediction = modelVGG16.predict(imagePreprocess)
    # label = decode_predictions(prediction)
    # # label = label[0][0]
    # # print('%s (%.2f%%)' % (label[1], label[2]*100))
    # # Retourne les prédictions sous forme de dictionnaire.
    # # return pd.DataFrame(label[0], columns=["id", "nom", "proba"]).to_dict()
    # return pd.DataFrame(label[0],columns=["id", "nom", "proba"]).to_dict()
    # Prédiction des étiquettes pour l'image.
    prediction = modelVGG16.predict(imagePreprocess)
    label = decode_predictions(prediction, top=top)[0]
    # Convertir les prédictions en une liste de dictionnaires
    predictions = [
        {"id": id, "nom": nom, "proba": proba * 100} for id, nom, proba in label
    ]
    # Crée un objet traducteur
    translator = Translator()

    # Traduit chaque prédiction en français
    for prediction in predictions:
        try:
            print(f"prediction['nom']--------  {prediction['nom']} ")
            prediction['nom'] = translator.translate(prediction['nom'], dest='fr').text
            print(f"traduction fr---------  {prediction['nom']} ")
        except Exception as e:
            print(f"Erreur lors de la traduction : {str(e)}")
            # En cas d'erreur, conserve le nom en anglais
            # prediction['nom'] = "Erreur lors de la traduction"

    return predictions


def predictionImage(request):
    """
    Traite les requêtes POST pour l'upload d'images et utilise le modèle VGG16 pour prédire les étiquettes.
    Affiche les résultats sur la page 'predictionImage.html' ou renvoie une erreur si nécessaire.

    Args:
        request: La requête HTTP.

    Returns:
        Un HttpResponse avec le rendu de la page 'predictionImage.html' ou 'error.html'.
    """
    # Message par défaut en cas d'absence d'upload.
    message = ""
    if request.method == "POST":
        # Récupération de l'image uploadée.
        imageUploade = request.FILES.get("monImage")
        # Sauvegarde de l'image dans la base de données.
        imageSauvegarde = Image(image=imageUploade, createur=1)
        fs = FileSystemStorage()
        filename = fs.save(imageUploade.name, imageUploade)
        image_url = fs.url(filename)
        # Création de l'objet Image et sauvegarde dans la base de données.
        imageSauvegarde = Image(image=image_url, createur=1)
        imageSauvegarde.save()

        # Construction du chemin de fichier sur le système de fichiers.
        file_path = fs.path(filename)

        # imageSauvegarde.save()
        message = f"L'image >>{imageUploade}<< a bien été sauvegardée !!"

        # Utilisation de VGG16 pour la prédiction.
        prediction = vgg16(file_path, top=5)
        return render(request, "predictionImage.html", {"prediction": prediction})
    else:
        # Pour les requêtes GET, affiche simplement la page de formulaire d'upload.
        return render(request, "predictionImage.html")

    #     # Recherche de l'image dans la base de données.
    #     # images = Image.objects.filter(image=imageUploade)
    #     if images:
    #         # Si l'image est trouvée, utilisation de VGG16 pour la prédiction.
    #         imageURL = images[0].image.url
    #         prediction = vgg16(file_path, top=5)
    #         # prediction = vgg16(imageURL, top=5)
    #         return render(request, "predictionImage.html", {'prediction': prediction})
    #     else:
    #         # Si aucune image correspondante n'est trouvée, affiche une page d'erreur.
    #         return render(request, "error.html", {'message': 'Aucune image correspondante trouvée.'})
    # else:
    #     # Pour les requêtes GET, affiche simplement la page de formulaire d'upload.
    #     return render(request, "predictionImage.html")
