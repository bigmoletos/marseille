import requests
import json
import urllib.parse
from urllib.parse import quote, urlencode
import logging
import requests
import urllib.parse
import pandas as pd
import numpy as np
import json
import logging
import urllib3
from datetime import datetime
from functools import reduce
import pytz
import logging
from gestion_logging import reconfigurer_logging

""" approche  utilisant le mode debug de edge:
Inspection du Réseau

onglet Réseau : Rafraîchissez la page tout en ayant l'onglet "Réseau" ouvert pour capturer toutes les requêtes effectuées par la page.

Recherchez des requêtes qui semblent télécharger les données que l'on souhaite extraire.

Ces requêtes peuvent retourner des données au format JSON
"""

#  Gestion des logs
logger = logging.getLogger('colorlog_example')
# Utilisation de la fonction
path_datasets = "Projet_Meteo/Datasets/meteo_france/upload_dataset_depuis_api/".replace('\\', '/')
# path_fichier_logs="projet_meteo\\Projet_Meteo\\log\\fichier.log"
params = {
    "path_datasets": path_datasets,
    # "path_fichier_logs":path_fichier_logs,
    "niveau_log": 'DEBUG',  # 'DEBUG' 'INFO' 'WARNING' 'ERROR'  'CRITICAL'
}

# Configuration du logging
reconfigurer_logging(params)



def format_utc_date_str(date_str):
    # Détecter si la date contient des heures et des minutes
    try:
        if date_str == "now()":
            # Retourne immédiatement "now()" pour être utilisé dans la requête
            utc_now = datetime.now(pytz.utc)
            date = utc_now.strftime('%Y-%m-%dT%H:%M:%SZ')
            return date
        # Supporte les formats avec et sans l'heure
        if "T" in date_str:
            format_str = "%Y-%m-%dT%H:%M:%SZ"
        else:
            format_str = "%Y-%m-%d"
        # Parse la date selon le format détecté
        utc_dt = datetime.strptime(date_str, format_str)
    except ValueError:
        print("Format de date non reconnu.")
        return None
    # Formater la date/horaire en UTC pour correspondre au format attendu
    date = utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    logger.debug(f"date : {date}")
    return date


#  Version pour charger plusieurs tables en même temps
## Fonction scrapping avec choix date, compilant plusieurs  requetes: météo,vagues, test ...


