# pylint: disable=all
import os
import sys
# from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent.parent))
from pathlib import Path  # permet l'import des fonctions siuées dans d'autres répertoires,  il faut toujours le placer en premier
# sys.path.append(str(Path(__file__).resolve().parent.parent))
# from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
# Ajouter le dossier 'outils' au sys.path
sys.path.append(str(project_root / 'outils'))
import requests
import json
import time
import configparser
from datetime import datetime, timedelta
# from api_meteo_france import telecharger_donnees_meteo
from urllib.parse import quote
import logging
from urllib.parse import urlencode
from api_meteo_france import preparation_commande_fichier_meteo_france, telecharger_donnees_meteo
from get_config_ini import lire_config_et_imprimer_cles_valeurs
from gestion_logging import reconfigurer_logging
from enregistrement_datasets import enregistrement_dataset_meteo_france
# from outils.get_config_ini import lire_config_et_imprimer_cles_valeurs
# from outils.gestion_logging import reconfigurer_logging
# from outils.enregistrement_datasets import enregistrement_dataset_meteo_france


logger = logging.getLogger('colorlog_example')

def upload_enregistrement_dataset_meteo_france(path_config,path_destination,nom_api, station_id, pas, date_debut, date_fin):

    # ====== RECUPERATION DES CLE ET URL DEPUIS LE FICHIER CONFIG.INI =========
    # recuperation de l'API se trouvant dans le fihcier config.ini
    # chemin_fichier = r"projet_meteo\Projet_Meteo\config.ini"
    chemin_fichier = path_config
    # path_enregistrement_dataset="Projet_Meteo\\Datasets\\meteo_france\\upload_dataset_depuis_api\\".replace('\\', '/')
    #  Attention de pas de \ à la fin du path
    # path_enregistrement_dataset = r"projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api".replace('\\', '/')
    path_enregistrement_dataset = path_destination.replace('\\', '/')

    #choisir le theme de l'api se trouvant dans le fichier config.ini
    # theme = 'meteo'
    theme = nom_api

    cles_valeurs_trouvees = lire_config_et_imprimer_cles_valeurs(chemin_fichier, theme)

    # liste des clés presentes dans le fichier config.ini
    # print("Noms des clés trouvées :", cles_valeurs_trouvees.keys())

    api_key_donnees_climatiques = cles_valeurs_trouvees['api_key_donnees_climatiques'].strip("'")
    api_key_donnees_climatiques_encoded = cles_valeurs_trouvees['api_key_donnees_climatiques_encoded'].strip( "'")
    # print(f"\nAPI_KEY :\n{API_KEY} \n")
    # print(f"\nAPI_KEY :\n{API_KEY} \n")
    # recuperation de l'url_base se trouvant dans le fihcier config.ini
    base_url_donnees_climatiques = cles_valeurs_trouvees["base_url_donnees_climatiques"].strip("'")
    # recuperation de l'enpoint se trouvant dans le fihcier config.ini
    endpoint_donnees_climatiques_commande = cles_valeurs_trouvees['endpoint_donnees_climatiques_commande'].strip("'")

    # url pour obtenir les informations d'historique d'une station
    endpoint_donnees_climatiques_info_station= cles_valeurs_trouvees["endpoint_donnees_climatiques_info_station"].strip("'")

    #  récuperation de l'url de telechargement
    url_donnees_climatiques_telechargement = cles_valeurs_trouvees["url_donnees_climatiques_telechargement"].strip("'")


    # convertion dates en chaînes de caractères au format: 'YYYY-MM-DDTHH:MM:SSZ'
    # date_debut=datetime.date_debut
    # date_fin=datetime.date_fin
    str_date_debut = date_debut.strftime('%Y-%m-%dT%H:%M:%SZ')
    str_date_fin = date_fin.strftime('%Y-%m-%dT%H:%M:%SZ')

    # ========= LANCEMENT DES FONCTIONS DE PREPARATION ET TELECHARGEMENT DES FICHIERS ISSUS DE L'API DE METEO FRANCE =========
    # Obtenir la liste des stations  meteo  du 13
    url = r'https://public-api.meteofrance.fr/public/DPClim/v1/liste-stations/infrahoraire-6m?id-departement=13'
    #  mesure sur 1 station toutes les 6 min sur 1 an
    # https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/infrahoraire-6m?id-station=13028001&date-deb-periode=2023-02-19T00%3A00%3A00Z&date-fin-periode=2024-02-18T00%3A00%3A00Z

    # ========= CONSTRUCTION DICTIONNAIRE PARAMS =========
    # ex 'url'
    # url = f"https://public-api.meteofrance.fr/public/DPClim/v1/commande-station/infrahoraire-6m?id-station={station}&date-deb-periode={date_debut}&date-fin-periode={date_fin}"
    # url_commande_finale = f"{url_base}/commande-station/{pas}?id-station={station}&date-deb-periode={date_debut}&date-fin-periode={date_fin}"
    # url_telechargement=url_donnees_climatiques_telechargement("id-cmde")

    params = {
        "fields": ["temperature", "wind_speed", "max_wind_speed"],
        "api_key": api_key_donnees_climatiques,
        "telechargement_dataset": True,
        "commande_dataset":True,
        "commande_deja_faites":True,
        "enregistrement_dataset":True,
        "path_enregistrement_dataset":path_enregistrement_dataset,
        "encodage": "utf-8-sig",
        # "pas": "horaire", #quotidienne, horaire, infrahoraire-6m
        # "pas": "quotidienne", #quotidienne, horaire, infrahoraire-6m
        # "pas": "infrahoraire-6m", #quotidienne, horaire infrahoraire-6m
        "pas": pas, #quotidienne, horaire, infrahoraire-6m
        # "station_id": '13028001',
        "station_id": station_id,
        "date_debut": str_date_debut,
        "date_fin": str_date_fin,
        # "date_debut": '2020-01-31T00:00:00Z',
        # "date_fin": '2021-01-30T00:00:00Z',
        "url_base": base_url_donnees_climatiques,
        "endpoint": endpoint_donnees_climatiques_commande,
        # "endpoint": endpoint_donnees_climatiques_info_station,
        "url_telechargement": url_donnees_climatiques_telechargement,
        "tentative_max": 6,
        "delai": 40,
        # "niveau_log": logging.debug,
        "niveau_log": "DEBUG",  # 'DEBUG' 'INFO' 'WARNING' 'ERROR'  'CRITICAL'
        # "format_log": "%(log_color)s\n[%(asctime)s-%(levelname)s]=>>> fichier=%(filename)s|ligne=%(lineno)d |fonction=%(funcName)s() | '%(message)s'\n",
        # #format='%(log_color)s%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'  # '%(asctime)s - %(levelname)s - %(message)s'
        # "format_log_file": ('[%(asctime)s|%(levelname)s|]>>>>>>>>> '
        #       'fichier=%(filename)s| chemin=%(pathname)s|ligne=%(lineno)d|'
        #       'fonction=%(funcName)s()|'
        #       'processus=%(process)d|nom_processus=%(processName)s|'
        #       'thread=%(threadName)s|temps_rel=%(relativeCreated)d|'
        #       'message={%(message)s}|exception={%(exc_info)s}'),
        #       #format='%(log_color)s%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'  # '%(asctime)s - %(levelname)s - %(message)s'
        # # "format_log_file": ('[%(asctime)s|%(levelname)s|%(msecs)d|]'
        # #       'fichier=%(filename)s|ligne=%(lineno)d|'
        # #       'fonction=%(funcName)s()|'
        # #       'processus=%(process)d|thread=%(threadName)s|module=%(module)s|'
        # #       '%(message)s'),  #format='%(log_color)s%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'  # '%(asctime)s - %(levelname)s - %(message)s'


    }

    # configure le logger en fonctino de params
    reconfigurer_logging(params)
    # utilisation du logger à la place du logging
    # logger=reconfigurer_logging(params)
    if date_fin.replace(hour=0, minute=0, second=0, microsecond=0)==datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
        logger.critical("!!! l'api ne fonctionne que sur des dates supérieures à la veille, il n'est pas possible d'avoir les données du jour. \nVeuillez selectionner une autre date")
        sys.exit(1)
    logger.info(f"\n str_date_debut:\n{str_date_debut} \n")
    logger.info(f"\n str_date_fin:\n{str_date_fin} \n")

    logger.debug(f"\n endpoint_donnees_climatiques_info_station:\n{endpoint_donnees_climatiques_info_station} \n")
    # logger.error(f"\n api_key_donnees_climatiques:\n{api_key_donnees_climatiques} \n")
    logger.debug(f"\n base_url_donnees_climatiques :\n{base_url_donnees_climatiques} \n")
    logger.debug(f"\n endpoint_donnees_climatiques_commande :\n{endpoint_donnees_climatiques_commande} \n")
    logger.debug(f"\n url_donnees_climatiques_telechargement :\n{url_donnees_climatiques_telechargement} \n")
    #  LANCEMENT FONCTIONS voir api_meteo_france.py
    telecharger_donnees_meteo(params)


