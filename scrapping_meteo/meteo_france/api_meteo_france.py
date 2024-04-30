# pylint: disable=all
import sys
from pathlib import Path  # permet l'import des fonctions siuées dans d'autres répertoires,  il faut toujours le placer en premier
# sys.path.append(str(Path(__file__).resolve().parent.parent))
# from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
# Ajouter le dossier 'outils' au sys.path
sys.path.append(str(project_root / 'outils'))
import requests
from urllib.parse import quote, urlencode
import time
import configparser
from datetime import datetime, timedelta
from get_config_ini import lire_config_et_imprimer_cles_valeurs
from gestion_logging import reconfigurer_logging
from enregistrement_datasets import enregistrement_dataset_meteo_france
# from outils.get_config_ini import lire_config_et_imprimer_cles_valeurs
# from outils.gestion_logging import reconfigurer_logging
# from outils.enregistrement_datasets import enregistrement_dataset_meto_france
import logging
import os

logger = logging.getLogger('colorlog_example')

class ValidationError(Exception):
    """Exception personnalisée pour les erreurs de validation des paramètres."""
    pass

def valider_params(params):
    """
    Validation des paramètres en entrée selon les critères de l'API Météo France.

    Args:
        params (dict): Dictionnaire contenant les paramètres à valider.

    Raises:
        ValidationError: Si un des paramètres ne respecte pas les critères définis.

    Returns:
        bool: True si tous les paramètres sont valides, False autrement.

    >>> valider_params({'fields': ['temperature'], 'date_debut': '2021-01-30T00:00:00Z', 'date_fin': '2021-01-31T00:00:00Z', 'pas': 'quotidienne', 'station_id': '123456', 'api_key': 'key', 'url_base': 'https://api.meteo.fr', 'endpoint': '/data', 'url_telechargement': 'https://api.meteo.fr/download', 'tentative_max': 5, 'delai': 10, 'path_enregistrement_dataset': '/valid/path'})
    True
    """
    # Définition des champs valides
    champs_valides = {"temperature", "wind_speed", "max_wind_speed"}
    # Vérification de la validité des champs
    if not all(field in champs_valides for field in params["fields"]):
        logger.error("Validation des champs : échec.")
        raise ValidationError("Un ou plusieurs champs spécifiés ne sont pas valides.")

    # Validation des formats de date
    try:
        format_date ="%Y-%m-%dT%H:%M:%SZ"
        datetime.strptime(params["date_debut"], format_date)
        datetime.strptime(params["date_fin"], format_date)
        date_fin_datetime = datetime.strptime(params["date_fin"], format_date)

        # verifie si la date de fin est égale à la date du jour
        if date_fin_datetime.replace(hour=0, minute=0, second=0, microsecond=0)==datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            logger.critical("!!! l'api ne fonctionne que sur des dates supérieures à la veille, il n'est pas possible d'avoir les données du jour. \nVeuillez selectionner une autre date")
            sys.exit(1)

    except ValueError as e:
        logger.error("Validation des dates : échec.")
        raise ValidationError(f"Erreur de format de date : {e}")

    # Vérification de la validité du pas
    pas_valides = {"quotidienne", "horaire", "infrahoraire-6m"}
    if params["pas"] not in pas_valides:
        logger.error("Validation du pas : échec.")
        raise ValidationError("Le pas spécifié n'est pas valide.")

    # Contrôle de la validité de la station_id
    if  not str(params["station_id"]).isdigit():
        # if not isinstance(params["station_id"], int) or not str(params["station_id"]).isdigit():
        logger.error("Validation de la station_id : échec.")
        raise ValidationError("La station_id spécifiée n'est pas valide.")

    # Vérification de la présence de l'api_key
    if not params["api_key"]:
        logger.error("Validation de l'api_key : échec.")
        raise ValidationError("L'api_key spécifiée est vide.")

    # Validation des URLs
    if not params["url_base"]:
        logger.error("Validation de l'url_base : échec.")
        raise ValidationError("L'url_base spécifiée est vide.")
    if not params["endpoint"]:
        logger.error("Validation de l'endpoint : échec.")
        raise ValidationError("L'endpoint spécifié est vide.")
    if not params["url_telechargement"]:
        logger.error("Validation de l'url_telechargement : échec.")
        raise ValidationError("L'url_telechargement spécifiée est vide.")

    # Contrôle du nombre de tentatives et du délai
    if not isinstance(params["tentative_max"], int) or params["tentative_max"] < 1:
        logger.error("Validation du nombre de tentatives_max : échec.")
        raise ValidationError("Le nombre de tentatives_max spécifié n'est pas valide.")
    if not isinstance(params["delai"], int) or params["delai"] < 1:
        logger.error("Validation du délai : échec.")
        raise ValidationError("Le délai spécifié n'est pas valide.")


    # Vérification de la validité du chemin pour l'enregistrement du dataset
    chemin_fichier = params.get("path_enregistrement_dataset")
    if chemin_fichier:
        dossier = os.path.dirname(chemin_fichier)
        if not os.path.isdir(dossier):
            logger.error(f"Le dossier spécifié pour 'path_enregistrement_dataset' n'existe pas : {dossier}")
            raise ValidationError(f"Le dossier spécifié pour 'path_enregistrement_dataset' n'existe pas : {dossier}")
        if not os.access(dossier, os.W_OK):
            logger.error(f"Le dossier spécifié pour 'path_enregistrement_dataset' n'est pas accessible en écriture : {dossier}")
            raise ValidationError(f"Le dossier spécifié pour 'path_enregistrement_dataset' n'est pas accessible en écriture : {dossier}")
    else:
        logger.error("Le chemin pour 'path_enregistrement_dataset' n'est pas spécifié.")
        raise ValidationError("Le chemin pour 'path_enregistrement_dataset' n'est pas spécifié.")