def scrapping_mobilis(pas, date_debut, date_fin="now()"):
    """
    Extrait les données de température, vitesse et direction du vent, pression, et humidité pour une période spécifiée,
    ainsi que des données sur les vagues.

    Paramètres :
    - jours (int) : Nombre de jours à partir de maintenant pour le début de la période de données.
    - pas (int) : Pas de temps en minutes pour l'agrégation des données.
    - date_fin (str) : Date de fin pour la collecte des données. "now()" par défaut pour utiliser le moment présent.

    Retourne :
    - DataFrame contenant les données extraites.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    list_col = []
    requete = []
    date_end = format_utc_date_str(date_fin)
    date_star = format_utc_date_str(date_debut)
    logger.debug(f"\n date_debut:\n{date_star} \n")
    logger.debug(f"\n date_fin:\n{date_end} \n")

    # # Construction de la requête pour météo
    # requete_meteo = f"""
    # SELECT mean("temperature_digital_Avg") AS "temperature_(°)", mean("wind_speed_digital") AS "wind_speed_(kn)",
    # max("wind_speed_digital_Max") AS "rafale_(kn)", mean("wind_direction_digital") AS "wind_direction",
    # mean("pressure_digital_Avg") AS "pression_(bar)", mean("humidity_digital_Avg") AS "humidity_(%)"
    # FROM "planier_meteo"
    # WHERE ("host"::tag = '0') AND time >= now() - {jours}d and time <= {date_fin}
    # GROUP BY time({pas}m) fill(none)
    # """

    # planier_current:
    # ['CurrentDirection_Avg1', 'CurrentDirection_Avg10', 'CurrentDirection_Avg11', 'CurrentDirection_Avg12', 'CurrentDirection_Avg13', 'CurrentDirection_Avg14', 'CurrentDirection_Avg15', 'CurrentDirection_Avg16', 'CurrentDirection_Avg17', 'CurrentDirection_Avg18', 'CurrentDirection_Avg19', 'CurrentDirection_Avg2', 'CurrentDirection_Avg20', 'CurrentDirection_Avg21', 'CurrentDirection_Avg22', 'CurrentDirection_Avg23', 'CurrentDirection_Avg24', 'CurrentDirection_Avg25', 'CurrentDirection_Avg3', 'CurrentDirection_Avg4', 'CurrentDirection_Avg5', 'CurrentDirection_Avg6', 'CurrentDirection_Avg7', 'CurrentDirection_Avg8', 'CurrentDirection_Avg9', 'CurrentSpeed_Avg1', 'CurrentSpeed_Avg10', 'CurrentSpeed_Avg11', 'CurrentSpeed_Avg12', 'CurrentSpeed_Avg13', 'CurrentSpeed_Avg14', 'CurrentSpeed_Avg15', 'CurrentSpeed_Avg16', 'CurrentSpeed_Avg17', 'CurrentSpeed_Avg18', 'CurrentSpeed_Avg19', 'CurrentSpeed_Avg2', 'CurrentSpeed_Avg20', 'CurrentSpeed_Avg21', 'CurrentSpeed_Avg22', 'CurrentSpeed_Avg23', 'CurrentSpeed_Avg24', 'CurrentSpeed_Avg25', 'CurrentSpeed_Avg3', 'CurrentSpeed_Avg4', 'CurrentSpeed_Avg5', 'CurrentSpeed_Avg6', 'CurrentSpeed_Avg7', 'CurrentSpeed_Avg8', 'CurrentSpeed_Avg9', 'RECNBR', 'temperature_eau_Avg']

    # PlanierTest:
    # ['humidity_digital_avg', 'pressure_digital_avg', 'record', 'temperature_digital_avg', 'wind_direction_digital', 'wind_speed_digital', 'wind_speed_digital_max', 'wind_speed_digital_wvc']

    # planier_meteo:
    # ['RECNBR', 'humidity_digital_Avg', 'pressure_digital_Avg', 'temperature_digital_Avg', 'wind_direction_digital', 'wind_speed_digital', 'wind_speed_digital_Max', 'wind_speed_digital_WVc\r']

    # planier_wave:
    # ['Direction_Seaview', 'H_seaview', 'Hmax_seaview', 'Periode_seaview', 'RECNBR', 'heading_seaview']

    # Construction de la requête pour météo
    # ['RECNBR', 'humidity_digital_Avg', 'pressure_digital_Avg', 'temperature_digital_Avg', 'wind_direction_digital', 'wind_speed_digital', 'wind_speed_digital_Max', 'wind_speed_digital_WVc\r']
    requete_meteo = f"""
    SELECT mean("temperature_digital_Avg") AS "temperature_(°C)",
    mean("wind_speed_digital") AS "vitesse_(kn)",
    max("wind_speed_digital_Max") AS "rafale_(kn)",
    mean("wind_direction_digital") AS "direction_(°)",
    mean("pressure_digital_Avg") AS "pression_(bar)",
    mean("humidity_digital_Avg") AS "humidity_(%)"
    FROM "planier_meteo"
    WHERE ("host"::tag = '0') AND time >= '{date_star}' and time <= '{date_end}'
    GROUP BY time({pas}m) fill(none)
    """

    # Construction de la requête pour les vagues
    # ['Direction_Seaview', 'H_seaview', 'Hmax_seaview', 'Periode_seaview', 'RECNBR', 'heading_seaview']
    requete_vagues = f"""
    SELECT mean("Hmax_seaview") AS "wave_amplitude",
    mean("Direction_Seaview") AS "wave_direction",
    mean("Periode_seaview") AS "wave_period"
    FROM "planier_wave"
    WHERE ("host"::tag = '0') AND time >=  '{date_star}' and time <= '{date_end}'
    GROUP BY time({pas}m) fill(none)
    """

    requete_current = f"""
    SELECT mean("CurrentDirection_Avg1") as "direction_de_surface_(°)",
    mean("temperature_eau_Avg") as "temperature_eau_(°C)",
    mean("CurrentSpeed_Avg1") as "vitesse_surface_(m/s)"
    FROM "planier_current"
    WHERE ("host"::tag = '0') AND time >=  '{date_star}' and time <= '{date_end}'
    GROUP BY time({pas}m) fill(none)

    """
    # ['humidity_digital_avg', 'pressure_digital_avg', 'record', 'temperature_digital_avg', 'wind_direction_digital', 'wind_speed_digital', 'wind_speed_digital_max', 'wind_speed_digital_wvc']
    requete_test = f"""
    SELECT mean("humidity_digital_avg") as "humidity_(%)",
    mean("pressure_digital_avg") as "pression_(bar)",
    mean("temperature_digital_avg") as "temperature_(°C)",
    mean("wind_direction_digital") as "direction_(°)",
    mean("wind_speed_digital") as "vitesse_(kn)",
    mean("wind_speed_digital_max") as "rafale_(kn)"
    FROM "PlanierTest"
    WHERE ("host"::tag = '0') AND time >=  '{date_star}' and time <= '{date_end}'
    GROUP BY time({pas}m) fill(none)
    """

    # FROM "planier_wave"
    # requete_vagues = f"""
    # SELECT mean("Hmax_seaview") AS "wave_amplitude", mean("Direction_Seaview") AS "wave_direction", mean("Periode_seaview") AS "wave_period"
    # FROM "planier_wave"
    # WHERE ("host"::tag = '0') AND time >= now() - 6h and time <= now() GROUP BY time(30s) fill(none)
    # """

    # Listes des requetes
    liste_requetes = [
        requete_test, requete_meteo, requete_vagues, requete_current
    ]
    # liste_requetes = [requete_test]

    dfs = []  # Liste pour stocker les DataFrames

    for requete in liste_requetes:
        logger.debug(f"\n requete:\n{requete} \n")
        requete_coded = urllib.parse.quote(requete)

        url_base = "https://portal.mobilis-sa.com:3000/api/datasources/proxy/uid/b9a4921f-a996-41fa-9606-fdec0083af61/query?db=dbplanier&q="
        url = url_base + requete_coded

        try:
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                verify=False)
            # logger.debug(f"response:  {response.text}")

            if response.status_code == 200:
                json_data = json.loads(response.text)
                df_temp = pd.json_normalize(
                    json_data,
                    record_path=['results', 'series', 'values'],
                    errors='ignore')
                logger.debug(f"df_temp:  {df_temp.head(2)}")

                if requete == requete_vagues:
                    list_col = [
                        "date", "wave_amplitude_(m)", "wave_direction_(°)",
                        "wave_period_(s)"
                    ]
                elif requete == requete_meteo:
                    list_col = [
                        'date', 'temperature_(°C)', 'vitesse_(kn)',
                        'rafale_(kn)', 'direction_(°)', 'pression_(bar)',
                        'humidity_(%)'
                    ]
                elif requete == requete_current:
                    list_col = [
                        'date', 'direction_de_surface_(°)',
                        'temperature_eau_(°C)', 'vitesse_surface_(m/s)'
                    ]
                elif requete == requete_test:
                    list_col = [
                        'date', "humidity_(%)", "pression_(bar)",
                        "temperature_(°C)", "direction_(°)", "vitesse_(kn)",
                        "rafale_(kn)"
                    ]
                df_temp.columns = list_col
                logger.debug(f"df_temp.columns:  {df_temp.columns.tolist()}")

                dfs.append(df_temp)

            else:
                logger.error(  f"Erreur lors de la requête: {response.status_code}")

        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête : {e}")

    # # Après avoir exécuté les deux requêtes et stocké les résultats dans dfs,
    # # fusionnez les DataFrames sur la colonne 'date'
    # if len(dfs) == 2:
    #     df_final = pd.merge(dfs[0], dfs[1], on="date", how="outer")
    # elif len(dfs) == 3:
    #     df_final = pd.merge(dfs[0], dfs[1], on="date", how="outer")
    #     df_final = pd.merge(df_final, dfs[1], on="date", how="outer")
    #     return df_final
    # else:
    #     return pd.DataFrame()  # Retourner un DataFrame vide en cas de problème

    # fusionnez les DataFrames sur la colonne 'date'
    if dfs:
        # Étape 1: Fusionner dynamiquement tous les DataFrames sur la colonne 'date'
        df_final = reduce(
            lambda left, right: pd.merge(left, right, on="date", how="outer"),
            dfs)

        # Étape 2: Consolider les colonnes redondantes
        # On obtient la liste de toutes les colonnes
        all_columns = df_final.columns.tolist()
        logger.debug(f"all_columns   {all_columns}")
        # On identifie les colonnes redondantes
        redundant_columns = {
            col.split('_x')[0]: col
            for col in all_columns if '_x' in col
        }
        logger.debug(f"redundant_columns:  {redundant_columns}")
        for base_col, col in redundant_columns.items():
            # Initialisez la colonne de base si elle n'existe pas
            if base_col not in df_final.columns:
                df_final[base_col] = np.nan  # Initialisation avec NaN

            # Liste des colonnes similaires basées sur le nom de base
            similar_cols = [c for c in all_columns if base_col in c]
            logger.debug(f"similar_cols:  {similar_cols}")

            # Fusion des colonnes similaires dans la colonne de base
            for similar_col in similar_cols:
                df_final[base_col] = df_final[base_col].combine_first(
                    df_final[similar_col])
                # Supprimer la colonne redondante après consolidation
                df_final.drop(columns=[similar_col], inplace=True)

        # # Étape 3: Nettoyer les éventuelles colonnes en double
        # df_final = df_final.loc[:,~df_final.columns.duplicated()]

        # # Étape 4: Assurez-vous que l'index est correct après toutes les opérations
        # df_final.reset_index(drop=True, inplace=True)

    else:
        df_final = pd.DataFrame()  # Retourner un DataFrame vide en cas de problème

    return df_final