# lancement upload
path_config=r"projet_meteo\Projet_Meteo\config.ini"
path_destination= r"projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api"
nom_api="meteofrance"
pas="horaire" # quotidienne, horaire, infrahoraire-6m

#--------------------------- LANCEMENT SUR 1 STATIONS ET 1 ANNEES-------------
# station_id='13055029'
# # Définir les dates de début et de fin format # YYYY,MM,DD,HH,MM,SS,année,mois,jour,heure, minute, secondes
# date_debut = datetime(2024, 2, 28, 17, 0, 0) # !!! l'api ne fonctionne que sur des dates supérieures à la veille, il n'est pas possible de d'avoir les données du jour
# date_fin = datetime(2024, 2, 29, 23, 59, 59)
# # if date_fin.replace(hour=0, minute=0, second=0, microsecond=0)==datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
# #     logger.critical("!!! l'api ne fonctionne que sur des dates supérieures à la veille, il n'est pas possible d'avoir les données du jour. \nVeuillez selectionner une autre date")
# #     sys.exit(1)
# # date_debut= '2019-01-31T00:00:00Z'
# # date_fin= '2020-01-30T00:00:00Z'
# upload_enregistrement_dataset_meteo_france(path_config,path_destination,nom_api,station_id, pas, date_debut, date_fin)


