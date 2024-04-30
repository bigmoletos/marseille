# pylint: disable=all
import sys
from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent.parent))
# Obtenir le chemin absolu du répertoire racine du projet
project_root = Path(__file__).resolve().parents[2]
# Ajouter le dossier 'outils' au sys.path
sys.path.append(str(project_root / 'outils'))
import configparser
import re
import os
import logging
from datetime import datetime
from urllib.parse import quote
# import des outils
from gestion_logging import reconfigurer_logging
from get_config_ini import lire_config_et_imprimer_cles_valeurs
# from outils.gestion_logging import reconfigurer_logging
# from outils.get_config_ini import lire_config_et_imprimer_cles_valeurs


logger = logging.getLogger('colorlog_example')


def enregistrement_dataset_meteo_france(params, response_content):
    """
    Enregistre les données meteo_france téléchargées dans un fichier CSV.

    Args:
        params (dict): Dictionnaire contenant les paramètres nécessaires pour l'enregistrement du fichier.
        response_content (bytes): Contenu binaire du fichier à enregistrer.

    Returns:
        str: Message indiquant le succès de l'enregistrement ou un message d'erreur.
    """
    try:
        formatage_date = "%d-%b-%Y_at_%Hh%M"
        # formatage_date="%d-%m-%Y_%Hh%M"
        # Formatage des dates
        date_debut_format = datetime.strptime(
            params["date_debut"],
            "%Y-%m-%dT%H:%M:%SZ").strftime(formatage_date)
        date_fin_format = datetime.strptime(
            params["date_fin"], "%Y-%m-%dT%H:%M:%SZ").strftime(formatage_date)
        logger.debug(
            f" date_debut_format================= {date_debut_format}")
        logger.debug(f" date_fin_format=================== {date_fin_format}")

        # Création du nom du dossier et du chemin du fichier
        nom_dossier = f"{params['path_enregistrement_dataset']}/{params['station_id']}/{params['pas']}/{params['station_id']}_{date_debut_format}_to_{date_fin_format}"
        os.makedirs(nom_dossier, exist_ok=True)
        logger.debug(f" nom_dossier {nom_dossier}")
        # Vérification de l'existence du fichier et ajout d'un indice supplementaire si nécessaire
        indice = 1
        # chemin_fichier = f"{nom_dossier}/{params['station_id']}/{params['pas']}/{date_debut_format}_to_{date_fin_format}_{indice}.csv"
        chemin_fichier = f"{nom_dossier}/{params['station_id']}_{date_debut_format}_to_{date_fin_format}_{indice}.csv"
        while os.path.exists(chemin_fichier):
            indice += 1
            chemin_fichier = f"{nom_dossier}/{params['station_id']}_{date_debut_format}_to_{date_fin_format}_{indice}.csv"
            # chemin_fichier = f"{nom_dossier}/{params['station_id']}/{params['pas']}/{date_debut_format}_to_{date_fin_format}_{indice}.csv"
        logger.debug(f" chemin_fichier {chemin_fichier}")

        # Enregistrement du fichier
        # logger.debug(f" response_content {response_content}")

        with open(chemin_fichier, "w", encoding=params["encodage"]) as fichier:
            fichier.write(response_content.decode(params["encodage"]))
        logger.info(
            f"Le fichier CSV a été enregistré avec succès: {chemin_fichier}")
        return f"Le fichier CSV a été enregistré avec succès: {chemin_fichier}"
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du fichier: {e}")
        return f"Erreur lors de l'enregistrement du fichier: {e}"