def preparation_commande_fichier_meteo_france(params):
    """
    Prépare et envoie une commande de fichier de données météorologiques à Météo France.

    Args:
        params (dict): Paramètres nécessaires pour la requête API, incluant url_base, endpoint,
                       api_key, fields, pas, station_id, date_debut, et date_fin.

    Returns:
        dict: Réponse de l'API sous forme de dictionnaire JSON.

    Raises:
        Exception: Si la requête échoue pour une raison quelconque.

    >>> params = {
    ...     "url_base": "https://api.meteo.france/v1",
    ...     "endpoint": "/donneeslibres",
    ...     "api_key": "votre_cle_api",
    ...     "fields": ["temperature", "humidite"],
    ...     "pas": "10min",
    ...     "station_id": "12345",
    ...     "date_debut": "20240101",
    ...     "date_fin": "20240102"
    ... }
    >>> print(preparation_commande_fichier_meteo_france(params)) # doctest: +SKIP
    """


    # Encodage de l'API key si nécessaire, normalement en passant par le header ce n'est pas utile
    if '%' not in params['api_key']:
        api_key_enc = quote(params['api_key'])
    else:
        api_key_enc = params['api_key']
    # logger.debug(f"\n api_key_enc:\n{api_key_enc} \n")

    # Construction de l'URL de la requête sans les champs `fields`
    endpoint_formatte = params['endpoint'].format(
        pas=params['pas'],
        station=params['station_id'],
        date_debut=quote(params['date_debut']), #encodage des dates pour eviter le :
        date_fin=quote(params['date_fin'])
    )
    logger.debug(f"\n date_debut:\n{quote(params['date_debut'])} \n")
    logger.debug(f"\n date_fin:\n{quote(params['date_fin'])} \n")
    # logger.debug(f"\n endpoint_formatte:\n{endpoint_formatte} \n")
    url_endpoint = f"{params['url_base']}{endpoint_formatte}"
    logger.debug(f"\n url_endpoint:\n{url_endpoint} \n")

    # Préparation des en-têtes pour inclure l'API key
    headers = {
        'accept': '*/*',
        'apikey': params['api_key'],
        # 'apikey': api_key_enc
    }


    try:
        # Utilisation des en-têtes dans la requête
        response = requests.get(url_endpoint, headers=headers)
        # logger.debug(f"\n réponse commande response.status_code:\n{response.status_code} \n")

        # Traitement des réponses en fonction du status code
        if response.status_code == 202:  # Assurez-vous que le code de statut attendu est correct
            response_data = response.json()
            # logger.debug(f"\n response_data=== :\n{response_data} \n")
            return response_data["elaboreProduitAvecDemandeResponse"]["return"]
        else:
            status_code_messages = {
                400: {"error": "Contrôle de paramètres en erreur"},
                401: {"error": "Invalid credential"},
                404: {"error": "La station demandée n'existe pas"},
                500: {"error": "Erreur interne au serveur"},
                507:{"error":"production rejetée par le système (trop volumineuse)"},
            }
            return status_code_messages.get(response.status_code, {"error": "Statut inconnu"})
    except Exception as e:
        logger.error(f"Erreur lors de la requête à Météo France : {str(e)}")
        raise Exception(f"Erreur lors de la requête : {str(e)}")