#--------------------------- LANCEMENT SUR TOUTES LES STATIONS ET SUR PLUSIEURS ANNEES-------------

# Liste des stations_id
# stations_id = [13001009, 13004003, 13005003, 13022003, 13028001, 13030001, 13031002, 13036003, 13047001, 13054001, 13055001, 13055029, 13056002, 13062002, 13074003, 13091002, 13092001, 13103001, 13108004, 13110003, 13111002]
# stations_id = [13001009, 13004003]

# # Calculer la date de fin comme étant la date du jour
# date_fin_actuelle = datetime.now()

#----------------------------------------------------------------

# # Pour chaque station_id
# for station_id in stations_id:
#     # Définir la date de fin temporaire pour la boucle
#     date_fin_temp = date_fin_actuelle

#     # Boucler sur les 2 dernières années, en découpant par intervalles d'un an
#     for _ in range(2):  # 2 pour les deux dernières années
#         # Calculer la date de début en soustrayant un an de la date de fin temporaire
#         date_debut = date_fin_temp - timedelta(days=365)

#         # Appeler la fonction d'upload pour chaque intervalle d'un an
#         logger.info(f" path_config  {path_config}")
#         logger.info(f" path_destination  {path_destination}")
#         logger.info(f"  nom_api {nom_api}")
#         logger.info(f"  station_id {station_id}")
#         logger.info(f" pas  {pas}")
#         logger.info(f"  date_debut {date_debut}")
#         logger.info(f"  date_fin_temp {date_fin_temp}")
#         upload_enregistrement_dataset_meteo_france(path_config, path_destination, nom_api, station_id, pas, date_debut, date_fin_temp)

#         # Afficher une confirmation pour chaque intervalle traité, optionnel
#         print(f"Upload terminé pour la station {station_id} du {date_debut.strftime('%Y-%m-%d')} au {date_fin_temp.strftime('%Y-%m-%d')}")