# df_mobilis_vagues = scrapping_mobilis(300, 1,date_fin = "2023-10-30T23:59:59Z")
# df_mobilis_vagues = scrapping_mobilis(300, 1,date_fin = "now()")
# df_mobilis3 = scrapping_mobilis(1, "2023-01-01",  "now()")
# df_mobilis3 = scrapping_mobilis(1, "2022-01-01", "now()")
# df_mobilis3


#  version avec une seule requete


# def format_utc_date_str(date_str):
#     # Détecter si la date contient des heures et des minutes
#     try:
#         # Supporte les formats avec et sans l'heure
#         if "T" in date_str:
#             format_str = "%Y-%m-%dT%H:%M:%SZ"
#         else:
#             format_str = "%Y-%m-%d"
#         # Parse la date selon le format détecté
#         utc_dt = datetime.strptime(date_str, format_str)
#     except ValueError:
#         print("Format de date non reconnu.")
#         return None

#     # Formater la date/horaire en UTC pour correspondre au format attendu
#     return utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# # def scrapping_mobilis(jours, pas, date_fin="now()"):
# def scrapping_mobilis(pas, date_debut,  date_fin="now()"):
#     """
#     Extrait les données de température, vitesse et direction du vent, pression, et humidité pour une période spécifiée,
#     ainsi que des données sur les vagues.