def telecharger_donnees_meteo(params):
    """
    Télécharge les données météo en utilisant l'identifiant de commande fourni et les paramètres spécifiés.

    Args:
        id_cmde (str): Identifiant de la commande pour le téléchargement des données.
        params (dict): Dictionnaire contenant les paramètres pour le téléchargement, y compris l'URL de téléchargement,
                       le nombre maximal de tentatives et le délai entre chaque tentative.

    Returns:
        dict: Un dictionnaire contenant soit les données téléchargées soit un message d'erreur.

    Exemple d'utilisation:
    >>> params = {
    ...     "fields": ["temperature", "wind_speed", "max_wind_speed"],
    ...     "api_key": "api_key_donnees_climatiques",
    ...     "pas": "quotidienne",
    ...     "station_id": "13028001",
    ...     "date_debut": "2024-01-01T00:00:00Z",
    ...     "date_fin": "2024-02-01T00:00:00Z",
    ...     "url_base": "base_url_donnees_climatiques",
    ...     "endpoint": "endpoint_donnees_climatiques_commande",
    ...     "endpoint_telechargement": "url_donnees_climatiques_telechargement",
    ...     "tentative_max": 5,
    ...     "delai": 30,
    ... }
    >>> # L'exemple suivant est illustratif et nécessite un environnement de test pour être exécuté.
    >>> # telecharger_donnees_meteo('12345ABC', params)
    {'message': 'Fichier téléchargé avec succès', 'data': b'données météo'}

    Note: Cet exemple de doctest est illustratif et ne peut pas être exécuté tel quel sans un environnement de test approprié.
    """
    # Validation des paramètres
    valider_params(params)
    # # configure le logger en fonctino de params
    # reconfigurer_logging(params)

    #  recuperation du id-cmde depuis la fonction preparation_commande_fichier_meteo_france
    # Si la commande n'est pas nécessaire, on ne continue pas dans cette partie
    commande_deja_faites = params["commande_deja_faites"]

    if params["commande_dataset"] == True:
        try:
            id_cmde = preparation_commande_fichier_meteo_france(params)
            commande_deja_faites = True
            logger.debug(f"id_cmde: {id_cmde}")
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de la commande: {e}")
            return {"error": "Erreur lors de la préparation de la commande."}

    # if id_cmde:logger.debug(f"\n id_cmde4:\n{id_cmde} \n")
    # id_cmde
    # if params["enregistrement_dataset"]==False: return
    # try:
    #     if id_cmde: logger.debug(f"\n id_cmde3:\n{id_cmde} \n")
    #     if params["commande_dataset"]==True:
    #         id_cmde = preparation_commande_fichier_meteo_france(params)  # Assurez-vous que cette fonction est définie ailleurs
    #         if id_cmde:logger.debug(f"\n id_cmde1:\n{id_cmde} \n")
    # except Exception as e:
    #     logging.error(f"Erreur lors de la préparation de la commande: {e}")
    #     return "Erreur lors de la préparation de la commande."
    if commande_deja_faites:
        url = params['url_telechargement'].format(id_cmde=id_cmde)
        logger.debug(f"\n url:\n{url} \n")

    url_telechargement = params["url_telechargement"]
    logger.debug(f"\n url_telechargement:\n{url_telechargement} \n")
    tentative_max = params.get("tentative_max")
    logger.debug(f"\n tentative_max:\n{tentative_max} \n")
    delai = params.get("delai")
    logger.debug(f"\n delai:\n{delai} \n")
    # url = f"{url_telechargement}?id_cmde={id_cmde}"
    tentative = 0

    #  Préparation des en-têtes pour inclure l'API key
    headers = {
        'accept': '*/*',
        'apikey': params['api_key']
        # 'apikey': api_key_enc
    }
    # logger.critical(f"\n headers:\n{headers} \n")

    status_code_messages = {
        200: lambda resp: resp.json(),
        201: lambda _: {
            "message": "Fichier renvoyé"
        },
        # 202: lambda resp: resp.json()['elaboreProduitAvecDemandeResponse']['return'],
        204: lambda _: {
            "message": "Production encore en attente ou en cours"
        },
        401: lambda _: {
            "error": "Credential invalide"
        },
        404: lambda _: {
            "error": "Le numéro de commande n'existe pas"
        },
        410: lambda _: {
            "error": "Production déjà livrée"
        },
        500: lambda _: {
            "error": "Production terminée, échec"
        },
        507: lambda _: {
            "error": "Production rejetée par le système (trop volumineuse)"
        }
    }

    while tentative < tentative_max:
        try:
            if params["telechargement_dataset"] == True:
                response = requests.get(url, headers=headers)
                # logger.debug(f"\n telechargement statut requete:\n{response.status_code} \n")
                logger.debug(
                    f"\n telechargement statut requete:\n{response.status_code} \n"
                )

                gestion_statut = status_code_messages.get(
                    response.status_code,
                    lambda _: {"error": "Statut inconnu"})
                # logger.debug(f"\n gestion_statut:\n{gestion_statut} \n")
                resultat = gestion_statut(response)
                logger.debug(f"\n resultat:\n{resultat} \n")
                if "error" in resultat:
                    logger.debug(resultat["error"])
                    return resultat["error"]
                elif "message" in resultat and resultat[
                        "message"] == "Fichier renvoyé":
                    logger.debug("Fichier téléchargé avec succès")
                    # Gestion de l'enregistrement du fichier
                    if params["enregistrement_dataset"] == True:
                        enregistrement_dataset_meteo_france(
                            params, response.content)
                        return f"Le fichier CSV a été enregistré avec succès"

                # return "Fichier téléchargé avec succès"
            time.sleep(delai)
            tentative += 1
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {e}")
            return f"Erreur lors du téléchargement: {e}"

    logger.debug(f"\n id_cmde:\n{id_cmde} \n")
    logger.error("Le téléchargement a échoué après plusieurs tentatives.")
    return "Le téléchargement a échoué après plusieurs tentatives."