#         # Mettre à jour la date de fin temporaire pour la prochaine itération
#         date_fin_temp = date_debut

#----------------------------------------------------------------


# # Définition de la période en fonction du type de pas
# periodes = {
#     "quotidienne": timedelta(days=365 * 2), # en année
#     "horaire": timedelta(days=10),  # en jours
#     "infrahoraire-6m": timedelta(hours=5),  # en heures
# }

# # Définition de la période en fonction du type de pas
# periodes = {
#     "quotidienne": timedelta(days=365 * 2),  # 2 ans
#     "horaire": timedelta(days=10),  # 3 mois
#     "infrahoraire-6m": timedelta(hours=2),  # 2 heures pour l'exemple
# }

# # Pour chaque station_id
# for station_id in stations_id:
#     # Adapter la boucle en fonction du type de pas
#     for pas, duree in periodes.items():
#         date_debut = date_fin_actuelle - duree
#         date_fin_temp = date_fin_actuelle

#         # Ajustement de la date en fonction du type de pas
#         if pas == "quotidienne":
#             date_debut = date_debut.replace(hour=0, minute=0, second=0)
#             date_fin_temp = date_fin_temp.replace(hour=0, minute=0, second=0)
#         elif pas == "horaire":
#             date_debut = date_debut.replace(minute=0, second=0)
#             date_fin_temp = date_fin_temp.replace(minute=0, second=0)
#         elif pas == "infrahoraire-6m":
#             date_debut = date_debut.replace(second=0)
#             date_fin_temp = date_fin_temp.replace(second=0)

#         # Appel à la fonction d'upload avec les dates ajustées
#         upload_enregistrement_dataset_meteo_france(path_config, path_destination, nom_api, station_id, pas, date_debut, date_fin_temp)

#         # Logging de confirmation
#         logger.info(f"Upload terminé pour {pas} de la station {station_id} du {date_debut.strftime('%Y-%m-%d %H:%M:%S')} au {date_fin_temp.strftime('%Y-%m-%d %H:%M:%S')}")


#----------------------------------------------------------------
#----------------------------------------------------------------

# # Définition de la période en fonction du type de pas
# periodes = {
#     "quotidienne": (0, 0, 0),  # 2 ans
#     "horaire": (0, 10, 0),  # 10 jours
#     "infrahoraire-6m": (0, 0, 2),  # 2 heures
# }

# def calculer_date_debut(date_fin, periode):
#     annees, jours, heures = periode
#     date_debut = date_fin - timedelta(days=(365.25 * annees) + jours, hours=heures)
#     return date_debut

# # Pour chaque station_id
# for station_id in stations_id:
#     # Adapter la boucle en fonction du type de pas
#     for pas, periode in periodes.items():
#         date_debut = calculer_date_debut(date_fin_actuelle, periode)
#         date_fin_temp = date_fin_actuelle

#         # Ajustement de la date en fonction du type de pas
#         if pas == "quotidienne":
#             date_debut = date_debut.replace(hour=0, minute=0, second=0)
#             date_fin_temp = date_fin_temp.replace(hour=0, minute=0, second=0)
#         elif pas == "horaire" or pas == "infrahoraire-6m":
#             # Pas besoin d'ajustement supplémentaire ici car la granularité est déjà gérée par la période
#             pass

#         # Appel à la fonction d'upload avec les dates ajustées
#         upload_enregistrement_dataset_meteo_france(path_config, path_destination, nom_api, station_id, pas, date_debut, date_fin_temp)

#         # Logging de confirmation
#         logger.info(f"Upload terminé pour {pas} de la station {station_id} du {date_debut.strftime('%Y-%m-%d %H:%M:%S')} au {date_fin_temp.strftime('%Y-%m-%d %H:%M:%S')}")


# #----------------------------------------------------------------
# #----------------------------------------------------------------
# # lancement upload
# path_config=r"projet_meteo\Projet_Meteo\config.ini"
# path_destination= r"projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api"
# nom_api="meteofrance"
# pas="quotidienne" # quotidienne, horaire, infrahoraire-6m