#     Paramètres :
#     - jours (int) : Nombre de jours à partir de maintenant pour le début de la période de données.
#     - pas (int) : Pas de temps en minutes pour l'agrégation des données.
#     - date_fin (str) : Date de fin pour la collecte des données. "now()" par défaut pour utiliser le moment présent.

#     Retourne :
#     - DataFrame contenant les données extraites.
#     """
#     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#     list_col=[]
#     requete=[]
#     date_end = format_utc_date_str(date_fin)
#     date_star = format_utc_date_str(date_debut)
#     logger.debug(f"\n date_debut:\n{date_star} \n")
#     logger.debug(f"\n date_fin:\n{date_end} \n")

#     # # Construction de la requête pour météo
#     # requete_meteo = f"""
#     # SELECT mean("temperature_digital_Avg") AS "temperature_(°)", mean("wind_speed_digital") AS "wind_speed_(kn)",
#     # max("wind_speed_digital_Max") AS "rafale_(kn)", mean("wind_direction_digital") AS "wind_direction",
#     # mean("pressure_digital_Avg") AS "pression_(bar)", mean("humidity_digital_Avg") AS "humidity_(%)"
#     # FROM "planier_meteo"
#     # WHERE ("host"::tag = '0') AND time >= now() - {jours}d and time <= {date_fin}
#     # GROUP BY time({pas}m) fill(none)
#     # """
#     # Construction de la requête pour météo
#     requete_meteo = f"""
#     SELECT mean("temperature_digital_Avg") AS "temperature_(°)", mean("wind_speed_digital") AS "wind_speed_(kn)",
#     max("wind_speed_digital_Max") AS "rafale_(kn)", mean("wind_direction_digital") AS "wind_direction",
#     mean("pressure_digital_Avg") AS "pression_(bar)", mean("humidity_digital_Avg") AS "humidity_(%)"
#     FROM "planier_meteo"
#     WHERE ("host"::tag = '0') AND time >= '{date_star}' and time <= '{date_end}'
#     GROUP BY time({pas}m) fill(none)
#     """