# def enregistrement_dataset_meteo_france():
#             # changement de format de la date
#             indice = 1
#             date_debut_format = datetime.strptime(params.get("date_debut"), "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%Y_%Hh%M")
#             date_fin_format = datetime.strptime(params.get("date_fin"), "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%Y_%Hh%M")
#             path=params.get("path_enregistrement_dataset")
#             logger.debug(f" path {path}")
#             nom_dossier = f"{path}{params.get('station_id')}_{params.get('pas')}_{date_debut_format}_{date_fin_format}"
#             logger.debug(f" nom_dossier {nom_dossier}")
#             os.makedirs(nom_dossier, exist_ok=True)
#             chemin_fichier = f"{nom_dossier}/{params.get('station_id')}_{params.get('pas')}_{date_fin_format}_au_{date_fin_format}_{indice}.csv"
#             logger.debug(f" chemin_fichier {chemin_fichier}")
#             # Vérification de l'existence du fichier et ajout d'un indice si nécessaire
#             while os.path.exists(chemin_fichier):
#                 indice += 1
#                 chemin_fichier = f"{nom_dossier}/{params.get('station_id')}_{params.get('pas')}_{date_fin_format}_au_{date_fin_format}_{indice}.csv"
#             with open(chemin_fichier, "wb") as fichier:
#                 fichier.write(response.content.decode('utf-8-sig').encode('utf-8'))
#             logging.info(f"Le fichier CSV a été enregistré avec succès: {chemin_fichier}")
#             return f"Le fichier CSV a été enregistré avec succès: {chemin_fichier}"