# # Liste des stations_id
# # stations_id = [13001009, 13004003, 13005003, 13022003, 13028001, 13030001, 13031002, 13036003, 13047001, 13054001, 13055001, 13055029, 13056002, 13062002, 13074003, 13091002, 13092001, 13103001, 13108004, 13110003, 13111002]
# stations_id = [13001009, 13004003,13056002]
# # Calculer la date de fin comme étant la date du jour
# date_fin_actuelle = datetime.now()
# # Définition unique des périodes
# periodes = (0, 10, 2)  # 2 ans, 10 jours, 2 heures
# #----------------------------------------------------------------
# #----------------------------------------------------------------

# from datetime import datetime, timedelta

# def calculer_dates(date_fin_actuelle, periodes, pas):
#     annees, jours, heures = periodes
#     date_debut = date_fin_actuelle - timedelta(days=(365.25 * annees) + jours, hours=heures)

#     if pas == "quotidienne":
#         date_debut = date_debut.replace(hour=0, minute=0, second=0, microsecond=0)
#         date_fin_temp = date_fin_actuelle.replace(hour=0, minute=0, second=0, microsecond=0)
#     elif pas == "horaire":
#         date_debut = date_debut.replace(minute=0, second=0, microsecond=0)
#         date_fin_temp = date_fin_actuelle.replace(minute=0, second=0, microsecond=0)
#     elif pas == "infrahoraire-6m":
#         date_debut = date_debut.replace(second=0, microsecond=0)
#         # Pour la date de fin dans le cas infrahoraire, on conserve l'heure et les minutes actuelles mais on réinitialise les secondes
#         date_fin_temp = date_fin_actuelle.replace(second=0, microsecond=0)

#     return date_debut, date_fin_temp



# # Pour chaque station_id
# for station_id in stations_id:
#     for pas in ["quotidienne", "horaire", "infrahoraire-6m"]:
#         date_debut,date_fin_temp = calculer_dates(date_fin_actuelle, periodes, pas)
#         date_fin_temp = date_fin_actuelle

#         # Log des paramètres pour vérification
#         logger.info(f"Path config: {path_config}")
#         logger.info(f"Path destination: {path_destination}")
#         logger.info(f"Nom API: {nom_api}")
#         logger.info(f"Station ID: {station_id}")
#         logger.info(f"Pas: {pas}")
#         logger.info(f"Date début: {date_debut}")
#         logger.info(f"Date fin: {date_fin_temp}")

#         # Ici, insérez l'appel à votre fonction upload_enregistrement_dataset_meteo_france
#         # Exemple d'appel (à remplacer par votre propre logique d'implémentation) :
#         upload_enregistrement_dataset_meteo_france(path_config, path_destination, nom_api, station_id, pas, date_debut, date_fin_temp)

#         # upload_enregistrement_dataset_meteo_france(path_config,path_destination,nom_api, station_id, pas, date_debut, date_fin)
#         # Logging de confirmation
#         logger.info(f"Upload terminé pour le pas '{pas}' de la station {station_id} du {date_debut.strftime('%Y-%m-%d %H:%M:%S')} au {date_fin_temp.strftime('%Y-%m-%d %H:%M:%S')}")




#----------------------------------------------------------------
#----------------------------------------------------------------
# lancement upload
path_config=r"projet_meteo\Projet_Meteo\config.ini"
path_destination= r"projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api2"
nom_api="meteofrance"
pas="horaire" # quotidienne, horaire, infrahoraire-6m





# Configuration initiale
path_config = "projet_meteo\\Projet_Meteo\\config.ini"
path_destination = "projet_meteo\\Projet_Meteo\\Datasets\\meteo_france\\upload_dataset_depuis_api2"
nom_api = "meteofrance"
pas = "horaire"  # Options : "quotidienne", "horaire", "infrahoraire-6m"
stations_id = [13001009, 13004003, 13005003, 13022003, 13028001, 13030001, 13031002, 13036003, 13047001, 13054001, 13055001, 13055029, 13056002, 13062002, 13074003, 13091002, 13092001, 13103001, 13108004, 13110003, 13111002]
# stations_id = [  13028001]
# stations_id = [13031002, 13036003]