#     # Construction de la requête pour les vagues
#     requete_vagues = f"""
#     SELECT mean("Hmax_seaview") AS "wave_amplitude", mean("Direction_Seaview") AS "wave_direction",
#     mean("Periode_seaview") AS "wave_period"
#     FROM "planier_wave"
#     WHERE ("host"::tag = '0') AND time >=  '{date_star}' and time <= '{date_end}'
#     GROUP BY time({pas}m) fill(none)
#     """

#     # FROM "planier_wave"
#     # requete_vagues = f"""
#     # SELECT mean("Hmax_seaview") AS "wave_amplitude", mean("Direction_Seaview") AS "wave_direction", mean("Periode_seaview") AS "wave_period"
#     # FROM "planier_wave"
#     # WHERE ("host"::tag = '0') AND time >= now() - 6h and time <= now() GROUP BY time(30s) fill(none)
#     # """

#     # Choisissez la requête à utiliser (météo ou vagues) en fonction de vos besoins
#     # requete = requete_meteo  # ou requete_vagues
#     # requete = requete_vagues  # ou requete_vagues
#     liste_requetes = [requete_meteo, requete_vagues]  # ou requete_vagues
#     for requete in liste_requetes:
#         logger.debug(f"\n requete:\n{requete} \n")
#         requete_coded = urllib.parse.quote(requete)
#         # https://portal.mobilis-sa.com:3000/api/datasources/proxy/uid/b9a4921f-a996-41fa-9606-fdec0083af61/query?db=dbplanier&q=
#         url_base = "https://portal.mobilis-sa.com:3000/api/datasources/proxy/uid/b9a4921f-a996-41fa-9606-fdec0083af61/query?db=dbplanier&q="
#         url = url_base + requete_coded

#         try:
#             response = requests.get(url, headers={'Content-Type': 'application/json'}, verify=False)

#             if response.status_code == 200:
#                 json_data = json.loads(response.text)
#                 df = pd.json_normalize(json_data, record_path=['results', 'series', 'values'], errors='ignore')
#                 logging.error(f"liste colonnes  {df.columns.to_list()}")
#                 logging.error(f"liste colonnes  {df.head(2)}")

#                 if requete == requete_vagues:
#                     list_col=[ "date",  "wave_amplitude","wave_direction","wave_period"]
#                 elif requete == requete_meteo:
#                     list_col=['date', 'temperature_(°)', 'wind_speed_(kn)', 'rafale_(kn)', 'direction', 'pression_(bar)', 'humidity_(%)']
#                 df.columns = list_col
#                 logging.error(f"list_col  {df.columns.to_list()}")
#                 # df.columns = ['date', 'temperature_(°)', 'wind_speed_(kn)', 'rafale_(kn)', 'direction', 'pression_(bar)', 'humidity_(%)']

#                 return df
#             else:
#                 logging.error(f"Erreur lors de la requête: {response.status_code}")
#                 return pd.DataFrame()
#         except Exception as e:
#             logging.error(f"Erreur lors de l'exécution de la requête : {e}")
#             return pd.DataFrame()