# Configuration du logger
logger = logging.getLogger('colorlog_example')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

# Dates de début et de fin choisies
date_debut_choisie = datetime(2024, 1, 1, 0, 0, 0)
date_fin_choisie = datetime(2024, 3,1, 1, 0, 0)

# Remise à zéro des minutes, secondes et microsecondes pour les dates choisies
date_debut_choisie = date_debut_choisie.replace(minute=0, second=0, microsecond=0)
date_fin_choisie = date_fin_choisie.replace(minute=0, second=0, microsecond=0)

if date_fin_choisie.replace(hour=0, minute=0, second=0, microsecond=0)==datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
    logger.critical("!!! l'api ne fonctionne que sur des dates supérieures à la veille, il n'est pas possible d'avoir les données du jour. \nVeuillez selectionner une autre date")
    sys.exit(1)
# # Limite de date de fin à la veille à 23h59m59s
# date_fin_limite = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0) - timedelta(days=1)

# Limite de date de fin à la veille à 23h59m59s
date_fin_limite = datetime.now().replace( minute=0, second=0, microsecond=0) - timedelta(days=1)

# Ajustement de la date de fin choisie en fonction de la limite
date_fin = min(date_fin_choisie, date_fin_limite)


def est_annee_bissextile(annee):
    """
    Vérifier si une année est bissextile.

    :param annee: int, l'année à vérifier.
    :return: bool, True si bissextile, sinon False.

    >>> est_annee_bissextile(2020)
    True
    >>> est_annee_bissextile(2021)
    False
    """
    return (annee % 4 == 0 and annee % 100 != 0) or (annee % 400 == 0)


def decouper_periodes(date_debut, date_fin):
    """
    Découper une période en tranches d'un an sans chevauchement.

    :param date_debut: datetime, date de début de période.
    :param date_fin: datetime, date de fin de période.
    :return: list, liste des tuples de dates (début, fin) de chaque tranche.

    >>> decouper_periodes(datetime(2010, 2, 28), datetime(2012, 2, 28))
    [(datetime.datetime(2010, 2, 28, 0, 0), datetime.datetime(2011, 2, 27, 0, 0)),
     (datetime.datetime(2011, 2, 28, 0, 0), datetime.datetime(2012, 2, 27, 0, 0))]
    """
    tranches = []
    while date_debut < date_fin:
        # Calculer la fin de l'année courante pour la date de début actuelle
        fin_annee_courante = datetime(date_debut.year, 12, 31, 23, 59, 59)

        # Si la date de début est déjà la fin de l'année, passer à l'année suivante
        if date_debut == fin_annee_courante + timedelta(seconds=1):
            fin_annee_courante = datetime(date_debut.year + 1, 12, 31, 23, 59, 59)

        # Calculer la nouvelle fin comme le minimum entre la fin de l'année courante et la date de fin choisie
        nouvelle_fin = min(fin_annee_courante, date_fin)

        # Ajouter la tranche actuelle à la liste
        tranches.append((date_debut, nouvelle_fin))

        # Préparer la date de début pour la prochaine tranche
        date_debut = nouvelle_fin + timedelta(seconds=1)

        # S'assurer de ne pas dépasser la date de fin choisie
        if date_debut > date_fin:
            break

    return tranches


# Affichage des dates de début et de fin ajustées
logger.info(f"Date de début choisie: {date_debut_choisie}")
logger.info(f"Date de fin ajustée: {date_fin}")

# Découpage en tranches d'un an max et traitement pour chaque station
for station_id in stations_id:
    tranches = decouper_periodes(date_debut_choisie, date_fin)
    for date_debut_tranche, date_fin_tranche in tranches:
        logger.info(
            f"Station ID: {station_id}, Tranche début: {date_debut_tranche}, Tranche fin: {date_fin_tranche}"
        )
        upload_enregistrement_dataset_meteo_france(path_config,
                                                   path_destination, nom_api,
                                                   station_id, pas,
                                                   date_debut_tranche,
                                                   date_fin_tranche)
