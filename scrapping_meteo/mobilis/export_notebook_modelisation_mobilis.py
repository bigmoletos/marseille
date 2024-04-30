# %% [markdown]
# # Scrapping de la balise méteo de mobilis DB8000 du phrare du planier
# https://portal.mobilis-sa.com:3000/d/e9ad019c-7bc0-4d90-ab9a-3146bffa7b1d/db-planier-meteo?from=now-30d&to=now&orgId=2&refresh=auto

# %% [markdown]
# pour windsup
# https://www.winds-up.com/spot-marseille-pointe-rouge-digue-windsurf-kitesurf-44-observations-releves-vent.html

# %% [markdown]
# ### drive de sotckage des datasets
#
# https://drive.google.com/drive/folders/1vG0EGdLS91CY-TJV6FK100vkKFna_dzv

# %% [markdown]
# # Parametrage notebook

# %% [markdown]
# ## Installation modules

# %%
# !pip install certifi
# !python -m pip install certifi
# !pip install --upgrade pyppeteer
# !pip install urllib3
# !pip install selenium
# !pip install webdriver-manager
# !pip install selenium --upgrade

# !pip install numpy==1.24.3
# !pip install h5py
# !pip install wrapt>=1.11.0
# !pip install click==7.1.1
# !pip install networkx>=2.4
# !pip install pandas>=0.25.3
# !pip install pydantic
# !pip install requests
# !pip install smart-open
# !pip install statsmodels
# !pip install dateparser
# !pip install tensorflow
# ! pip install "unsloth[cu121-ampere-torch220] @ git+https://github.com/unslothai/unsloth.git"
# !pip install torch torchvision torchaudio
# !setx PATH "%PATH%;C:\Users\romar\AppData\Roaming\Python\Python311\Scripts"
# !pip install xgboost
# !pip install tensorboard
# !pip install pmdarima
# !pip install pytz
# !pip install --upgrade pmdarima statsmodels numpy pandas


# %% [markdown]
# ## Ajout du chemin outils dans le PATH

# %%
import sys

file_to_add = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\outils'
sys.path.append(file_to_add.replace('\\', '/'))


# %% [markdown]
# # Mise en place logging
# appel à la fonction ***def reconfigurer_logging(params)***:
#
#     """
#     Reconfigure le logging avec le niveau et le format spécifiés à partir du dictionnaire params,
#     en ajoutant des couleurs au logs selon leur niveau de gravité.
#     """
#
#     # Assurez-vous que 'niveau_log' et 'format_log' sont définis dans params
#
#     niveau = params['niveau_log'].upper()
#     format_log = params['format_log']
#     format_log_file = params['format_log_file']......
#
#
# debugeur avec le mot magique %debug
#
# - n (next) : Exécute la ligne suivante du programme. Si la ligne suivante est une fonction, elle exécutera la fonction sans entrer dans celle-ci.
# - s (step) : Exécute la ligne suivante du programme et entre dans les fonctions appelées.
# - c (continue) : Continue l'exécution jusqu'au prochain point d'arrêt.
# - q (quit) : Quitte le débogueur et termine l'exécution du programme.
# - l (list) : Affiche l'emplacement actuel dans le code.
# - p : Imprime la valeur de l'expression qui suit (par exemple, p variable_name affiche la valeur de variable_name).
# - h (help) : Affiche une liste des commandes disponibles.

# %%
import sys
from pathlib import Path
from get_path_dossier_or_files import trouver_chemin_element_depuis_workspace

# projet_meteo\Projet_Meteo\outils\get_path_dossier_or_files.py

chemin_outils = trouver_chemin_element_depuis_workspace("outils", est_un_dossier=True)


# %%



# %% [markdown]
# #### ajout dans le path des dossiers pour upload les datasets upload_data_depuis_api ou autres

# %%
# %%capture captureajoutpath
# Ajout dans le path du dossier de sauvegarde des datasets
# Formatage et sauvegarde du df   C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\data_mobilis\upload_data_depuis_api

# MOBILIS
from regex import P

# DATA
nom_element = "data_mobilis/upload_data_depuis_api"
path_data_mobilis_upload_data_depuis_api = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print( f"\n path_data_mobilis_upload_data_depuis_api:\n{path_data_mobilis_upload_data_depuis_api} \n")

# METEO FRANCE
# nom_element = "meteo_france/upload_dataset_depuis_api/13001009/horaire/01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59"
nom_element = "meteo_france/upload_dataset_depuis_api"
path_data_meteo_france_upload_data_depuis_api = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_data_meteo_france_upload_data_depuis_api:\n{path_data_meteo_france_upload_data_depuis_api} \n")

# chemin de sauvegarde des datasets meteo france scrappé par l'api, donnnées brutes
nom_element = "meteo_france/upload_dataset_depuis_api2"
path_data_meteo_france_upload_data_depuis_api2 = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print( f"\n path_data_meteo_france_upload_data_depuis_api2:\n{path_data_meteo_france_upload_data_depuis_api2} \n")

# chemin de sauvegarde des datasets meteo france scrappé par l'api dont les colonnes sont renommées et converties
nom_element="sauve_df_col_renamed"
path_data_meteo_france_api2_col_renamed = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_data_meteo_france_api2_col_renamed:\n{path_data_meteo_france_api2_col_renamed} \n")

# chemin de sauvegarde des datasets meteo france, mobilis, windsup, fusionnés
nom_element = "datasets_fusionned"
path_data_meteo_france_api2_datasets_fusionned = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_data_meteo_france_api2_datasets_fusionned:\n{path_data_meteo_france_api2_datasets_fusionned} \n")

# chemin du dossier contenant les fichiers donnés par meteo france au pas de 6 min sources .txt
nom_element = "DONNEES_6_MNs_POUR_WIND"
path_datasets_fourni_par_meteo_france_6min_source = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_datasets_fourni_par_meteo_france_6min_source:\n{path_datasets_fourni_par_meteo_france_6min_source} \n")

# chemin de sauvegarde des fichiers onnés par meteo france au pas de 6 min traités, renommage des colonnes, conversion,
nom_element = "traitement_datasets_fourni_par_meteo_france_6min"
path_sauvegarde_datasets_meteo_france_6min_clean = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauvegarde_datasets_meteo_france_6min_clean:\n{path_sauvegarde_datasets_meteo_france_6min_clean} \n")

# chemin de sauvegarde des fichiers onnés par meteo france au pas de 6 min traités, suppression des colonnes vides
nom_element = "traitement_datasets_fourni_par_meteo_france_6min_clean"
path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide:\n{path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide} \n")

# chemin de sauvegarde des fichiers donnés par meteo france au pas de 6 min traités, suppression des outliers
nom_element = "traitement_datasets_fourni_par_meteo_france_6min_clean_sans_outliers"
path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier= trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier:\n{path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier} \n")


# WINDSUP
nom_element = "data_windsup"
path_data_windsup_upload_data_depuis_api = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print( f"\n path_data_windsup_upload_data_depuis_api:\n{path_data_windsup_upload_data_depuis_api} \n")

nom_element = "df_preprocessing"
path_dossier_windsup_renamed=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_dossier_windsup_renamed:\n{path_dossier_windsup_renamed} \n")

nom_element = "df_windsup_renamed.csv"
# chemin_dossier_windsups_renamed = os.path.join(path_data_windsup_upload_data_depuis_api, chemin_sauvegarde_df_windsup_preprocessed)
path_fichier_windsup_renamed=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=False)
print(f"\n path_fichier_windsup_renamed:\n{path_fichier_windsup_renamed} \n")


# MODELES

## WINDSUP
nom_element = "sauvegarde_modeles\model_windsup"
path_sauve_modeles_windsup=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauve_modeles_windsup:\n{path_sauve_modeles_windsup} \n")
## Mobilis
nom_element = "sauvegarde_modeles\model_mobilis"
path_sauve_modeles_mobilis=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauve_modeles_mobilis:\n{path_sauve_modeles_mobilis} \n")
## Meteo france 6min
nom_element = "sauvegarde_modeles\model_meteo_france_6min"
path_sauve_modeles_meteo_france_6min=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauve_modeles_meteo_france_6min:\n{path_sauve_modeles_meteo_france_6min} \n")
## Meteo france 1h
nom_element = "sauvegarde_modeles\model_meteo_france_1h"
path_sauve_modeles_meteo_france_1h= trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauve_modeles_meteo_france_1h:\n{path_sauve_modeles_meteo_france_1h} \n")


# CONCATENATION ALL DATASETS

# projet_meteo\Projet_Meteo\Datasets\Concatenation_all_datasets\dataset_interpolated_pas_moyen
## dossier principal
nom_element = "Concatenation_all_datasets"
path_Concatenation_all_datasets=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_Concatenation_all_datasets:\n{path_Concatenation_all_datasets} \n")

## dossier des dataset interpolés au pas moyen de 12 min par exemple
nom_element = "Concatenation_all_datasets\dataset_interpolated_pas_moyen"
path_dataset_interpolated_pas_moyen=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_dataset_interpolated_pas_moyen:\n{path_dataset_interpolated_pas_moyen} \n")

## dossier des datasets normalisés
nom_element = "Concatenation_all_datasets\datasets_normalized"
path_datasets_normalized=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_datasets_normalized:\n{path_datasets_normalized} \n")

## dossier de sauvegarde des datasets concatener
nom_element = "Concatenation_all_datasets\sauvegarde"
path_sauve_all_dataset_concatenated=trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
print(f"\n path_sauve_all_dataset_concatenated:\n{path_sauve_all_dataset_concatenated} \n")









# %% [markdown]
# #### choix du mode de log entre 'DEBUG' 'INFO' 'WARNING' 'ERROR'  'CRITICAL'

# %%
# %%capture capturechoixlog
import logging
from gestion_logging import reconfigurer_logging

logger = logging.getLogger('colorlog_example')
# Utilisation de la fonction
path_datasets = "Projet_Meteo/Datasets/meteo_france/upload_dataset_depuis_api/".replace(
    '\\', '/')
# path_fichier_logs="projet_meteo\\Projet_Meteo\\log\\fichier.log"
params = {
    "path_datasets": path_datasets,
    # "path_fichier_logs":path_fichier_logs,
    "niveau_log": 'WARNING',  # 'DEBUG' 'INFO' 'WARNING' 'ERROR'  'CRITICAL'
}

# Configuration du logging
reconfigurer_logging(params)


# %% [markdown]
# ## Fonction de chargement dataset mobilis

# %%
from gestion_logging import reconfigurer_logging
import pandas as pd
import logging
import os
import sys


# Remonter de trois niveaux à partir du notebook
path_to_outils = os.path.join(os.getcwd(), '..', '..', 'Projet_Meteo','outils')
# Normaliser le chemin pour résoudre tous les liens symboliques et les références relatives
path_to_outils = os.path.normpath(path_to_outils)
# Ajouter le chemin à sys.path
sys.path.append(path_to_outils)
logger = logging.getLogger('colorlog_example')

def load_dataframe(df_name, path, format_type='csv', sep=","):
    """
    Charge un DataFrame à partir d'un fichier en spécifiant le format souhaité.
    Paramètres :
    - df_name (str) : Nom de base du DataFrame à charger (sans extension).
    - path (str) : Chemin du dossier contenant le fichier.
    - format_type (str) : Format du fichier ('csv', 'json', 'pkl').
    Retourne :
    - DataFrame chargé.
    """
    # Construction du chemin complet du fichier
    file_basename = os.path.join(path, df_name)
    logger.debug(f" file_basename:  {file_basename}")
    try:
        # Chargement du DataFrame en fonction du format spécifié
        if format_type == 'csv':
            filepath = f"{file_basename}.csv"
            # df = pd.read_csv(filepath)
            df = pd.read_csv(filepath, on_bad_lines='skip',sep=sep)

            logger.info(f"DataFrame loaded from CSV at {filepath}")
        elif format_type == 'json':
            filepath = f"{file_basename}.json"
            df = pd.read_json(filepath, orient='split')
            logger.info(f"DataFrame loaded from JSON at {filepath}")
        elif format_type == 'pkl':
            filepath = f"{file_basename}.pkl"
            df = pd.read_pickle(filepath)
            logger.info(f"DataFrame loaded from pickle HDF5 at {filepath}")
        else:
            raise ValueError("Unsupported file format. Please choose 'csv', 'json', or 'h5'." )
        return df
    except Exception as e:
        logger.error(f"An error occurred while loading the file: {e}")
        raise e


# %% [markdown]
# ### Chargement dataset mobilis

# %% [markdown]
# #### charge les 2 datasets bruts

# %%
# Chargement du dataset mobilis df_mobilis
# df_mobilis = load_dataframe("df_mobilis", r"../../Projet_Meteo/Datasets/data_mobilis/upload_data_depuis_api", format_type='pkl')
df_mobilis3_7col = load_dataframe("df_mobilis3_7col",  path_data_mobilis_upload_data_depuis_api,
                                  format_type='pkl')
df_mobilis3_12col = load_dataframe("df_mobilis3_12col", path_data_mobilis_upload_data_depuis_api,
                                   format_type='pkl')


# %% [markdown]
# #### charge les 2 datasets sans NA ni outliers

# %%
# Chargement du dataset mobilis df_mobilis
# df_mobilis = load_dataframe("df_mobilis", r"../../Projet_Meteo/Datasets/data_mobilis/upload_data_depuis_api", format_type='pkl')
df_clean_7col = load_dataframe("df_clean_7col",  path_data_mobilis_upload_data_depuis_api,
                                  format_type='pkl')
df_clean_12col = load_dataframe("df_clean_12col", path_data_mobilis_upload_data_depuis_api,
                                   format_type='pkl')


# %%
df_clean_12col


# %%
# df_mobilis3_7col


# %% [markdown]
# # METEO FRANCE

# %% [markdown]
# ### parcourir les sous-repertoires et selectionne les stations entre 2 dates, retourne des dico contenant la liste des fichiers csv pour chaque station slectionnées

# %%
# from datetime import datetime
# import os

# logger = logging.getLogger('colorlog_example')

# def selectionner_stations_between_date_retourne_dico(chemin, date_debut, date_fin):
#     """
#     Sélectionne les dossiers parent "horaire" contenant des fichiers CSV entre les dates spécifiées.

#     Args:
#         chemin (str): Chemin du dossier racine à parcourir.
#         date_debut (str): Date de début au format 'dd-MM-yyyy'.
#         date_fin (str): Date de fin au format 'dd-MM-yyyy'.

#     Returns:
#         dict1: Dictionnaire avec le nom du dossier parent et les fichiers CSV entre les dates spécifiées,
#         uniquement si toutes les années prévues entre les dates sont presentes
#         dict2: Dictionnaire avec le nom du dossier parent et les fichiers CSV entre les dates spécifiées.
#         uniquement si toutes les années prévues entre les dates ne sont pas presentes
#         dict3: Dictionnaire avec le nom du dossier parent et les fichiers CSV entre les dates spécifiées,
#     """
#     # Conversion des chaînes de date en objets datetime pour la comparaison
#     date_debut_obj = datetime.strptime(date_debut, '%d-%m-%Y')
#     date_fin_obj = datetime.strptime(date_fin, '%d-%m-%Y')
#     # Convertir les chaînes de caractères en objets datetime
#     date_debut_formated = datetime.strptime(date_debut, '%d-%m-%Y')
#     date_fin_formated = datetime.strptime(date_fin, '%d-%m-%Y')

#     number_of_years = date_fin_formated.year - date_debut_formated.year
#     if (date_fin_formated.month > date_debut_formated.month) or (
#             date_fin_formated.month == date_debut_formated.month
#             and date_fin_formated.day > date_debut_formated.day):
#         number_of_years += 1
#     logger.debug(f"\n number_of_years:\n{number_of_years} \n")
#     stations_between_dates_total = {}
#     stations_between_dates_complet = {}
#     stations_between_dates_incompletes={}
#     for root, dirs, files in os.walk(chemin):
#         if 'horaire' in dirs:
#             chemin_horaire = os.path.join(root, 'horaire')
#             nom_parent = os.path.basename(root)
#             fichiers_csv = []
#             try:
#                 for sous_dossier in next(os.walk(chemin_horaire))[1]:
#                     # Extraction de la date de début à partir du nom de dossier
#                     date_str = sous_dossier.split('_')[1]
#                     # Conversion de la date en objet datetime
#                     date_sous_dossier_obj = datetime.strptime(
#                         date_str, '%d-%b-%Y')
#                     if date_debut_obj <= date_sous_dossier_obj <= date_fin_obj:
#                         chemin_sous_dossier = os.path.join(
#                             chemin_horaire, sous_dossier)
#                         fichiers_csv += [
#                             f for f in os.listdir(chemin_sous_dossier)
#                             if f.endswith('.csv')
#                         ]
#                 if fichiers_csv:
#                     stations_between_dates_total[nom_parent] = {
#                         'compteur': len(fichiers_csv),
#                         'fichiers': fichiers_csv
#                     }
#                     # ne selectionne que les stations dont les dates sont completes
#                     # Sélectionner uniquement les stations avec un historique complet
#                     if len(fichiers_csv) == number_of_years:
#                         stations_between_dates_complet[nom_parent] =  {
#                         'compteur': len(fichiers_csv),
#                         'fichiers': fichiers_csv
#                     }
#                     else:
#                         stations_between_dates_incompletes[nom_parent] =  {
#                         'compteur': len(fichiers_csv),
#                         'fichiers': fichiers_csv
#                     }
#                 # for station, infos in stations_between_dates_total.items():
#                 #     if infos['compteur'] == number_of_years:
#                 #         stations_between_dates_complet.append(station)
#             except Exception as e:
#                 logger.error(f"Erreur lors de l'accès à {chemin_horaire}: {e}")

#     return  stations_between_dates_complet,stations_between_dates_incompletes,stations_between_dates_total


# %% [markdown]
# ### Parcourir les sous-repertoires et selectionner les stations entre 2 dates, retourner des df et les sauvegarder en csv, json et pkl, les df contenant la liste des fichiers csv pour chaque station selectionnées

# %%
from datetime import datetime
import os
import pandas as pd
import logging
from sauve_charge_df_csv_json_pkl import save_dataframe, load_dataframe
# Configuration de base du logger pour éviter les erreurs liées à l'utilisation de logger non défini
logger = logging.getLogger('colorlog_example')

def selectionner_stations_between_date_sauve(chemin, date_debut, date_fin):
    """
    Sélectionne les dossiers parent "horaire" contenant des fichiers CSV entre les dates spécifiées
    et retourne les résultats sous forme de DataFrames pandas.
    Sauvegarde les df au froamt csv, json et pkl

    Args:
        chemin (str): Chemin du dossier racine à parcourir.
        date_debut (str): Date de début au format 'dd-MM-yyyy'.
        date_fin (str): Date de fin au format 'dd-MM-yyyy'.

    Returns:
        Tuple de pandas DataFrames: DataFrames pour les stations complètes, incomplètes et totales.
    """
    date_debut_obj = datetime.strptime(date_debut, '%d-%m-%Y')
    date_fin_obj = datetime.strptime(date_fin, '%d-%m-%Y')

    number_of_years = date_fin_obj.year - date_debut_obj.year + int((date_fin_obj.month, date_fin_obj.day) >= (date_debut_obj.month, date_debut_obj.day))
    logger.debug(f"\n number_of_years:\n{number_of_years} \n")

    stations_between_dates_total = {}
    stations_between_dates_complet = {}
    stations_between_dates_incompletes = {}

    for root, dirs, files in os.walk(chemin):
        if 'horaire' in dirs:
            chemin_horaire = os.path.join(root, 'horaire')
            nom_parent = os.path.basename(root)
            fichiers_csv = []

            try:
                for sous_dossier in next(os.walk(chemin_horaire))[1]:
                    date_str = sous_dossier.split('_')[1]
                    date_sous_dossier_obj = datetime.strptime(date_str, '%d-%b-%Y')
                    if date_debut_obj <= date_sous_dossier_obj <= date_fin_obj:
                        chemin_sous_dossier = os.path.join(chemin_horaire, sous_dossier)
                        fichiers_csv += [f for f in os.listdir(chemin_sous_dossier) if f.endswith('.csv')]

                if fichiers_csv:
                    stations_between_dates_total[nom_parent] = {
                        'compteur': len(fichiers_csv),
                        'fichiers': fichiers_csv
                    }
                    if len(fichiers_csv) == number_of_years:
                        stations_between_dates_complet[nom_parent] = {
                            'compteur': len(fichiers_csv),
                            'fichiers': fichiers_csv
                        }
                    else:
                        stations_between_dates_incompletes[nom_parent] = {
                            'compteur': len(fichiers_csv),
                            'fichiers': fichiers_csv
                        }
            except Exception as e:
                logger.error(f"Erreur lors de l'accès à {chemin_horaire}: {e}")

    # Conversion des dictionnaires en DataFrames
    df_complet = pd.DataFrame.from_dict(stations_between_dates_complet, orient='index').reset_index().rename(columns={'index': 'station'})
    df_incompletes = pd.DataFrame.from_dict(stations_between_dates_incompletes, orient='index').reset_index().rename(columns={'index': 'station'})
    df_total = pd.DataFrame.from_dict(stations_between_dates_total, orient='index').reset_index().rename(columns={'index': 'station'})
    # sauvegarde les 3 df
    chemin_dossier_sauve_liste_df = os.path.join(chemin_dossier, "sauve_liste_df")
    save_dataframe(df_stations_between_dates_complet,"stations_between_dates_complet",chemin_dossier_sauve_liste_df)
    save_dataframe(df_stations_between_dates_incompletes,"stations_between_dates_incompletes",chemin_dossier_sauve_liste_df)
    save_dataframe(df_stations_between_dates_total,"stations_between_dates_total",chemin_dossier_sauve_liste_df)

    return df_complet, df_incompletes, df_total


# %% [markdown]
# ### Utilisation de la fonction selectionner_stations_between_date_sauve()

# %%
 # Utilisation de la fonction selectionner_stations_between_date_sauve

chemin_dossier = path_data_meteo_france_upload_data_depuis_api2
chemin_dossier_sauve_liste_df = os.path.join(chemin_dossier, "sauve_liste_df")
# date_debut = '01-01-2014'
# date_fin = '01-03-2024'

# lancement fonction
# df_stations_between_dates_complet, df_stations_between_dates_incompletes, df_stations_between_dates_total = selectionner_stations_between_date_sauve(chemin_dossier_sauve_liste_df, date_debut, date_fin)

# logger.debug(f"\n stations_between_dates_total:\n{df_stations_between_dates_total.head(2)} \n")
# logger.debug(f"\n stations_between_dates_complet:\n{df_stations_between_dates_complet.head(2)} \n")
# logger.debug(f"\n stations_between_dates_incompletes:\n{df_stations_between_dates_incompletes.head(2)} \n")





# %% [markdown]
# ### sauve les dataframes meteofrance contenant la liste des stations selectionnées avec le nom des fichiers csv, inutile si les df ont déja été sauvés avec la fonction selectionner_stations_between_date_sauve()

# %%
# from sauve_charge_df_csv_json_pkl import save_dataframe, load_dataframe
# chemin_dossier = path_data_meteo_france_upload_data_depuis_api2
chemin_dossier_sauve_liste_df = os.path.join(chemin_dossier, "sauve_liste_df")
# save_dataframe(df_stations_between_dates_complet,"stations_between_dates_complet",chemin_dossier_sauve_liste_df)
# save_dataframe(df_stations_between_dates_incompletes,"stations_between_dates_incompletes",chemin_dossier_sauve_liste_df)
# save_dataframe(df_stations_between_dates_total,"stations_between_dates_total",chemin_dossier_sauve_liste_df)


# %% [markdown]
# ### Charge les listes des  dataframes meteofrance contenant la liste des stations selectionnées avec le nom des fichiers csv

# %%
from sauve_charge_df_csv_json_pkl import save_dataframe, load_dataframe
chemin_dossier = path_data_meteo_france_upload_data_depuis_api2
chemin_dossier_sauve_liste_df = os.path.join(chemin_dossier, "sauve_liste_df")

df_stations_between_dates_complet=load_dataframe("df_stations_between_dates_complet", chemin_dossier_sauve_liste_df, format_type='pkl')
# load_dataframe("df_stations_between_dates_incompletes", chemin_dossier, format_type='pkl')
# load_dataframe("df_stations_between_dates_total", chemin_dossier, format_type='pkl')


# %%
# df_stations_between_dates_complet.head(2  )


# %% [markdown]
# ### Concatene les df par station, supprime les colonnes ayant trop de NA, sauve les df en json, csv, pkl

# %%
import pandas as pd
import os
import logging
import json
import re
from sauve_charge_df_csv_json_pkl import save_dataframe
from descriptif_dataset_meteo_france import expliquer_et_renommer_colonne

# Configuration du logger
logger = logging.getLogger('colorlog_example')
# Initialisation de global_df_dict en tant que dictionnaire vide
global_df_dict = {}


def remove_columns_with_na(df, threshold=0.2):
    """
    Supprime les colonnes d'un DataFrame ayant un pourcentage de valeurs manquantes
    supérieur au seuil spécifié.

    :param df: Le DataFrame pandas à traiter.
    :param threshold: Le seuil de pourcentage de valeurs manquantes pour la suppression des colonnes.
                      La valeur par défaut est 0.2 (20%).
    :return: Un DataFrame avec les colonnes ayant un pourcentage de valeurs manquantes
             inférieur ou égal au seuil spécifié.
    """
    # Calculer le pourcentage de valeurs manquantes pour chaque colonne
    missing_percentage = df.isna().mean()
    # print(f"\n missing_percentage:\n{missing_percentage} \n")
    # Convertir en pourcentage et formater chaque valeur
    formatted_missing_percentage = missing_percentage.apply(lambda x: f"{x*100:.2f}%")

    print(f"\nPourcentage de valeurs manquantes par colonne:\n{formatted_missing_percentage}\n")
    # Identifier les colonnes à conserver (celles avec un pourcentage de Na <= seuil)
    columns_to_keep = missing_percentage[missing_percentage <=
                                         threshold].index.tolist()

    # Filtrer le DataFrame pour ne conserver que les colonnes sélectionnées
    filtered_df = df[columns_to_keep]

    return filtered_df

def extraire_info_fichier(premier_fichier, dernier_fichier):
    """
    Extrait le numéro de la station, la date de début et de fin à partir des noms du premier et dernier fichier.
    """
    logger.debug(f"Extraction des informations à partir des fichiers : {premier_fichier}, {dernier_fichier}")
    try:
        pattern = r'(\d+)_(\d{2})-(\w+)-(\d{4})_at.*to_(\d{2})-(\w+)-(\d{4})_at.*\.csv'
        debut_match = re.search(pattern, premier_fichier)
        fin_match = re.search(pattern, dernier_fichier)

        if debut_match and fin_match:
            station = debut_match.group(1)
            date_debut = debut_match.group(2) + debut_match.group(3)[:3].lower() + debut_match.group(4)
            date_fin = fin_match.group(5) + fin_match.group(6)[:3].lower() + fin_match.group(7)
            nom_df = f"df_{station}_{date_debut}_{date_fin}"
            logger.debug(f"Nom du DataFrame formé : {nom_df}")
            return nom_df
        else:
            logger.error("Impossible d'extraire correctement les informations des fichiers")
            return None
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des informations : {e}")
        return None

def trouver_chemin_complet(chemin_base, station, nom_fichier):
    """
    Recherche de manière récursive le chemin complet d'un fichier donné, sans supposer la nature du sous-dossier (comme 'horaire' ou 'quotidienne').

    Args:
        chemin_base (str): Le chemin de base où débuter la recherche.
        station (str): Identifiant de la station concernée.
        nom_fichier (str): Nom du fichier à rechercher.

    Returns:
        str: Chemin complet du fichier si trouvé, None sinon.
    """
    for racine, dossiers, fichiers in os.walk(os.path.join(chemin_base, station)):
        if nom_fichier in fichiers:
            return os.path.join(racine, nom_fichier)
    logger.warning(f"Fichier {nom_fichier} non trouvé pour la station {station}.")
    return None

def concatener_dataframes_station(df_stations_between_dates_complet, chemin_dossier):
    """
    Concatène les DataFrames de chaque station basé sur les fichiers spécifiés,
    et forme un nom approprié pour chaque DataFrame concaténé.
    supprime les colonnes ayant trop de NA
    """
    # global_df_dict=[]
    global global_df_dict

    # Assurez-vous que global_df_dict est bien un dictionnaire
    if not isinstance(global_df_dict, dict):
        logger.warning("global_df_dict n'est pas un dictionnaire. Réinitialisation effectuée.")
        global_df_dict = {}  # Réinitialise global_df_dict comme un dictionnaire vide

    noms_df = []

    for _, row in df_stations_between_dates_complet.iterrows():
        station = row['station']
        fichiers = sorted(row['fichiers']) if isinstance(row['fichiers'], list) else sorted(json.loads(row['fichiers']))
        logger.debug(f"Traitement de la station {station} avec {len(fichiers)} fichiers.")

        if fichiers:
            # Trouver le chemin complet et charger les fichiers
            dfs = []
            for fichier in fichiers:
                chemin_complet = trouver_chemin_complet(chemin_dossier, station, fichier)
                if chemin_complet:
                    try:
                        df = pd.read_csv(chemin_complet, sep=";",on_bad_lines='skip')
                        dfs.append(df)
                        logger.debug(f"Fichier {fichier} chargé avec succès.")
                    except Exception as e:
                        logger.error(f"Erreur lors du chargement du fichier {fichier}: {e}")

            # Concaténer, nettoyer  et stocker le DataFrame
            if dfs:
                logger.debug(f"dfs   {dfs}")
                df_concatene = pd.concat(dfs, ignore_index=True)
                nom_df = extraire_info_fichier(fichiers[0], fichiers[-1])
                if nom_df:
                    # supprime les colonnes ayant plus de 20 % de na
                    df_concatene_cleaned =remove_columns_with_na(df_concatene)
                    # rend le df accessible gloabalement
                    global_df_dict[nom_df] = df_concatene_cleaned
                    logger.debug(f"nom_df   {nom_df}")
                    noms_df.append(nom_df)
                    logger.debug(f"DataFrame {nom_df} créé et ajouté au dictionnaire global.")
                    # enregistre le df
                    chemin_dossier_sauve_df = os.path.join(chemin_dossier, "sauve_df")
                    save_dataframe(df_concatene_cleaned,nom_df.replace("df_",""),chemin_dossier_sauve_df)
            else:
                logger.warning(f"Aucun DataFrame créé pour la station {station}.")
    # enregistre la liste des df df
    chemin_dossier_sauve_liste_df_clean = os.path.join(chemin_dossier, "sauve_liste_df_clean")
    save_dataframe(noms_df,"liste_df_clean",chemin_dossier_sauve_liste_df_clean)

    logger.debug("Concaténation terminée pour toutes les stations.")
    return noms_df


# %%
# %%capture

# #chemin définition
# chemin_dossier = path_data_meteo_france_upload_data_depuis_api2
# # Obtenir la liste des df_concantés, clean et sauvegardés
# noms_df=concatener_dataframes_station(df_stations_between_dates_complet, chemin_dossier)


# %%


# %% [markdown]
# ### Charge et renomme les colonnes des datasets déja nettoyés

# %%
# # %%capture captchargerenomme
# from sauve_charge_df_csv_json_pkl import charger_all_dataframes
# from descriptif_dataset_meteo_france import expliquer_et_renommer_colonne
# # dossier = r"..\Datasets\saved_dataframe3"
# # utilisation de la methode externe pour cahrger tous les df d'un dossier
# dossier = r"..\..\Datasets\meteo_france\upload_dataset_depuis_api2\sauve_df"
# # # Chargez les DataFrames en utilisant la fonction
# dataframes = charger_all_dataframes(dossier, default_format="csv", sep=",")
# print(list(dataframes.keys()))

# # Parcourez chaque DataFrame pour renommer les colonnes
# for df_name, df_object in dataframes.items():
#     # Assurez-vous que la fonction expliquer_et_renommer_colonne() retourne bien un tuple avec le nouveau nom en seconde position
#     colonnes_renommees = {col: expliquer_et_renommer_colonne(col)[1] for col in df_object.columns}
#     logger.debug(f" df_name: {df_name}  colonnes_renommees:{colonnes_renommees}")
#     df_renomme = df_object.rename(columns=colonnes_renommees)

#     # Assignez le DataFrame renommé à la variable globale correspondante
#     globals()[df_name] = df_renomme

#     # Affichez les premières lignes du DataFrame renommé pour vérification
#     print(f"{df_name} après renommage:")
#     print(df_renomme.head(2))

# # Affichez la liste des noms de DataFrame pour vérification
# print("Liste des DataFrames chargés et renommés :")
# print(list(dataframes.keys()))


# %%
# %%capture capturechargeglobale

import pandas as pd
import logging
import os
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe
from sauve_charge_df_csv_json_pkl import format_and_save_dataframe
from descriptif_dataset_meteo_france import expliquer_et_renommer_colonne

logger = logging.getLogger("colorlog_example")

# Initialisation du dictionnaire global pour stocker les DataFrames
global_df_dict = {}


# Fonction pour charger et rendre accessible globalement chaque DataFrame
def charge_format_rename_convert_df_globalement(chemin_dossier_df, chemin_liste_df_clean, chemin_sauvagarde_df_col_renamed):

    #charge la liste des df cleaned
    # chargement
    # df_liste_df_clean = load_dataframe("df_liste_df_clean", chemin_liste_df_clean,format_type='pkl')
    noms_df = pd.read_csv(os.path.join(chemin_liste_df_clean, "df_liste_df_clean.csv"), header=0, names=['Nom_df'])
    # noms_df = load_dataframe("df_liste_df_clean", chemin_liste_df_clean, format_type='csv', sep=",")

    noms_df = pd.DataFrame(noms_df)
    logger.debug(f" noms_df :{noms_df.head(2)}")
    # noms_df.columns.tolist()
    # renomme la colonne
    # noms_df.rename(columns={0: 'Nom_df'}, inplace=True)
    logger.info(f" df_liste_df_clean :{noms_df}")

    for index, row in noms_df.iterrows():
        nom_df = row['Nom_df']
        chemin_complet = os.path.join(chemin_dossier_df, f"{nom_df}.csv")

        try:
            # Charger le DataFrame à partir du fichier CSV
            df = pd.read_csv(chemin_complet)
            # Renommer les colonnes du DataFrame en utilisant la fonction importée
            colonnes_renommees = {col: expliquer_et_renommer_colonne(col)[1] for col in df.columns}
            df_renomme = df.rename(columns=colonnes_renommees)
            # Stocker le DataFrame dans le dictionnaire global
            # global_df_dict[nom_df] = df

            logger.debug(f" liste colonne df {df.columns.tolist()} ")
            logger.debug(f" liste colonne df_renomme {df_renomme.columns.tolist()} ")
            logger.debug(f"{nom_df} chargé et ajouté au dictionnaire global.")
            # Stocker le DataFrame dans le dictionnaire global
            global_df_dict[nom_df] = df_renomme
            #sauvegarde des df renommés dans le repertoire sauve_df_col_renamed
            format_and_save_dataframe(df_renomme, nom_df.replace("df_", ""), chemin_sauvagarde_df_col_renamed)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {nom_df}: {e}")
# df_13001009_01jan2014_01mar2024
# df_13004003_01jan2014_01mar2024
# df_13005003_01jan2014_01mar2024
# df_13022003_01jan2014_01mar2024
# df_13036003_01jan2014_01mar2024
# df_13047001_01jan2014_01mar2024
# df_13055029_01jan2014_01mar2024
# df_13056002_01jan2014_01mar2024
# df_13091002_01jan2014_01mar2024
# df_13103001_01jan2014_01mar2024
# df_13108004_01jan2014_01mar2024
# df_13110003_01jan2014_01mar2024


# %%



# %%
# Appel de la fonction
chemin_dossier = path_data_meteo_france_upload_data_depuis_api2
#chemin de stockage de la liste des df cleaned noms_df
chemin_dossier_sauve_liste_df_clean = os.path.join(chemin_dossier, "sauve_liste_df_clean")
#chemin de stockage des df cleaned
chemin_dossier_sauve_df = os.path.join(chemin_dossier, "sauve_df")
chemin_dossier_sauve_df_col_renamed = os.path.join(chemin_dossier, "sauve_df_col_renamed")

# lancement fonction
# dataframes = charge_format_rename_convert_df_globalement(chemin_dossier_sauve_df, chemin_dossier_sauve_liste_df_clean, chemin_dossier_sauve_df_col_renamed)



# # ['df_13001009_01jan2014_01mar2024', 'df_13004003_01jan2014_01mar2024', 'df_13005003_01jan2014_01mar2024', 'df_13022003_01jan2014_01mar2024', 'df_13036003_01jan2014_01mar2024', 'df_13047001_01jan2014_01mar2024', 'df_13055029_01jan2014_01mar2024', 'df_13056002_01jan2014_01mar2024', 'df_13091002_01jan2014_01mar2024', 'df_13103001_01jan2014_01mar2024', 'df_13108004_01jan2014_01mar2024', 'df_13110003_01jan2014_01mar2024']


# %%
### Chargement des df formatés et renommés
df = pd.read_csv(os.path.join(chemin_dossier_sauve_df_col_renamed, "df_13056002_01jan2014_01mar2024.csv"), sep=",")
nom_fichier = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api2\13056002\horaire\13056002_01-Jan-2006_at_00h00_to_31-Dec-2006_at_23h59\13056002_01-Jan-2006_at_00h00_to_31-Dec-2006_at_23h59_1.csv'
df2=pd.read_csv(nom_fichier,header=0, sep=';', encoding='utf-8')
df2

nom_fichier = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api2\13111002\horaire\13111002_01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59\13111002_01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59_1.csv'
df3=pd.read_csv(nom_fichier,header=0, sep=';', encoding='utf-8' )
df3



# %%




# %%
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe

# df_13005003_01jan2014_01mar2024 = load_dataframe('df_13005003_01jan2014_01mar2024', chemin_dossier_sauve_df_col_renamed, format_type='csv', sep=",")
# df_13005003_01jan2014_01mar2024
# chargement station de cap couronnes
df_13056002_01jan2014_01mar2024 = load_dataframe('df_13056002_01jan2014_01mar2024', chemin_dossier_sauve_df_col_renamed, format_type='json', sep=",")
# load_dataframe(df_name, path, format_type='csv', sep=",")
# df_13001009_01jan2014_01mar2024 = global_df_dict['df_13001009_01jan2014_01mar2024']
df_13056002_01jan2014_01mar2024


# %%
from sauve_charge_df_csv_json_pkl import charger_all_dataframes
from descriptif_dataset_meteo_france import expliquer_et_renommer_colonne
# dossier = r"..\Datasets\saved_dataframe3"
# utilisation de la methode externe pour cahrger tous les df d'un dossier
# dossier = r"..\..\Datasets\meteo_france\upload_dataset_depuis_api2\sauve_df"
# dataframes = charger_all_dataframes(dossier, default_format='csv', sep=",")

# dataframes = charger_all_dataframes(chemin_dossier_sauve_df_col_renamed, default_format='csv', sep=",")

for df_name, df_object in global_df_dict.items():
    logger.debug(f" df_name: {df_name}  df_object:{df_object}")
    df_object.head(2)
    globals()[df_name] = df_object

    logger.debug(f"{df_name} est maintenant accessible comme une variable globale.")



# %%
# nom_du_df = 'df_13022003_01jan2014_01mar2024'
nom_du_df = 'df_13001009_01jan2014_01mar2024'
nom_du_df = 'df_13110003_01jan2014_01mar2024'
nom_du_df = 'df_13005003_01jan2014_01mar2024'


# %%
# #charge les df contenu dans la liste
# #chemin de stockage des df cleaned
# chemin_dossier_sauve_df = os.path.join(chemin_dossier, "sauve_df")

# df = load_dataframe("liste_df_clean", chemin_dossier_sauve_df, format_type='pkl')

# Supposons que df_13001009 soit le nom du DataFrame que vous souhaitez inspecter
nom_df = noms_df[0]  # 'df_13001009_01jan2014-01mar2024'

# Accéder au DataFrame depuis global_df_dict en utilisant le nom
df = global_df_dict.get(nom_df)
nom_df=noms_df[0]
if df is not None:
    # Maintenant que vous avez le DataFrame, vous pouvez utiliser .info() pour afficher ses informations
    print(df.head(2))
else:
    print(f"Le DataFrame nommé {nom_df} n'a pas été trouvé.")

# print(noms_df)
# # ['df_13001009_01jan2014-01mar2024', 'df_13004003_01jan2014-01mar2024', 'df_13005003_01jan2014-01mar2024', 'df_13022003_01jan2014-01mar2024', 'df_13036003_01jan2014-01mar2024', 'df_13047001_01jan2014-01mar2024', 'df_13055029_01jan2014-01mar2024', 'df_13056002_01jan2014-01mar2024', 'df_13091002_01jan2014-01mar2024', 'df_13103001_01jan2014-01mar2024', 'df_13108004_01jan2014-01mar2024', 'df_13110003_01jan2014-01mar2024']


# %%
# df


# %% [markdown]
# ### Parcourir les sous-répertoires et évaluer les stations dont l'historique est complet, en ne conservant que les stations qui ont 20 ans d'historique

# %%
import os

def selectionner_stations_avec_20_csv(chemin,taille_histo=19):
    """
    Sélectionne uniquement les dossiers parent "horaire" contenant exactement 20 fichiers CSV.
    Le dictionnaire retourné inclut le nom des fichiers CSV et un compteur de fichiers.

    Args:
        chemin (str): Chemin du dossier racine à parcourir.

    Returns:
        dict: Dictionnaire avec le nom du dossier parent, le nombre de fichiers CSV et leurs noms.
    """
    stations_avec_20_csv = {}
    for root, dirs, files in os.walk(chemin):
        if 'horaire' in dirs:
            chemin_horaire = os.path.join(root, 'horaire')
            nom_parent = os.path.basename(root)
            fichiers_csv = []
            try:
                for sous_dossier in next(os.walk(chemin_horaire))[1]:
                    chemin_sous_dossier = os.path.join(chemin_horaire, sous_dossier)
                    fichiers_csv += [f for f in os.listdir(chemin_sous_dossier) if f.endswith('.csv')]
                # Ajouter seulement si le nombre de fichiers CSV est égal à 20
                if len(fichiers_csv) >= taille_histo:
                    stations_avec_20_csv[nom_parent] = {
                        'compteur': len(fichiers_csv),
                        'fichiers': fichiers_csv
                    }
            except Exception as e:
                print(f"Erreur lors de l'accès à {chemin_horaire}: {e}")
    return stations_avec_20_csv


# Utilisation de la fonction
# resultat = selectionner_stations_avec_20_csv(chemin_dossier)
# for station, infos in resultat.items():
#     print(f"Station: {station}, Nombre de fichiers: {infos['compteur']}")
#     for fichier in infos['fichiers']:
#         print(f"  {fichier}")
#     print("\n")



# %%
# import os
# import pandas as pd
# logger=logging.getLogger('colorlog_example')


# def charger_dataframes(chemin_base, taille_histo=19):
#     """
#     Charge les dataframes à partir des fichiers CSV dans les dossiers spécifiés
#     et les stocke dans un dictionnaire avec un nom spécifique basé sur la station et l'année,
#     tout en enregistrant des informations de débogage.

#     Args:
#         chemin_base (str): Le chemin de base où les fichiers CSV sont stockés.
#         taille_histo(int): permet de selectionner les stations possédant un historique complet sur un certain nombre d'années

#     Returns:
#         dict: Un dictionnaire contenant les DataFrames chargés.
#     """
#     stations_avec_20_csv = selectionner_stations_avec_20_csv(chemin_base, taille_histo)
#     dataframes = {}

#     for station, infos in stations_avec_20_csv.items():
#         if infos[
#                 'compteur'] >= taille_histo:  #selectionne uniquement les stations dont l'historique est complet sur par ex au moins 19 ans
#             logger.debug(
#                 f"Traitement de la station {station} avec {infos['compteur']} fichiers."
#             )
#             for fichier_csv in infos['fichiers']:
#                 nom_fichier_sans_extension = fichier_csv.rsplit('.', 1)[0]
#                 annee = nom_fichier_sans_extension.split('-')[2].split('_')[0]
#                 nom_dataframe = f"df_meteo_france_{station}_{annee}"
#                 # Construction du chemin
#                 chemin_dossier = os.path.join(chemin_base, station, "horaire",
#                                               nom_fichier_sans_extension)
#                 # Séparer le nom du fichier par les underscores et retirer le dernier élément
#                 parts = chemin_dossier.rsplit('_', 1)
#                 chemin_dossier = parts[0] if len(parts) > 1 else chemin_dossier
#                 # Remplacer les séparateurs de chemin par '/'
#                 chemin_fichier_complet = os.path.join(chemin_dossier,
#                                                       fichier_csv).replace(
#                                                           '\\', '/')

#                 # if not os.path.isfile(chemin_fichier_complet):
#                 #     logger.debug(f"Le fichier {chemin_fichier_complet} n'existe pas.")
#                 #     continue

#                 logger.debug(
#                     f"Chargement du fichier {chemin_fichier_complet}.")
#                 dataframe = pd.read_csv(chemin_fichier_complet, sep=";")
#                 globals()[nom_dataframe] = dataframe
#                 dataframes[nom_dataframe] = dataframe
#                 logger.debug(f"DataFrame {nom_dataframe} chargé avec succès.")

#     return dataframes

# # Exemple d'utilisation de la fonction
# base_path = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api'
# base_path=base_path.replace("\\", "/")
# dataframes_charges = charger_dataframes(base_path)

# # Afficher le résultat
# print("DataFrames chargés :")
# for nom_df in dataframes_charges:
#     print(f" df:{nom_df}")
# # C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api\13036003\horaire\01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59\01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59_1.csv
# # C:/programmation/IA/Projet_Meteo/projet_meteo/Projet_Meteo/Datasets/meteo_france/upload_dataset_depuis_api/13005003/horaire/01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59/01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59_1.csv.
# # C:/programmation/IA/Projet_Meteo/projet_meteo/Projet_Meteo/Datasets/meteo_france/upload_dataset_depuis_api/13036003/horaire/01-Jan-2011_at_00h00_to_31-Dec-2011_at_23h59/01-Jan-2011_at_00h00_to_31-Dec-2011_at_23h59_1.csv.


# %%
# chemin_dossier = path_data_meteo_france_upload_data_depuis_api2


# %% [markdown]
# ### Chargement dataset Meteo France au pas de 6 min donné par météo france données brutes

# %%
# df_meteo_france_T92438_2021=pd.read_csv("C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\DATA-20240208T162707Z-001\DATA\METEO_FRANCE\T92438_2021.txt", header=None, sep=" ")
# df_meteo_france_T92438_2021


# %%
# # df_meteo_france_13009 = load_dataframe("01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59_1",path_data_meteo_france_upload_data_depuis_api, format_type='csv', sep=";")
# filepath = r"C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api\13001009\horaire\01-Jan-2017_at_00h00_to_31-Dec-2017_at_23h59\01-Jan-2017_at_00h00_to_31-Dec-2017_at_23h59_1.csv"
# path_data_mobilis_upload_data_depuis_api=r"meteo_france\upload_dataset_depuis_api\13001009\horaire\01-Jan-2017_at_00h00_to_31-Dec-2017_at_23h59"
# filepath=filepath.replace("\\","/")
# path_data_mobilis_upload_data_depuis_api=path_data_mobilis_upload_data_depuis_api.replace("\\","/")
# # df_meteo_france_13009 = pd.read_csv(filepath, sep=";")
# # df_meteo_france_13009 = pd.read_csv(filepath, sep=";")
# df_meteo_france_13009 = load_dataframe("01-Jan-2017_at_00h00_to_31-Dec-2017_at_23h59_1", path_data_mobilis_upload_data_depuis_api,
#                                    format_type='csv', sep=";")
# df_meteo_france_13009.info()


# %%
# %%capture captchargedataframes
# dataframes_charges = charger_dataframes(base_path)
dataframes_charges_filtered={}

for nom_df in dataframes_charges:
    logger.debug(f"Traitement du DataFrame {nom_df}")
    df_actuel = dataframes_charges[
        nom_df]  # Accéder à l'objet DataFrame à partir du dictionnaire
    logger.debug(f"df_actuel {df_actuel}")
    df_filtered = remove_columns_with_na( df_actuel, threshold=0.4)  # Appliquer la fonction de filtrage
    globals()[nom_df] = df_filtered
    dataframes_charges_filtered[nom_df] = df_filtered  # Stocker le résultat filtré

dataframes_charges_filtered


# %%
df.info()


# %% [markdown]
# ## Traitement des datasets fournis par méteo France au pas de  6 min

# %% [markdown]
# ### suppresssion des colonnes vides
#
# pour meteo france ces colonnes contiennent uniquemment des 00000 ou des 999999, on ne supprime que les colonnes contenant 100% de veleurs nulles

# %%
import pandas as pd
import logging
import os
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe, save_dataframe

logger = logging.getLogger("colorlog_example")


def supprimer_colonnes_vides_et_sauvegarder(chemin_des_fichiers_source, chemin_sauvegarde):
    """
    Vérifier et supprimer les colonnes de chaque DataFrame dans un dictionnaire qui ont 100% des cellules
    vides ou égales à 999999 et sauvegarder les DataFrames nettoyés.

    Args:
        dataframes (dict): Dictionnaire de DataFrames à vérifier.
        chemin_sauvegarde (str): Chemin de base pour la sauvegarde des fichiers nettoyés.

    Returns:
        dict: Dictionnaire des DataFrames nettoyés.
    """
    dataframes_without_colonnes_vides = {}
    dataframes = {}

    dataframes = charger_all_dataframes(chemin_des_fichiers_source, default_format="txt", sep=" ")

    for df_name, df in dataframes.items():
        logger.info(f"Traitement du DataFrame: {df_name}")
        colonnes_a_supprimer = [col for col in df.columns if (df[col].isnull().all() or (df[col] == 999999).all())]

        # Supprimer les colonnes identifiées
        if colonnes_a_supprimer:
            logger.info(f"Suppression des colonnes suivantes dans '{df_name}': {colonnes_a_supprimer}")
            df.drop(columns=colonnes_a_supprimer, inplace=True)
            logger.info(f"Les colonnes ont été supprimées dans le DataFrame '{df_name}'")
        else:
            logger.info(f"Aucune colonne à supprimer dans le DataFrame '{df_name}'")
        df_name = df_name.replace('df_', '')
        logger.warning(f"\n df_name:\n{df_name} ")
        # Sauvegarder le DataFrame nettoyé
        # fichier_sauvegarde = os.path.join(chemin_sauvegarde, f"{df_name}_clean.csv")
        df_clean = save_dataframe(df, df_name, chemin_sauvegarde)
        # df_clean=save_dataframe(df, df_name, chemin_sauvegarde)
        # df.to_csv(fichier_sauvegarde, index=False)
        # logger.info(f"DataFrame '{df_name}' sauvegardé en tant que: {fichier_sauvegarde}")
        logger.info(f"DataFrame '{df_name}' sauvegardé ")

        # Ajouter le DataFrame nettoyé au dictionnaire
        dataframes_without_colonnes_vides[df_name] = df_clean

    return dataframes_without_colonnes_vides


#['df_station_13005003', 'df_station_13022003', 'df_station_13028004', 'df_station_13030001', 'df_station_13031002', 'df_station_13036003', 'df_station_13047001', 'df_station_13054001', 'df_station_13055001', 'df_station_13055029', 'df_station_13056002', 'df_station_13062002', 'df_station_13074003', 'df_station_13091002', 'df_station_13092001', 'df_station_13103001', 'df_station_13108004', 'df_station_13110003', 'df_station_13111002']


# %%
# chemin du dossier contenant les fichiers donnés par meteo france au pas de 6 min sources .txt
path_datasets_fourni_par_meteo_france_6min_source
logger.info(f"\n path_datasets_fourni_par_meteo_france_6min_source:\n{path_datasets_fourni_par_meteo_france_6min_source} ")
# chemin de sauvegarde des fichiers onnés par meteo france au pas de 6 min traités, renommage des colonnes, conversion, suppression des colonnes vides
path_sauvegarde_datasets_meteo_france_6min_clean
logger.info(f"\n path_sauvegarde_datasets_meteo_france_6min_clean:\n{path_sauvegarde_datasets_meteo_france_6min_clean} ")


# %%

# dataframes_without_colonnes_vides = supprimer_colonnes_vides_et_sauvegarder(path_datasets_fourni_par_meteo_france_6min_source,
                                                                            # path_sauvegarde_datasets_meteo_france_6min_clean)


# %% [markdown]
# ### formatage, conversion , renommage des colonnes
#
# nommage des colonnes en francais, conversion dse unités,

# %%
#debugage
# %debug
# import pdb
# pdb.set_trace()

import pandas as pd
import logging
import os
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe
from sauve_charge_df_csv_json_pkl import format_and_save_dataframe
from descriptif_dataset_meteo_france import renommer_colonne_df_meteo_france_6min

logger = logging.getLogger("colorlog_example")



def traiter_et_renommer_dataset(chemin_des_fichiers_source,  chemin_sauvegarde):
    """
    Lit un dataset de Météo France depuis un fichier .txt et renomme ses colonnes.
    """
    dataframes={}
    dataframes_formated={}

    dataframes=charger_all_dataframes(chemin_des_fichiers_source, default_format="csv", sep=",")
    # logger.debug(f"\n dataframes:\n{dataframes} ")
    # # Lecture du fichier .txt
    # df = pd.read_csv(fichier, sep=' ', header=None)
    for df_name, df in dataframes.items():
        # Renommage des colonnes
        logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
        logger.debug(f"\n df_name:\n{df_name} ")
        logger.debug(f"\n nombre de colonnes:\n{len(df.columns)} ")

        #compte le nombre de colonne du df car le renommage en dépend, en particulier pour la colonne direction
        nombre_colonne_df=len(df.columns)
        # le nom de la station est necessaire pour traiter la station 13054001 dont les colonnes ne sont pas comme les autres stations
        nom_station = df.iloc[0, 0]
        logger.debug(f"\n nombre_colonne_df:\n{nombre_colonne_df} ")
        # Renommage des colonnes
        df.columns = [renommer_colonne_df_meteo_france_6min(f'col{i}',nom_station, nombre_colonne_df) for i in range(len(df.columns))]

        logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
        logger.debug(f"\n liste colonnes:\n{df.head(2)} ")

        # Formate convertie et sauve les datasets
        logger.info(f" sauvegarde des datasets ")
        df_name = df_name.replace('df_', '')
        df=format_and_save_dataframe(df, df_name, chemin_sauvegarde)
        # Ajouter le DataFrame chargé au dictionnaire
        dataframes_formated[df_name] = df
        logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
        logger.debug(f"\n nombre de colonnes:\n{len(df.columns)} ")

    logger.debug(f"\n dataframes:\n{dataframes_formated} ")
    return dataframes_formated


# %%
# # chemin du dossier contenant les fichiers donnés par meteo france au pas de 6 min sources .txt
# path_datasets_fourni_par_meteo_france_6min_source
# logger.info(f"\n path_datasets_fourni_par_meteo_france_6min_source:\n{path_datasets_fourni_par_meteo_france_6min_source} ")

# chemin de sauvegarde des fichiers onnés par meteo france au pas de 6 min traités, renommage des colonnes, conversion, suppression des colonnes vides
path_sauvegarde_datasets_meteo_france_6min_clean
logger.info(f"\n path_sauvegarde_datasets_meteo_france_6min_clean:\n{path_sauvegarde_datasets_meteo_france_6min_clean} ")

# chemin de sauvegarde des fichiers onnés par meteo france au pas de 6 min traités,suppression des colonnes vides
path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide
logger.info(f"\n path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide:\n{path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide} ")


# %%
#test de la fonction
# dataframes_formated = traiter_et_renommer_dataset(path_sauvegarde_datasets_meteo_france_6min_clean, path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide)
# dataframes_formated


# %% [markdown]
# ## Chargement des dataset meteo france au pas de 6 min

# %%
import pandas as pd
import logging
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe

logger = logging.getLogger("colorlog_example")

# chemin de sauvegarde des fichiers onnés par meteo france au pas de 6 min traités,suppression des colonnes vides
path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide
logger.info(f"\n path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide:\n{path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide} ")


# # chemin de sauvegarde des fichiers onnés par meteo france au pas de 6 min traités, renommage des colonnes, conversion, suppression des colonnes vides
# path_sauvegarde_datasets_meteo_france_6min_clean
# logger.info(f"\n path_sauvegarde_datasets_meteo_france_6min_clean:\n{path_sauvegarde_datasets_meteo_france_6min_clean} ")
dataframes={}
dataframes = charger_all_dataframes(path_sauvegarde_datasets_meteo_france_6min_suppression_col_vide, default_format="csv", sep=",")


# %%
# df=dataframes['df_station_13092001']
# df = dataframes['df_station_13054001']
# df = dataframes['df_station_13092001']

df_station_13054001 = dataframes["df_station_13054001"]
df_station_13054001


#obtenir le nom de la station
# df_station_13054001["station"].loc[0]
# df_station_13054001.iloc[0,0].dtype


# %% [markdown]
# ### Test rapide sur les dataframes contenant un certain pourcentage de colonnes contenant des valeurs nulles ou égales à 99999

# %%
# test avec un pourcentage de 2 %
pourcentage_filtre=2
pourcentage_filtre=pourcentage_filtre/100
# # Parcourir chaque DataFrame dans le dictionnaire
for df_name, df in dataframes.items():
    # colonnes_a_supprimer = [col for col in df.columns if (df[col].isnull().sum() / len(df) > 10 or (df[col] == 999999).sum() / len(df) > 10)]
    colonnes_avec_40_pourcent_de_nul = [col for col in df.columns if (df[col].isnull().sum() / len(df) > pourcentage_filtre) or (df[col] == 999999).sum() / len(df) > pourcentage_filtre]

    if colonnes_avec_40_pourcent_de_nul:
        logger.critical(f"Le DataFrame '{df_name}' contient plus de {pourcentage_filtre*100}%. \n Nom des colonnes: {colonnes_avec_40_pourcent_de_nul}")
    else:
        logger.info(f"Le DataFrame '{df_name}' ne contient pas plus de {pourcentage_filtre*100}%. \n Nom des colonnes: {colonnes_avec_40_pourcent_de_nul}")


# %% [markdown]
# # WINDSUP
#
# attention il faut supprimer le ; de fin de ligne du dataset car il produit des décalages de colonne
#
# Station Id;Date Timestamp [UTC];Date Txt [UTC]; Average Wind Speed [nds];Min Wind Speed [nds];Max Wind Speed [nds];Wind Direction [degree];Wind Direction [txt]
#
# 44;1210558680;2008-05-12 04:18;2;1;3;180;S ***;***

# %%
# import pandas as pd
# import logging
# import os
# from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe
# from sauve_charge_df_csv_json_pkl import format_and_save_dataframe
# from descriptif_dataset_meteo_france import expliquer_et_renommer_colonne

# logger = logging.getLogger("colorlog_example")


# # # Création d'un dictionnaire pour le renommage
# # colonnes_renommees = {}



# def traitement_windsup(nom_fichier_original, nom_fichier_modifie, chemin_sauvegarde_df_windsup_preprocessed):
#     # SUPPRESSION DU ; DE FIN DE LIGNE
#     # Ouvrir le fichier original en mode lecture et le fichier modifié en mode écriture
#     with open(nom_fichier_original, 'r', encoding='utf-8') as fichier_original, open(nom_fichier_modifie, 'w', encoding='utf-8') as fichier_modifie:
#         for ligne in fichier_original:
#             # Enlever le dernier point-virgule de la ligne (s'il existe) et écrire la ligne modifiée dans le nouveau fichier
#             fichier_modifie.write(ligne.rstrip(';\n') + '\n')

#     #CHARGEMENT FICHIER

#     df_windsup = pd.read_csv(nom_fichier_modifie, header=0, sep=';', encoding='utf-8')
#     df=df_windsup.copy()
#     # Station Id;Date Timestamp [UTC];Date Txt [UTC]; Average Wind Speed [nds];Min Wind Speed [nds];Max Wind Speed [nds];Wind Direction [degree];Wind Direction [txt]
#     logger.debug(f"\n liste colonnes:\n{df_windsup.columns.tolist()} ")

#     # SUPPRESSION DES COLONNES
#     # Supprimer les colonnes spécifiques si elles existent
#     colonnes_a_supprimer = ['Date Txt [UTC]', 'Wind Direction [txt]']
#     for col in colonnes_a_supprimer:
#         if col in df.columns:
#             df.drop(columns=[col], inplace=True)
#             logger.debug(f"\nSuppression de la colonne : {col}")

#     # RENOMMAGE DES COLONNES
#     # Création d'un dictionnaire pour le renommage
#     colonnes_renommees = {}
#     for col in df.columns:
#         try:
#             # Renommer les colonnes du DataFrame en utilisant la fonction importée
#             # Utilisation de la deuxième partie du tuple retourné par `expliquer_et_renommer_colonne` pour le renommage
#             _, nouveau_nom = expliquer_et_renommer_colonne(col)
#             colonnes_renommees[col] = nouveau_nom

#         except Exception as e:
#             logger.error(f"Erreur lors du chargement de {df}: {e}")
#     # df_renomme['date'] = pd.to_datetime(df_renomme['date'], format='%Y-%m-%d %H:%M', errors='coerce')
#     df_renomme = df.rename(columns=colonnes_renommees)

#     logger.debug(f" liste colonne df {df.columns.tolist()} ")
#     logger.debug(f" liste colonne df_renomme {df_renomme.columns.tolist()} ")

#     # CONVERSION COLONNE DATE
#     # df_renomme['date'] = pd.to_datetime(df_renomme['date'], format='%Y-%m-%d %H:%M', errors='coerce')
#     # Convertir les timestamps UNIX en objets datetime
#     df_renomme['date'] = pd.to_datetime(df_renomme['date'], unit='s', utc=True)

#     df_renomme['date'] = df_renomme['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

#     # Vérifier si la colonne 'date' existe dans le DataFrame
#     print('date' in df_renomme.columns)

#     # Afficher les premières lignes de la colonne 'date' si elle existe
#     if 'date' in df_renomme.columns:
#         print(df_renomme['date'].head())
#     else:
#         print("La colonne 'date' n'existe pas dans df_renomme.")

#     # SAUVEGARDE
#     format_and_save_dataframe(df_renomme, "windsup_renamed", chemin_sauvegarde_df_windsup_preprocessed)

#     return df_renomme


# %% [markdown]
# ## traitement windsup

# %%
import pandas as pd
import logging
import os
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe
from sauve_charge_df_csv_json_pkl import format_and_save_dataframe
from descriptif_dataset_meteo_france import expliquer_et_renommer_colonne

logger = logging.getLogger("colorlog_example")


def traitement_windsup(nom_fichier_original, nom_fichier_modifie, chemin_sauvegarde_df_windsup_preprocessed):
    """
    Traite un fichier CSV de données windSUP en supprimant le dernier caractère ';',
    supprime certaines colonnes non nécessaires, renomme les colonnes selon un dictionnaire prédéfini,
    et enregistre le nouveau DataFrame dans un chemin spécifié.

    Parameters:
    - nom_fichier_original: Chemin vers le fichier original.
    - nom_fichier_modifie: Chemin vers le fichier temporaire modifié.
    - chemin_sauvegarde_df_windsup_preprocessed: Chemin pour sauvegarder le DataFrame prétraité.

    Returns:
    - DataFrame prétraité et renommé.

    >>> traitement_windsup('data/windsup_original.csv', 'data/windsup_modifie.csv', 'data/preprocessed')
    DataFrame avec les colonnes renommées et nettoyées.
    """
    # Suppression du caractère ';' de fin de ligne
    with open(nom_fichier_original, 'r', encoding='utf-8') as fichier_original, open(nom_fichier_modifie, 'w', encoding='utf-8') as fichier_modifie:
        for ligne in fichier_original:
            fichier_modifie.write(ligne.rstrip(';\n') + '\n')

    # Chargement du fichier après prétraitement
    try:
        df_windsup = pd.read_csv(nom_fichier_modifie, header=0, sep=';', encoding='utf-8')
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier modifié: {e}")
        return None

    df = df_windsup.copy()
    logger.debug(f"\n liste colonnes:\n{df_windsup.columns.tolist()} ")

    # Suppression des colonnes non désirées
    for col in ['Date Txt [UTC]', 'Wind Direction [txt]']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
            logger.debug(f"\nSuppression de la colonne : {col}")

    # Renommage des colonnes
    colonnes_renommees = {}
    for col in df.columns:
        _, nouveau_nom = expliquer_et_renommer_colonne(col)
        colonnes_renommees[col] = nouveau_nom

    df_renomme = df.rename(columns=colonnes_renommees)
    logger.debug(f"\n liste colonne df_renomme {df_renomme.columns.tolist()} ")

    # Conversion de la colonne 'date'
    df_renomme['date'] = pd.to_datetime(df_renomme['date'], unit='s', utc=True)
    df_renomme['date'] = df_renomme['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Vérification de l'existence de la colonne 'date'
    if 'date' in df_renomme.columns:
        logger.debug(df_renomme['date'].head())
    else:
        logger.error("La colonne 'date' n'existe pas dans df_renomme.")

    # Sauvegarde du DataFrame prétraité
    try:
        format_and_save_dataframe(df_renomme, "windsup_renamed", chemin_sauvegarde_df_windsup_preprocessed)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du DataFrame: {e}")

    return df_renomme


# %%
# "traitement_windsup"
nom_fichier = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\data_windsup\Station44-2008-1-1_to_2024-1-12_23_59_59.csv'
chemin_sauvegarde_df_windsup_preprocessed = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\data_windsup\df_preprocessing'

nom_fichier_original = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\data_windsup\Station44-2008-1-1_to_2024-1-12_23_59_59.csv'
nom_fichier_modifie = r'C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\data_windsup\Station44-2008-1-1_to_2024-1-12_23_59_59_modified.csv'


# %%
#lancement fonction
# df_windsup=traitement_windsup(nom_fichier_original, nom_fichier_modifie, chemin_sauvegarde_df_windsup_preprocessed)
# df_windsup


# %% [markdown]
# ## Chargement dataset windsup renommé

# %%
import pandas as pd
import logging

from sauve_charge_df_csv_json_pkl import  load_dataframe

logger = logging.getLogger("colorlog_example")

# chemin_sauvegarde_df_windsup_preprocessed = "df_preprocessing"
# chemin_dossier_windsups_renamed = os.path.join(path_data_windsup_upload_data_depuis_api, chemin_sauvegarde_df_windsup_preprocessed)
# logger.debug(f"\npath_data_windsup_upload_data_depuis_api :\n{path_data_windsup_upload_data_depuis_api} ")
# logger.debug(f"\nchemin_dossier_windsups_renamed :\n{chemin_dossier_windsups_renamed} ")

# path_fichier_windsup_renamed = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=False)
# logger.debug(f"\n nom_element:\n{nom_element} ")
print(f"\n path_fichier_windsup_renamed:\n{path_fichier_windsup_renamed} \n")
print(f"\n path_dossier_windsup_renamed:\n{path_dossier_windsup_renamed} \n")

df_windsup = load_dataframe("df_windsup_renamed", path_dossier_windsup_renamed, format_type='csv', sep=",")
df_windsup


# %% [markdown]
# # Fusion des dataset meteo france / mobilis/ windsup

# %%
# import pandas as pd
# import logging
# import os




# def lire_et_fusionner_datasets(dossier, prefixe_nom_fichier, type_fichier='pkl', chemin_sauve_dataset_fusionne=None,colonnes_requises=None,  nom_station_par_defaut=None):
#     """
#     Lit tous les fichiers CSV dans un dossier et ses sous-dossiers qui correspondent à un préfixe donné,
#     les fusionne en un seul DataFrame, ajoute une colonne 'station' si nécessaire, et sauvegarde le résultat dans un fichier CSV.

#     :param dossier: Chemin vers le dossier contenant les fichiers.
#     :param prefixe_nom_fichier: Préfixe du nom de fichier à chercher par exemple csv
#     :param colonnes_requises: Liste des colonnes à conserver dans le DataFrame fusionné. Si None, toutes les colonnes sont conservées.
#     :param chemin_sauve_dataset_fusionne: Chemin complet pour sauvegarder le DataFrame fusionné en CSV. Si None, pas de sauvegarde.
#     :param nom_station_par_defaut: Nom de la station à utiliser si la colonne 'station' n'est pas présente. Si None, pas d'ajout de colonne.
#     :return: DataFrame fusionné.
#     """
#     dataframes = []
#     dataframes_renommes = []

#     files_processed = 0

#     for root, dirs, files in os.walk(dossier):
#         logger.debug(f"\n liste des fichiers:\n{files} ")

#         for file in files:
#             logger.debug(f"\n root:\n{root} ")
#             logger.debug(f"\n dirs:\n{dirs} ")
#             logger.debug(f"\n file:\n{file} ")
#             logger.debug(f"\n prefixe_nom_fichier:\n{prefixe_nom_fichier} ")

#             if file.startswith(prefixe_nom_fichier) and file.endswith(type_fichier):
#                 # if  file.endswith('.csv'):
#                 filepath = os.path.join(root, file)
#                 logger.debug(f"\n filepath car se termine par .csv:\n{filepath} ")
#                 try:
#                     if type_fichier== "csv":
#                         df = pd.read_csv(filepath, sep=',', encoding='utf-8', parse_dates=['date'], dayfirst=True)
#                         logger.info(f"DataFrame loaded from CSV at {filepath}")
#                     if type_fichier== "json":
#                         df = pd.read_json(filepath, orient='split')
#                         logger.info(f"DataFrame loaded from json at {filepath}")
#                     if type_fichier== "pkl":
#                         df = pd.read_pickle(filepath)
#                         logger.info(f"DataFrame loaded from pickle at {filepath}")

#                     logger.debug(f"\n df:\n{df.head(2)} ")
#                     files_processed += 1
#                     logger.info(f"Fichier chargé: {filepath}")

#                     # Ajouter une colonne 'station' si nécessaire
#                     if 'station' not in df.columns and nom_station_par_defaut is not None:
#                         df['station'] = nom_station_par_defaut
#                         logger.debug(f"\n nom_station_par_defaut:\n{nom_station_par_defaut} ")

#                     # Filtrer les colonnes si nécessaire
#                     if colonnes_requises is not None:
#                         colonnes_disponibles = [col for col in colonnes_requises if col in df.columns]
#                         df = df[colonnes_disponibles]
#                         logger.debug(f"\n colonnes_disponibles:\n{colonnes_disponibles} ")

#                     dataframes.append(df)
#                     logger.debug(f"\n dataframes :\n{dataframes} ")
#                 except Exception as e:
#                     logger.error(f"Erreur lors de la lecture du fichier {filepath}: {e}")

#     # Vérifier si la liste des DataFrames est vide
#     if not dataframes:
#         logger.error("Aucun DataFrame à fusionner. Vérifiez le dossier et le préfixe des noms de fichier.")
#         return pd.DataFrame()  # Retourner un DataFrame vide pour éviter l'erreur

#     # Concaténer les DataFrames
#     # df_fusionne = pd.concat(dataframes, ignore_index=True)
#     # logger.debug(f"\n df_fusionne:\n{df_fusionne.head(2)} ")
#     # logger.info("DataFrames fusionnés avec succès.")


#     try:
#         # Réinitialiser les index des DataFrames et vérifier les noms de colonnes ici si nécessaire
#         dataframes = [df.reset_index(drop=True) for df in dataframes]
#         for df in dataframes:
#             # Extraire le nom de la station à partir de la première ligne de la colonne 'station'
#             nom_station = df.loc[df.index[0], 'station']
#             # Définir la colonne 'date' comme index
#             df = df.set_index('date')
#             # Renommer les colonnes, sauf 'station' et 'date'
#             df = df.rename(columns={col: f"{col}_{nom_station}" if col not in ['station', 'date'] else col for col in df.columns})
#             dataframes_renommes.append(df)
#             logger.debug(f"\n dataframes_renommes:\n{dataframes_renommes} ")

#         dataframes_renommes_ajustes = []
#         # Créer un index complet qui couvre toutes les dates présentes dans tous les DataFrames
#         dates_completes = pd.date_range(start='2014-01-01', end='2024-03-01', freq='h')
#         # test de l'unicité des index
#         # Réindexer chaque DataFrame pour utiliser cet index complet
#         dataframes_renommes = [df.reindex(dates_completes) for df in dataframes_renommes]
#         for df in dataframes_renommes:
#             logger.warning(df.index.is_unique)
#             # Supprimer les index dupliqués, en ne gardant que la première occurrence
#             df = df.loc[~df.index.duplicated(keep='first')]
#             # Ajouter le DataFrame ajusté à la nouvelle liste
#             dataframes_renommes_ajustes.append(df.reindex(dates_completes))


#         # Concaténer les DataFrames
#         # df_fusionne = pd.concat(dataframes_renommes, ignore_index=True)
#         # concat suivant la colonne avec axis=1
#         df_fusionne = pd.concat(dataframes_renommes_ajustes, axis=1)
#         logger.debug(f"\n df_fusionne:\n{df_fusionne.head(2)} ")
#         logger.info("DataFrames fusionnés avec succès.")

#         # Suite du traitement...
#     except Exception as e:
#         logger.error("Erreur lors de la concaténation des DataFrames", exc_info=True)
#         df_fusionne = pd.DataFrame()



#     # Sauvegarder le DataFrame fusionné
#     if chemin_sauve_dataset_fusionne is not None and not df_fusionne.empty:
#         df_fusionne.to_csv(chemin_sauve_dataset_fusionne, index=False, sep=',', encoding='utf-8')
#         logger.info(f"Le dataset fusionné a été sauvegardé dans : {chemin_sauve_dataset_fusionne}")
#     logger.debug(f"\nfiles_processed :\n{files_processed} ")

#     return df_fusionne


# %%
import pandas as pd
import logging
import os

# Configuration initiale du logger
logger = logging.getLogger("colorlog_example")


def lire_et_fusionner_datasets(dossier,
                               prefixe_nom_fichier,
                               type_fichier='pkl',
                               chemin_sauve_dataset_fusionne=None,
                               colonnes_requises=None,
                               nom_station_par_defaut=None):
    logger.debug(f"Début de la fonction lire_et_fusionner_datasets avec le dossier {dossier} et le type de fichier {type_fichier}")
    dataframes_renommes = []

    for root, dirs, files in os.walk(dossier):
        logger.debug(f"Exploration de {root} contenant {len(files)} fichiers")
        for file in files:
            logger.debug(f"Traitement du fichier {file}")
            if file.startswith(prefixe_nom_fichier) and file.endswith(type_fichier):
                filepath = os.path.join(root, file)
                logger.debug(f"Chargement du fichier {filepath}")
                try:
                    if type_fichier == "csv":
                        df = pd.read_csv(filepath, sep=',', encoding='utf-8', parse_dates=['date'], dayfirst=True)
                        logger.debug(f"DataFrame chargé depuis CSV avec {len(df)} lignes")
                    elif type_fichier == "json":
                        df = pd.read_json(filepath, orient='split')
                        logger.debug(f"DataFrame chargé depuis JSON avec {len(df)} lignes")
                    elif type_fichier == "pkl":
                        df = pd.read_pickle(filepath)
                        logger.debug(f"DataFrame chargé depuis pickle avec {len(df)} lignes")

                    if 'station' not in df.columns and nom_station_par_defaut is not None:
                        df['station'] = nom_station_par_defaut
                        logger.debug(f"Ajout de la colonne 'station' avec valeur par défaut {nom_station_par_defaut}")

                    if colonnes_requises is not None:
                        df = df[[col for col in colonnes_requises if col in df.columns]]
                        logger.debug(f"Filtrage des colonnes requises, nouvelle forme {df.shape}")

                    df.set_index('date', inplace=True)
                    nom_station = df['station'].iloc[0] if 'station' in df.columns else nom_station_par_defaut
                    df = df.rename(columns={col: f"{col}_{nom_station}" if col not in ['station', 'date'] else col for col in df.columns})
                    logger.debug(f"Renommage des colonnes avec le suffixe {nom_station}")

                    if 'station' in df.columns:
                        df.drop(columns=['station'], inplace=True)
                        logger.debug("Colonne 'station' supprimée")

                    dataframes_renommes.append(df)
                    logger.warning(f"\n dataframes_renommes:\n{dataframes_renommes} ")
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture du fichier {filepath}: {e}")

    if not dataframes_renommes:
        logger.error("Aucun DataFrame à fusionner. Vérifiez le dossier et le préfixe des noms de fichier.")
        return pd.DataFrame()

    try:
        if dataframes_renommes:
            df_fusionne = dataframes_renommes[0]
            logger.debug(f"Initialisation de df_fusionne pour la fusion  {df_fusionne.head(2)}")
            for df in dataframes_renommes[1:]:
                df_fusionne = pd.merge(df_fusionne, df, left_index=True, right_index=True, how='outer')
                logger.debug(f"Fusion de DataFrame effectuée {df_fusionne.head(2)}")

            if chemin_sauve_dataset_fusionne is not None and not df_fusionne.empty:
                # df_fusionne.to_csv(chemin_sauve_dataset_fusionne, index=True, sep=',', encoding='utf-8')
                df_fusionne.to_pickle(chemin_sauve_dataset_fusionne)
                logger.info(f"Le dataset fusionné a été sauvegardé dans : {chemin_sauve_dataset_fusionne}")
    except Exception as e:
        logger.critical("Erreur lors de la fusion des DataFrames", exc_info=True)
        df_fusionne = pd.DataFrame()

    return df_fusionne, dataframes_renommes


# %%
# chemin de sauvegarde du dataset
# chemin_sauve_dataset_fusionne = 'projet_meteo\Projet_Meteo\Datasets\datasets_fusionned'
path_data_meteo_france_api2_datasets_fusionned
logger.debug(f"\n path_data_meteo_france_api2_datasets_fusionned:\n{path_data_meteo_france_api2_datasets_fusionned} \n")
# chemin windsup
path_fichier_windsup_renamed
path_dossier_windsup_renamed
logger.debug(f"\n path_fichier_windsup_renamed:\n{path_fichier_windsup_renamed} \n")
logger.debug(f"\n path_dossier_windsup_renamed:\n{path_dossier_windsup_renamed} \n")

#chemin meteo france
path_data_meteo_france_upload_data_depuis_api2
# path_data_meteo_france_upload_data_depuis_api2 = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
logger.debug(f"\n path_data_meteo_france_upload_data_depuis_api2:\n{path_data_meteo_france_upload_data_depuis_api2} \n")
path_data_meteo_france_api2_col_renamed
logger.debug(f"\n path_data_meteo_france_api2_col_renamed:\n{path_data_meteo_france_api2_col_renamed} \n")

#chemin mobilis
# path_data_mobilis_upload_data_depuis_api = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
path_data_mobilis_upload_data_depuis_api
logger.debug(f"\n path_data_mobilis_upload_data_depuis_api:\n{path_data_mobilis_upload_data_depuis_api} \n")
# nom station pour le df de mobilis
nom_station_par_defaut = 'planier'  # Pour les fichiers de Mobilis


colonnes_requises=["vent"]


# %%
# Utiliser la fonction pour lire, fusionner, et potentiellement ajouter une colonne 'station' avec 'planier' comme valeur par défaut
# (dossier, prefixe_nom_fichier, type_fichier='pkl', chemin_sauve_dataset_fusionne=None ,colonnes_requises=None,  nom_station_par_defaut=None)

df_meteo_france, dataframes_renommes= lire_et_fusionner_datasets(path_data_meteo_france_api2_col_renamed, 'df_', 'pkl', path_data_meteo_france_api2_datasets_fusionned)

# # Exemple d'utilisation :
# # Assurez-vous de lire vos datasets avec pd.read_csv ou toute autre méthode appropriée avant de les passer à la fonction.
# # Remplacer 'nom_fichier' par le chemin réel vers vos fichiers CSV
# df1 = pd.read_csv('meteofrance1.csv', sep=',', encoding='utf-8')
# df2 = pd.read_csv('meteofrance2.csv', sep=',', encoding='utf-8')
# df3 = pd.read_csv('mobili1.csv', sep=',', encoding='utf-8')
# df4 = pd.read_csv('mobili2.csv', sep=',', encoding='utf-8')
# df5 = pd.read_csv('windups.csv', sep=';', encoding='utf-8')

# # Convertir la colonne 'Date Timestamp [UTC]' en datetime pour windups
# df5['Date Timestamp [UTC]'] = pd.to_datetime(df5['Date Timestamp [UTC]'], unit='s')

# liste_datasets = [df1, df2, df3, df4, df5]
# df_fusionne = fusionner_datasets(liste_datasets)

print(df_meteo_france.head())
dataframes_renommes


# %%
dataframes_renommes
df_meteo_france


# %% [markdown]
# # Graphique

# %% [markdown]
# ## Fonction courbes temperature, vent, rafales, direction

# %%
import pandas as pd
# from gestion_logging import reconfigurer_logging
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import dateparser
from dateparser import parse

logger = logging.getLogger('colorlog_example')


def est_date_valide(date_str):
    """
  Fonction pour valider le format de la date et de l'heure
  """
    try:
        dateparser.parse(date_str)
        return True
    except ValueError:
        return False


def graphiques_plot(df, cols, date_debut, date_fin, pas,method_interpolation="linear", order=None):

    # # Contrôle de saisie du format de la date de fin
    # if not est_date_valide(date_fin):
    #     raise ValueError("Format de la date de fin invalide")
    # elif date_fin == "now()":
    #     date_fin = pd.to_datetime('now')
    df=df.copy()
    logger.debug(f"\n cols[0]:\n{cols[0]}, cols[1]:\n{cols[1]}, cols[2]:\n{cols[2]} ,cols[3]:\n{cols[3]}")
    if 'date' in df.columns :
        # Conversion de la colonne 'date' en format datetime, si ce n'est pas déjà fait
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    else:
        raise KeyError("La colonne 'date' n'existe pas dans le DataFrame.")

    df = df[cols]
    # Conversion des strings date_debut et date_fin en datetime, si ce n'est pas déjà fait
    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin) if date_fin != "now()" else pd.to_datetime('now')

    # # Filtrage des dates en utilisant l'index
    # df_filtered = df.loc[date_debut:date_fin]


    # Assurez-vous que l'index du DataFrame est de type DateTimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("L'index du DataFrame doit être de type DateTimeIndex.")

    # Filtrage du DataFrame basé sur les dates
    flitre_dates = (df.index >= date_debut) & (df.index <= date_fin)
    df_filtered = df.loc[flitre_dates]


    # Conversion de la valeur de pas en type timedelta64[ns] et rééchantillonnage
    pas = pd.to_timedelta(pas)
    df_grouped = df_filtered.resample(pas).mean()

    # Traitement des valueurs manquantes liées au resample
    # Interpolation des valeurs manquantes après le rééchantillonnage
    df_interpolated = df_grouped.interpolate(method=method_interpolation, order=order)
    df_grouped=df_interpolated
    # # Contrôle de saisie du format de la date de début
    # if not est_date_valide(date_debut):
    #     raise ValueError("Format de la date de début invalide")




    # #  filtrage des dates
    # df = df.loc[df['date'] >= date_debut]
    # df = df.loc[df['date'] <= date_fin]

    # # pas='7D'
    # # Regroupement des données par heure et calcul des moyennes
    # df_grouped = df.resample(pas, on='date').mean()

    # Configuration du style de matplotlib pour utiliser un fond sombre
    plt.style.use('classic')

    # Création de trois subplots verticalement
    fig, (ax1, ax22, ax3) = plt.subplots(3, 1, figsize=(10, 15))

    # Graphique de la Température
    ax1.plot(df_grouped.index,
             df_grouped[cols[0]],
             marker='o',
             linestyle='-',
             color='tomato',
             label=cols[0])
    ax1.set_title(f'{cols[0]} Moyenne par Heure')
    ax1.set_xlabel('Date')
    ax1.set_ylabel(cols[0])
    ax1.tick_params(axis='x', rotation=45)
    ax1.legend()

    # # Graphique de la Vitesse du Vent
    # ax2.plot(df_grouped.index, df_grouped['vitesse_(km/h)'], marker='s', linestyle='-', color='royalblue', label='Vitesse du Vent (m/s)')
    # ax2.set_title('Vitesse du Vent Moyenne par Heure')
    # ax2.set_xlabel('Date')
    # ax2.set_ylabel('Vitesse (m/s)')
    # ax2.legend()

    # Graphique des rafales
    ax22.plot(df_grouped.index, df_grouped[cols[1]], marker='.', linestyle='-', color='royalblue', label=cols[1])
    ax22.plot(df_grouped.index, df_grouped[cols[2]], marker='.', linestyle='-', color='seagreen', label=cols[2])
    ax22.set_title(f'{cols[1]} et {cols[2]} Moyenne par Heure')
    ax22.set_xlabel('Date')
    ax22.set_ylabel(cols[2])
    ax22.tick_params(axis='x', rotation=45)
    ax22.legend()

    # Graphique de la Direction du Vent
    ax3.plot(df_grouped.index, df_grouped[cols[3]], marker='^', linestyle='-', color='seagreen', label=cols[3])
    ax3.set_title(f'{cols[3]} Moyenne par Heure')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Direction (degrés)')
    ax3.tick_params(axis='x', rotation=45)
    ax3.legend()

    # Ajustement de l'espacement entre les graphiques pour éviter le chevauchement
    plt.tight_layout()

    # Affichage des graphiques
    plt.show()


# %%
import pandas as pd
# df
# df['date'] = pd.to_datetime(df['date'])
df = df_13005003_01jan2014_01mar2024.copy()
# # Convertir la colonne 'date' en datetime si ce n'est pas déjà fait
# df['date'] = pd.to_datetime(df['date'])
# # Définir la colonne 'date' comme nouvel index du DataFrame
# df.set_index('date', inplace=True)


# %%
df
print(df.columns)


# %%
# %%capture capturegraphique
# df_mobilis3_12col['date']
# df_mobilis3_12col.set_index('date', inplace=False)

df_mobilis3_12col["temperature_(°C)"].plot()
plt.show()


# %% [markdown]
# #### Test des differentes possibilités d'interpoler les valeurs manquantes, visualisation graphique

# %%
def test_toutes_methodes_interpolation(df, col, date_debut, date_fin, pas, liste_methodes_interpolation):
    """
    Teste différentes méthodes d'interpolation sur une colonne spécifique d'un DataFrame entre deux dates.

    Pour chaque méthode d'interpolation fournie, cette fonction génère un graphique pour visualiser
    les résultats de l'interpolation.

    Args:
        df (pd.DataFrame): Le DataFrame sur lequel effectuer l'interpolation.
        col (str): Le nom de la colonne du DataFrame à interpoler.
        date_debut (str): Date de début pour la période d'interpolation (format YYYY-MM-DD).
        date_fin (str): Date de fin pour la période d'interpolation (format YYYY-MM-DD).
        pas (str): Le pas de temps pour l'interpolation (ex: '1D' pour 1 jour ou '0.01D' pour 14.4 minutes ).
        liste_methodes_interpolation (list): Une liste de dictionnaires, chaque dictionnaire contient
                                              'method' pour le nom de la méthode d'interpolation et
                                              'order' (optionnel) pour l'ordre d'interpolation si nécessaire.

    Returns:
        None
    """

    # Itération sur chaque méthode d'interpolation fournie dans la liste
    for method_info in liste_methodes_interpolation:
        logger.info(f"Interpolation en cours avec la méthode : {method_info['method']}")

        # Affichage de la méthode d'interpolation utilisée
        print(f"\nMéthode d'interpolation : {method_info['method']}")

        # Vérification de la présence de l'argument 'order' pour les méthodes qui le nécessitent
        if 'order' in method_info:
            # Appel de la fonction graphiques_plot avec 'order' si spécifié
            graphiques_plot(df, col, date_debut, date_fin, pas, method_interpolation=method_info['method'], order=method_info['order'])
        else:
            # Appel de la fonction graphiques_plot sans 'order'
            graphiques_plot(df, col, date_debut, date_fin, pas, method_interpolation=method_info['method'])



# Convertir la colonne 'date' en datetime si ce n'est pas déjà fait
# df['date'] = pd.to_datetime(df['date'])
# Définir la colonne 'date' comme nouvel index du DataFrame
# df.set_index('date', inplace=True)
# Choix colonne

col =[ 'temperature_sol_(°C)', "vitesse_vent_moyen_at_1_m_(km/h)", 'vitesse_vent_max_(km/h)', 'Direction_(°)']

liste_methodes_interpolation= [
    # {'method': 'linear'},                         # Interpolation linéaire simple.
    # {'method': 'time'},                           # Interpolation linéaire prenant en compte l'index de temps.
    # {'method': 'index', 'order': None},           # Interpolation linéaire prenant en compte l'index numérique.
    # {'method': 'values', 'order': None},          # Identique à 'index'.
    # {'method': 'pad'},                            # Remplissage avec la dernière valeur connue.
    {'method': 'nearest'},                        # Utilisation de la valeur la plus proche pour l'imputation.
    # {'method': 'zero'},                           # Interpolation de type step, qui crée un palier jusqu'à la prochaine valeur.
    # {'method': 'slinear'},                        # Interpolation spline linéaire (ordre 1).
    # {'method': 'quadratic', 'order': 2},          # Interpolation spline d'ordre 2.
    # {'method': 'cubic', 'order': 3},              # Interpolation spline d'ordre 3 (cubique).
    # {'method': 'barycentric'},                    # Interpolation barycentrique.
    # {'method': 'polynomial', 'order': 3},         # Interpolation polynomiale. Vous devez spécifier l'ordre.
    # {'method': 'krogh'},                          # Interpolation de Krogh.
    # {'method': 'piecewise_polynomial', 'order': None}, # Interpolation polynomiale par morceaux.
    # {'method': 'spline', 'order': 3},             # Interpolation spline d'ordre spécifié.
    # {'method': 'pchip'},                          # Interpolation PCHIP (Hermite polynomiale par morceaux cubique).
    # {'method': 'akima'},                          # Interpolation Akima.
    # {'method': 'cubicspline'}                     # Interpolation par spline cubique, spécifique à pandas.
]



# %%
# df = df_13005003_01jan2014_01mar2024.copy()
df = df_station_13054001.copy()
date_debut = '2023-02-01'
date_fin = '2023-02-10'
pas = '0.01D'

#test fpnction
# test_toutes_methodes_interpolation(df, col, date_debut, date_fin, pas, liste_methodes_interpolation)


# %% [markdown]
# ### Calcul de la durée d'un pas en minute traduit en fraction de jour

# %%


pas='0.01D'
# pas='D'
# Pour avoir un pas de 2 min :
duree_pas_en_min=2
fraction_dun_jour = duree_pas_en_min / (60 * 24)
# fraction_dun_jour
print(f"\npour avoir un pas de {duree_pas_en_min}min il faut indiquer:  \npas='{round(fraction_dun_jour,5)}D' \n")

fraction_dun_jour='0.01D'
duree_pas_en_min = float(fraction_dun_jour.replace("D","")) * 24 * 60
print(f"Un pas de \npas=('{fraction_dun_jour}')  \ncorrespond à une durée de  \n'{round(duree_pas_en_min,5)} min \n")




# %%
def convertir_pas_temps(pas_ou_duree):
    """
    Convertit une durée en minutes en fraction de jour en format 'xD' ou l'inverse.

    Args:
        pas_ou_duree (str or int): Soit une durée en minutes (int) à convertir en fraction de jour,
                                   soit une fraction de jour en format 'xD' (str) à convertir en minutes.

    Returns:
        str or float: Conversion de la durée en 'xD' si l'entrée est un int,
                      ou conversion de 'xD' en durée en minutes si l'entrée est un str.
    """
    if isinstance(pas_ou_duree, int):  # Si l'entrée est une durée en minutes
        fraction_dun_jour = pas_ou_duree / (60 * 24)
        pas = round(fraction_dun_jour, 5)
        logger.info(f"pour avoir un pas de \n{pas_ou_duree} min \nil faut indiquer: \npas='{pas}D'")
        return pas
        # return f"pour avoir un pas de {pas_ou_duree} min il faut indiquer: \npas='{round(fraction_dun_jour,5)}D'"
    elif isinstance(pas_ou_duree, str) and pas_ou_duree.endswith("D"):  # Si l'entrée est une fraction de jour
        duree_pas_en_min = float(pas_ou_duree.replace("D", "")) * 24 * 60
        duree=round(duree_pas_en_min,5)
        logger.info(f"Un pas de \npas=('{pas_ou_duree}') \ncorrespond à une durée de \n{duree} min")
        return duree
    else:
        logger.error("Format non reconnu. Veuillez entrer un entier pour les minutes ou une chaîne en format 'xD' pour les jours.")


# %%
# Exemple d'utilisation
print(convertir_pas_temps(2))  # Convertir une durée en minutes en fraction de jour
print(convertir_pas_temps('0.01D'))  # Convertir une fraction de jour en durée en minutes
duree_pas_en_min = convertir_pas_temps('0.01D')
pas = convertir_pas_temps(2)
print(f"\n duree_pas_en_min:\n{duree_pas_en_min} \n")
print(f"\n 2 min correspondent à un pas:\n'{pas}D' \n")


# %% [markdown]
# ### Modif niveau de log

# %%
# Configuration du logging
# 'DEBUG' 'INFO' 'WARNING' 'ERROR'  'CRITICAL'

params = {"niveau_log": 'DEBUG'}
# params = {"niveau_log": 'INFO'}
# params = {"niveau_log": 'WARNING'}
# params = {"niveau_log": 'ERROR'}
# params = {"niveau_log": 'CRITICAL'}
reconfigurer_logging(params)


# %% [markdown]
# # Preprocessing
# ## remplacement des valeurs manquantes

# %%
import pandas as pd
import numpy as np


def remplir_valeurs_manquantes(data):
    """
    Remplit les valeurs manquantes dans le dataset.

    :param data: DataFrame Pandas contenant les données.
    :return: DataFrame avec les valeurs manquantes remplies, nombre de NA avant et après le traitement.
    """
    # Compter le nombre de valeurs NA avant le traitement
    na_avant = data.isna().sum()
    print("Nombre de valeurs NA avant le traitement :")
    print(na_avant)

    # Utiliser la méthode 'interpolate' pour une approximation linéaire des valeurs manquantes
    data_interpolated = data.interpolate()

    # et 'fillna' avec la méthode 'bfill' et 'ffill' pour les valeurs restantes au début et à la fin
    data_filled = data_interpolated.fillna(method='bfill').fillna(method='ffill')

    # Compter le nombre de valeurs NA après le traitement
    na_apres = data_filled.isna().sum()
    print("\nNombre de valeurs NA après le traitement :")
    print(na_apres)

    return data_filled


# %% [markdown]
# ## suppression des outliers
# ### Visualisation et suppression des outliers

# %% [markdown]
# #### traitement 1 par 1

# %%
import matplotlib.pyplot as plt
import seaborn as sns


def traitement_outliers_na(data, col):
    """
    Traite les valeurs manquantes
    Visualise et supprime les outliers des colonnes numeriques,
    graphiques avant et après le traitement.

    :param data: DataFrame contenant les données.
    :param col: Nom de la colonne à visualiser.
    """
    #  suppression des na
    data = remplir_valeurs_manquantes(data)
    # Configuration du style
    sns.set(style="whitegrid")

    # Visualisation avant le traitement des outliers
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.boxplot(y=data[col])
    plt.title(f"Avant le traitement des outliers - {col}")

    # Calcul des limites pour identifier les outliers
    q1 = data[col].quantile(0.25)
    q3 = data[col].quantile(0.75)
    iqr = q3 - q1
    limite_basse = q1 - 1.5 * iqr
    limite_haute = q3 + 1.5 * iqr

    # Suppression des outliers
    data_sans_outliers = data[(data[col] >= limite_basse) & (data[col] <= limite_haute)]

    logger.info(f" data {data.shape}")

    # Visualisation après le traitement des outliers
    plt.subplot(1, 2, 2)
    sns.boxplot(y=data_sans_outliers[col])
    plt.title(f"Après le traitement des outliers - {col}")

    plt.tight_layout()
    plt.show()

    # Scatter plot pour visualiser la répartition des données avant et après
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.scatter(range(len(data)), data[col], alpha=0.5)
    plt.title(f"Avant le traitement des outliers - {col}")

    plt.subplot(1, 2, 2)
    plt.scatter(range(len(data_sans_outliers)), data_sans_outliers[col], alpha=0.5)
    plt.title(f"Après le traitement des outliers - {col}")

    plt.tight_layout()
    plt.show()
    logger.info(f" data_sans_outliers {data_sans_outliers.shape}")
    return data_sans_outliers


# %% [markdown]
# #### meteo france traitement outliers

# %%
import numpy as np
def suppression_outliers_meteo_france_pas_6min(dataframes):
    """

    """
    liste_df_sans_outlier={}
    liste_des_df = [station for station in dataframes.keys()]
    print(f"\nliste_des_df :\n{liste_des_df} \n")

    df = dataframes[liste_des_df[0]]
    print(f"\n describe df :\n{df.describe()} \n")

    for df_name in liste_des_df:
        print(f"\n df:\n{df} \n")
        df = dataframes[df_name]
        # df_name=str(df['station'].iloc[0])
        print(f"\n df_name:\n{df_name} \n")
        print(f"\n describe df :\n{df.describe()} \n")
        list_col = df.select_dtypes(include=[np.number]).columns.tolist()
        print(f"\n list_col:\n{list_col} \n")
        # ['précipitations_(mm)', 'direction_(°)', 'insolation_(mn)', 'vitesse_vent_(km/h)', 'temperature_(°C)']
        list_col.remove("station")
        list_col.remove('précipitations_(mm)') if 'précipitations_(mm)' in list_col else list_col
        print(f"\n list_col:\n{list_col} \n")

        # Traitement des df
        # Suppression des outliers
        for col in list_col:
            # Remplacer les valeurs 99999 par NaN pour utiliser ffill ensuite
            df[col].replace(999999, np.nan, inplace=True)
            #Comme il peut y avoir dautres valeurs aberrantes que 999999, on supprime toutes les valeurs superieures à 90000
            df[col] = df[col].apply(lambda x: np.nan if x > 90000 else x)
            # Appliquer forward fill pour les valeurs NaN
            df[col].fillna(method='ffill', inplace=True)
            valeur_max = df[col].max()
            print(f"\n valeur_max:\n{valeur_max} pour la colonne {col} \n")
            # Clipper les valeurs au-delà de la valeur maximale
            df[col] = df[col].clip(upper=valeur_max)

            # affichage et remplacement des outliers restant
            df_sans_outlier = traitement_outliers_na(df, col)

            # ajout du df sans outliers dans la liste
            liste_df_sans_outlier[df_name] = df_sans_outlier
            # liste_df_sans_outlier.append(df_sans_outlier)
            # liste_df_sans_outlier=pd.DataFrame()
    return liste_df_sans_outlier


# %%
import numpy as np
import pandas as pd
import logging

# # Configuration du logger
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


def suppression_outliers_meteo_france_pas_6min(dataframes):
    """
    Supprime les outliers des DataFrames contenus dans un dictionnaire en se basant sur des critères prédéfinis.
    Les valeurs aberrantes sont identifiées selon des seuils spécifiques et sont soit corrigées, soit supprimées.

    Args:
        dataframes (dict): Un dictionnaire contenant des identifiants de stations météo comme clés et des DataFrames comme valeurs.

    Returns:
        dict: Un dictionnaire avec les mêmes clés que l'entrée, mais où chaque DataFrame a eu ses outliers supprimés ou corrigés.

    Exemple:
        >>> test_data = {'df_test': pd.DataFrame({'temperature_(°C)': [15, 999999, 20], 'précipitations_(mm)': [0, 0, 999999]})}
        >>> result = suppression_outliers_meteo_france_pas_6min(test_data)
        Le résultat sera un dictionnaire avec les DataFrames nettoyés.
    """
    liste_df_sans_outlier = {}
    liste_des_df = [station for station in dataframes.keys()]
    logger.debug(f"Liste des DataFrames à traiter: {liste_des_df}")

    for df_name in liste_des_df:
        try:
            df = dataframes[df_name]
            logger.debug(f"Traitement du DataFrame {df_name}")
            list_col = df.select_dtypes(include=[np.number]).columns.tolist()
            # Suppression de colonnes spécifiques de la liste de traitement
            if "station" in list_col: list_col.remove("station")
            if 'précipitations_(mm)' in list_col: list_col.remove('précipitations_(mm)')
            logger.debug(f"Colonnes numériques traitées: {list_col}")

            for col in list_col:
                try:
                    # Suppression des outliers
                    df[col].replace(999999, np.nan, inplace=True)
                    df[col] = df[col].apply(lambda x: np.nan if x > 90000 else x)
                    df[col].fillna(method='ffill', inplace=True)
                    valeur_max = df[col].max()
                    df[col] = df[col].clip(upper=valeur_max)
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de la colonne {col} dans {df_name}: {e}")

            # Ici, inclure la logique pour traiter et nettoyer davantage le DataFrame df avant de l'ajouter au dictionnaire
            df_sans_outlier = traitement_outliers_na(df, col)
            liste_df_sans_outlier[df_name] = df_sans_outlier

        except Exception as e:
            logger.error(f"Erreur lors du traitement du DataFrame {df_name}: {e}")

    return liste_df_sans_outlier


# %%
# liste_df_sans_outlier = suppression_outliers_meteo_france_pas_6min(dataframes)


# %% [markdown]
# #### sauvegarde des df meteo france au pas de 6 min clean et sans outliers

# %%
#debugage
# %debug
# import pdb
# pdb.set_trace()

import pandas as pd
import logging
import os
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe
from sauve_charge_df_csv_json_pkl import format_and_save_dataframe, save_dataframe
from descriptif_dataset_meteo_france import renommer_colonne_df_meteo_france_6min

logger = logging.getLogger("colorlog_example")


def sauve_df_meteo_france_6min_clean_sans_outliers(liste_df_sans_outlier , chemin_sauvegarde):
    """
    Sauvegarde les datafames donnés par meteo france au pas de 6 min clean et sans outliers
    """

    dataframes_clean_sans_outlier = {}


    for df_name, df in liste_df_sans_outlier.items():

        # Formate convertie et sauve les datasets
        logger.info(f" sauvegarde des datasets ")
        df_name = df_name.replace('df_', '')
        df = save_dataframe(df, df_name, chemin_sauvegarde)
        # Ajouter le DataFrame chargé au dictionnaire
        dataframes_clean_sans_outlier[df_name] = df


    logger.debug(f"\n dataframes:\n{dataframes_clean_sans_outlier} ")
    return dataframes_clean_sans_outlier


# %%
# liste_df_sans_outlier.keys()
# # chemin de sauvegarde des fichiers donnés par meteo france au pas de 6 min traités, suppression des outliers

# path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier
# print(f"\n path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier:\n{path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier} \n")

# dataframes_clean_sans_outlier=sauve_df_meteo_france_6min_clean_sans_outliers(liste_df_sans_outlier,path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier)
# dataframes_clean_sans_outlier


# %% [markdown]
# #### Chargement des df meteo france au pas de 6 min clean et sans outliers

# %%
#debugage
# %debug
# import pdb
# pdb.set_trace()

import pandas as pd
import logging
import os
from sauve_charge_df_csv_json_pkl import charger_all_dataframes, load_dataframe
from sauve_charge_df_csv_json_pkl import format_and_save_dataframe
from descriptif_dataset_meteo_france import renommer_colonne_df_meteo_france_6min

logger = logging.getLogger("colorlog_example")


def charge_df_meteo_france_6min_clean_sans_outliers(chemin_sauvegarde):
    """
    Charge  les datafames donnés par meteo france au pas de 6 min clean et sans outliers
    """

    dataframes_clean_sans_outlier = {}

    dataframes = charger_all_dataframes(chemin_sauvegarde, default_format="csv", sep=",")
    # logger.debug(f"\n dataframes:\n{dataframes} ")
    # # Lecture du fichier .txt
    # df = pd.read_csv(fichier, sep=' ', header=None)
    for df_name, df in dataframes.items():
        # Renommage des colonnes
        # logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
        # logger.debug(f"\n df_name:\n{df_name} ")
        dataframes_clean_sans_outlier[df_name]=df
        # logger.debug(f"\n df_name:\n{df_name} ")


    return dataframes_clean_sans_outlier


# %%
# chemin de sauvegarde des fichiers donnés par meteo france au pas de 6 min traités, suppression des outliers
path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier
print(f"\n path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier:\n{path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier} \n")
dataframes_meteo_france_6_min_clean_sans_outlier = charge_df_meteo_france_6min_clean_sans_outliers(path_sauvegarde_datasets_meteo_france_6min_clean_sans_outlier)


dataframes_meteo_france_6_min_clean_sans_outlier.keys()


# %%
df = dataframes_meteo_france_6_min_clean_sans_outlier["df_station_13005003"]
df=df.copy()
# df=df_station_13054001.copy()
# df=df_station_13005003.copy()

logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
# ['station', 'date', 'précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'vitesse_vent_(km/h)', 'temperature_(°C)']


# %%
# print(f"\n df_mobilis3_7col_sans_outlier.describe():\n{df_mobilis3_7col_sans_na.describe()} \n")
# print(f"\n df_mobilis3_12col_sans_outlier.describe():\n{df_mobilis3_12col_sans_na.describe()} \n")


# %%
# df = df_mobilis3_7col_sans_na.copy()
# list_col = df.select_dtypes(include=[np.number]).columns
# print(f"\n list_col:\n{list_col} \n")

# # Initialisation d'un DataFrame pour recevoir les données sans outliers
# df_mobilis3_7col_sans_outlier = df.copy()

# Suppression colonne
# col='ma_colonne'
# df.drop(columns=[col], inplace=True)

list_col = df.select_dtypes(include=[np.number]).columns.tolist()
# ['précipitations_(mm)', 'direction_(°)', 'insolation_(mn)', 'vitesse_vent_(km/h)', 'temperature_(°C)']
list_col.remove("station")
print(f"\n list_col:\n{list_col} \n")
# for col in list_col:
#     df_mobilis3_7col_sans_outlier = traitement_outliers_na(df_mobilis3_7col_sans_outlier, col)

for col in list_col:
    # Remplacer les valeurs 99999 par NaN pour utiliser ffill ensuite
    df[col].replace(999999, np.nan, inplace=True)
    #Comme il peut y avoir dautres valeurs aberrantes que 999999, on supprime toutes les valeurs superieures à 90000
    df[col]=df[col].apply(lambda x: np.nan if x > 90000 else x)
    # Appliquer forward fill pour les valeurs NaN
    df[col].fillna(method='ffill', inplace=True)
    valeur_max=df[col].max()
    print(f"\n valeur_max:\n{valeur_max} pour la colonne {col} \n")
    # Clipper les valeurs au-delà de la valeur maximale
    df[col] = df[col].clip(upper=valeur_max)

    # affichage et remplacement des outliers restant
    df_sans_outlier = traitement_outliers_na(df, col)
# # Il faut s'assurer que df_sans_outliers est bien mis à jour dans la fonction traitement_outliers_na

# print(f"\n df_sans_outliers.describe():\n{df_mobilis3_7col_sans_outlier.describe()} \n")
#  list_col:
# ['précipitations_(mm)', 'direction_(°)', 'insolation_(mn)', 'vitesse_vent_(km/h)', 'temperature_(°C)']
#  valeur_max:
# 12.0 pour la colonne précipitations_(mm)
#  valeur_max:
# 360.0 pour la colonne direction_(°)
#  valeur_max:
# 100.0 pour la colonne insolation_(mn)
#  valeur_max:
# 3599996.4 pour la colonne vitesse_vent_(km/h)
#  valeur_max:
# 999725.85 pour la colonne temperature_(°C)


# %%
# df = df_mobilis3_12col_sans_na.copy()
# list_col = df.select_dtypes(include=[np.number]).columns
# print(f"\n list_col:\n{list_col} \n")

# # Initialisation d'un DataFrame pour recevoir les données sans outliers
# df_mobilis3_12col_sans_outlier = df.copy()

# for col in list_col:
#     df_mobilis3_12col_sans_outlier = traitement_outliers_na(df_mobilis3_12col_sans_outlier, col)

# # Il faut s'assurer que df_sans_outliers est bien mis à jour dans la fonction traitement_outliers_na

# print(f"\n df_sans_outliers.describe():\n{df_mobilis3_12col_sans_outlier.describe()} \n")


# %%
# print(f"\n df_mobilis3_7col_sans_outlier.describe():\n{df_mobilis3_7col_sans_outlier.describe()} \n")
# print(f"\n df_mobilis3_12col_sans_outlier.describe():\n{df_mobilis3_12col_sans_outlier.describe()} \n")


# %% [markdown]
# ### sauvegarde dataset sans outiliers ni na

# %%
# df_mobilis3_12col_sans_outlier


# %%


# df_clean_12col = format_and_save_dataframe(df_mobilis3_12col_sans_outlier, "clean_12col", path_data_mobilis_upload_data_depuis_api)
# df_clean_7col = format_and_save_dataframe(df_mobilis3_7col_sans_outlier, "clean_7col", path_data_mobilis_upload_data_depuis_api)

# df_clean_12col


# %% [markdown]
# ### Chargement dataset df_sans_outlier_na

# %%
# df_clean_12col = load_dataframe("df_clean_12col",  path_data_mobilis_upload_data_depuis_api,  format_type='pkl')
# df_clean_7col = load_dataframe("df_clean_7col",  path_data_mobilis_upload_data_depuis_api,  format_type='pkl')
# df_clean_7col

# print(f"\n df_clean_7col:\n{df_clean_7col.head(2)} \n")
# print(f"\n df_clean_12col:\n{df_clean_12col.head(2)} \n")


# %%
# print(f"\n df_clean_7col:\n{df_clean_7col.describe()} \n")
# print(f"\n df_clean_12col:\n{df_clean_12col.describe()} \n")


# %%
# df_clean_12col


# %% [markdown]
# ## Normalisation

# %%
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def normaliser_donnees(data):
    """
    Normalise les données numériques à des valeurs entre 0 et 1 tout en conservant les colonnes non numériques.

    :param data: DataFrame contenant les données.
    :return: DataFrame normalisé avec colonnes non numériques conservées.
    """


    # Séparation des colonnes numériques et non numériques
    data_numerique = data.select_dtypes(include=[np.number])
    data_non_numerique = data.select_dtypes(exclude=[np.number])

    # Normalisation des données numériques
    scaler = MinMaxScaler()
    data_numerique_scaled = scaler.fit_transform(data_numerique)

    # Conversion en DataFrame et conservation des noms de colonnes
    data_numerique_scaled = pd.DataFrame(data_numerique_scaled,
                                         columns=data_numerique.columns)

    # Réintégration des colonnes non numériques
    data_final = pd.concat(
        [data_numerique_scaled,
         data_non_numerique.reset_index(drop=True)],
        axis=1)
    logger.info(data_final.head())

    return data_final


# # Exemple d'utilisation
# # Supposons que df_sans_outlier_na soit votre DataFrame initial avec une colonne de date
# df_sans_outlier_normalized = normaliser_donnees(df_sans_outlier_na)

# Afficher le résultat


# %%
# df_clean_12col


# %%
# df = df_clean_12col.copy()
# df_clean_12col_normalized = normaliser_donnees(df)
# df = df_clean_7col.copy()
# df_clean_7col_normalized = normaliser_donnees(df)


# %%
# df = df_clean_7col_normalized
# df


# %%
# df = df_clean_12col_normalized
# df


# %% [markdown]
# ### Sauvegarde dataset normalisé

# %%

# df_normalized_12col = format_and_save_dataframe(df_clean_12col_normalized, "normalized_12col", path_data_mobilis_upload_data_depuis_api)
# df_normalized_7col = format_and_save_dataframe(df_clean_7col_normalized, "normalized_7col", path_data_mobilis_upload_data_depuis_api)


# %% [markdown]
# ### Chargement dataset normalisé

# %%
df_normalized_12col = load_dataframe("df_normalized_12col",  path_data_mobilis_upload_data_depuis_api,  format_type='pkl')
df_normalized_7col = load_dataframe("df_normalized_7col",  path_data_mobilis_upload_data_depuis_api,  format_type='pkl')


# %%

# Convertir la colonne 'date' au format datetime
df_normalized_12col['date'] = pd.to_datetime(df_normalized_12col['date'])

# Définir la colonne 'date' comme index du DataFrame
df_normalized_12col = df_normalized_12col.set_index('date')


# Convertir la colonne 'date' au format datetime
df_normalized_7col['date'] = pd.to_datetime(df_normalized_7col['date'])

# Définir la colonne 'date' comme index du DataFrame
df_normalized_7col = df_normalized_7col.set_index('date')


# %%
df_normalized_12col


# %% [markdown]
# # Analyse graphique du dataset
# ## Fonction pour tracer les données de série temporelle

# %%
import matplotlib.pyplot as plt
import numpy as np


def plot_time_series(data, columns, title="Time Series Data"):
    """
    Trace les séries temporelles pour les colonnes spécifiées.

    :param data: DataFrame contenant la série temporelle.
    :param columns: Liste des noms de colonnes à tracer.
    :param title: Titre du graphique.
    """
    plt.figure(figsize=(14, 7))
    for col in columns:
        plt.plot(data.index, data[col], label=col)
    plt.title(title)
    plt.legend()
    plt.show()


# %%
# df=df_normalized_12col.copy()
# df


# %%
# df = df_normalized_12col.copy()
# df=df_normalized_7col.copy()
print(f"\n df.columns.to_list:\n{df.columns.tolist()} \n")


# %%
# plot_time_series(df_mobilis_sans_outlier,columns=df_mobilis2.select_dtypes(include=[np.number]).columns)
# columns = ['temperature_(°)', 'vitesse_(km/h)', 'rafale_(km/h)']
columns = ['wave_amplitude_(m)', 'wave_period_(s)', 'direction_de_surface_(°)', 'temperature_eau_(°C)', 'humidity_(%)',
           'pression_(bar)', 'temperature_(°C)', 'direction_(°)', 'vitesse_(km/h)', 'rafale_(km/h)', 'vitesse_surface_(km/h)']
columns = ['vitesse_(km/h)', 'rafale_(km/h)', 'vitesse_surface_(km/h)']
plot_time_series(df, columns)
columns = ['direction_de_surface_(°)',  'direction_(°)']
plot_time_series(df, columns)
columns = ['direction_de_surface_(°)',  'direction_(°)']
plot_time_series(df, columns)
columns = ['temperature_eau_(°C)']
plot_time_series(df, columns)
columns = ['wave_amplitude_(m)', 'wave_period_(s)']
plot_time_series(df, columns)


# %% [markdown]
# ## Fonction pour afficher une matrice de corrélation

# %%
import seaborn as sns
import numpy as np


def plot_correlation_matrix(data, title="Correlation Matrix"):
    """
    Affiche la matrice de corrélation des caractéristiques dans le DataFrame.

    :param data: DataFrame dont on souhaite afficher la corrélation.
    :param title: Titre du graphique.
    !! ne choisir que des colonnes numeriques
    """

    plt.figure(figsize=(10, 8))
    correlation_matrix = data.corr()
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm')
    plt.title(title)
    plt.show()


# %%
# plot_correlation_matrix(df)
print(f"\n df.columns.to_list:\n{df.columns.tolist()} \n")


# %%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Supposons que df_13001009_01jan2014_01mar2024 est votre DataFrame original
df = df_13001009_01jan2014_01mar2024.copy()

# Étape 1 et 2: Exclure 'station' si elle existe et utiliser 'date' comme index
if 'station' in df.columns:
    df = df.drop(columns='station')
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d%H')  # Ajustez le format si nécessaire
df = df.set_index('date')

# Étape 3: Sélectionner uniquement les colonnes numériques
df_numeric = df.select_dtypes(include=[np.number])


# Étape 4: Tracer la matrice de corrélation
def plot_correlation_matrix(df):
    corr = df.corr()
    plt.figure(figsize=(15, 12))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True)
    plt.title("Matrice de Corrélation")
    plt.tight_layout()
    plt.show()


plot_correlation_matrix(df_numeric)


# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Exemple de DataFrame ajusté avec les vrais noms de colonnes
# Note : Remplacez `df` par le nom de votre DataFrame réel
# df = ...
print(df.columns.tolist())
#Assurez-vous que les données sont numériques (devraient déjà l'être selon vos noms de colonnes)
df['vitesse_vent_moyen_at_1_m_(km/h)'] = pd.to_numeric(df['vitesse_vent_moyen_at_1_m_(km/h)'], errors='coerce')
df['Direction_(°)'] = pd.to_numeric(df['Direction_(°)'], errors='coerce')

# Calcul de la corrélation entre vitesse du vent et direction
corr_matrix = df[['vitesse_vent_moyen_at_1_m_(km/h)', 'Direction_(°)']].corr()
print("Matrice de corrélation entre la vitesse et la direction du vent :")
print(corr_matrix)

# Visualisation avec un scatter plot
plt.figure(figsize=(6, 4))
sns.scatterplot(data=df, x='vitesse_vent_moyen_at_1_m_(km/h)', y='Direction_(°)')
plt.title('Corrélation entre la vitesse et la direction du vent')
plt.xlabel('Vitesse du vent à 1m (km/h)')
plt.ylabel('Direction du vent (°)')
plt.tight_layout()
plt.show()


# %%
df = df_normalized_7col.copy()
df = df.select_dtypes(include=[np.number])
plot_correlation_matrix(df)


# %%
# df = df[['wave_amplitude_(m)', 'wave_period_(s)', 'direction_de_surface_(°)','rafale_(km/h)', 'vitesse_(km/h)', 'direction_(°)']]
# plot_correlation_matrix(df)


# %%
# df = df[['pression_(bar)', 'temperature_(°C)','rafale_(km/h)', 'vitesse_(km/h)', 'direction_(°)']]
# plot_correlation_matrix(df)


# %% [markdown]
# ## Fonction pour créer des scatter plots entre deux variables

# %%
def plot_scatter(data, x_col, y_col, title="Scatter Plot"):
    """
    Crée un scatter plot entre deux variables.

    :param data: DataFrame contenant les données.
    :param x_col: Nom de la colonne pour l'axe des x.
    :param y_col: Nom de la colonne pour l'axe des y.
    :param title: Titre du graphique.
    """
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=data, x=x_col, y=y_col)
    plt.title(title)
    plt.show()


# %%
plot_scatter(df, df['vitesse_(km/h)'], df['temperature_(°C)'])


# %% [markdown]
# ## Fonction pour créer des diagrammes de dispersion avec régression linéaire

# %%
def plot_regression(data, x_col, y_col, title="Regression Plot"):
    """
    Crée un diagramme de dispersion avec une ligne de régression linéaire.

    :param data: DataFrame contenant les données.
    :param x_col: Nom de la colonne pour l'axe des x.
    :param y_col: Nom de la colonne pour l'axe des y.
    :param title: Titre du graphique.
    """
    plt.figure(figsize=(10, 6))
    sns.regplot(x=x_col,
                y=y_col,
                data=data,
                scatter_kws={
                    'alpha': 0.5,
                    'color': 'blue'
                },
                line_kws={'color': 'orange'})
    plt.title(title)
    plt.show()


# %%
# df = df_sans_outlier_normalized
x_col = 'vitesse_(km/h)'
y_col = 'temperature_(°C)'
plot_regression(df, x_col, y_col)


# %% [markdown]
# ## Fonction pour visualiser la distribution d'une variable

# %%
def plot_distribution(data, column, title="Distribution Plot"):
    """
    Affiche la distribution d'une variable.

    :param data: DataFrame contenant les données.
    :param column: Nom de la colonne à visualiser.
    :param title: Titre du graphique.
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(data[column], kde=True)
    plt.title(title)
    plt.show()


# %%
df = df_normalized_12col.copy()
df


# %%

list_col = df.select_dtypes(include=[np.number]).columns
# ['temperature_(°)', 'vitesse_(km/h)', 'rafale_(km/h)', 'direction']
print(f"\n list_col:\n{list_col} \n")
for col in list_col:
    plot_distribution(data=df, column=col)


# %%
# plot_distribution(df_sans_outlier,'rafale_(km/h)')
#



# %% [markdown]
# # Modelisation
#

# %% [markdown]
# ### Modèles Potentiels et Approches
# 1. Régressions avancées (par exemple, Random Forests ou Gradient Boosting Machines comme XGBoost) :
# - Ces modèles peuvent capturer des relations non linéaires complexes entre les caractéristiques d'entrée (comme la température, l'humidité, la direction du vent précédente, etc.) et la vitesse ou la direction du vent. Ils sont flexibles et souvent performants sans nécessiter une grande quantité de données d'entraînement.
#
# 2. Réseaux de neurones récurrents (RNN), en particulier LSTM et GRU :
# - Ces modèles sont conçus pour traiter des séquences de données, ce qui les rend particulièrement adaptés pour des prévisions temporelles où la relation temporelle entre les points de données est cruciale. Ils pourraient être plus adaptés pour prédire des séquences de vitesse de vent sur les trois horizons temporels.
#
# 3. Modèles hybrides :
# - Une approche combinant des réseaux neuronaux pour capturer des dynamiques temporelles complexes, avec des modèles basés sur des arbres pour exploiter des relations spatiales et non linéaires entre les caractéristiques, peut offrir une flexibilité et une performance accrues.
#
# ### Étapes
# 1. Prétraitement des données :
# - Assurez-vous que vos données sont nettoyées et normalisées. Pour les modèles temporels, structurez vos données en séquences qui reflètent les dépendances temporelles.
#
# 2. Feature engineering :
# - Créez des caractéristiques supplémentaires qui pourraient aider le modèle à mieux comprendre les dynamiques météorologiques, telles que des indicateurs de changement de temps, des moyennes mobiles, ou des mesures de tendance.
#
# 3. Sélection de modèles et validation croisée :
# - Testez plusieurs modèles et configurations pour identifier ceux qui offrent les meilleures performances sur vos données. Utilisez la validation croisée, en particulier une forme temporelle de la validation croisée pour les séries temporelles, pour évaluer la robustesse de vos modèles.
#
# 4. Optimisation des hyperparamètres :
# - Ajustez les hyperparamètres de vos modèles sélectionnés pour maximiser la performance. Des outils comme Grid Search ou Random Search peuvent être utiles, ou des approches plus sophistiquées comme Bayesian Optimization.
#
# 5. Évaluation et déploiement : Une fois que vous avez sélectionné le modèle le plus performant, évaluez-le sur un jeu de données de test pour vous assurer qu'il répond à vos attentes en termes de précision de prévision pour les différents horizons temporels. Déployez ensuite le modèle pour une utilisation en temps réel, en prévoyant une mise à jour régulière avec de nouvelles données pour maintenir sa précision.
#
#

# %% [markdown]
#     1. Les stations:
#
#  **13028004, 13030001, 13031002, 13055001, 13092001**
#
# contiennent les colonnes suivantes :
#
# station, date, précipitations_(mm), temperature_(°C)
#
#     2. Les stations:
#
# **13054001, 13005003, 13022003, 13036003, 13047001, 13055029, 13062002, 13074003, 13091002, 13103001, 13108004, 13110003, 13111002**
#
#  contiennent les colonnes suivantes :
#
# station, date, précipitations_(mm), direction_(°), humidity_(%), vitesse_vent_(km/h), temperature_(°C)
#
#     3. La station:
# **13056002** contient les colonnes suivantes :
#
# station, date, direction_(°), temperature_(°C)

# %% [markdown]
# ## Regression linéaire

# %% [markdown]
# ### changement niveau de log

# %%
# Configuration du logging
# 'DEBUG' 'INFO' 'WARNING' 'ERROR'  'CRITICAL'

# params = {"niveau_log": 'DEBUG'}
# params = {"niveau_log": 'INFO'}
# params = {"niveau_log": 'WARNING'}
params = {"niveau_log": 'ERROR'}
# params = {"niveau_log": 'CRITICAL'}
reconfigurer_logging(params)


# %%
# import pandas as pd
# import numpy as np
# from sklearn.linear_model import LinearRegression
# import matplotlib.pyplot as plt
# from sklearn.metrics import mean_squared_error
# import logging



# def preparer_donnees(df, params):
#     """
#     Prépare les données pour la modélisation en filtrant les dates, extrayant les composants temporels,
#     et en appliquant un encodage one-hot sur les données temporelles.

#     :param df: DataFrame contenant les données à préparer.
#     :return: DataFrame préparé avec les dummies des composants temporels.
#     """
#     df['date'] = pd.to_datetime(df['date'])
#     if filtre:
#         # Filtrage des données entre le 1er juin et le 30 septembre de chaque année
#         df = df[df['date'].dt.month.isin([6, 7, 8, 9])]
#         # Filtrage pour les heures de 8h à 18h inclus
#         df = df[(df['date'].dt.hour >= 8) & (df['date'].dt.hour <= 18)]


#     # Extraction des composants temporels
#     df['mois'] = df['date'].dt.month
#     df['heure'] = df['date'].dt.hour
#     df['minute'] = df['date'].dt.minute

#     # Suppression des colonnes inutiles pour la modélisation
#     df = df.drop(['station', 'date', 'précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], axis=1)
#     logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
#     # Application des dummies
#     df = pd.get_dummies(df, columns=['mois', 'heure', 'minute'])

#     return df




# logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")


# def prediction_vent_avec_filtre(df, params):
#     resultats=[]
#     # Préparation des données
#     df_prepared = preparer_donnees(df, filtre=filtre_horaire)
#     df_prepared.index = pd.to_datetime(df_prepared.index)


#     # Division des données (assurez-vous que la colonne 'vitesse_vent_(km/h)' est bien dans votre df_prepared)
#     train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='index')

#     # Modèle de régression linéaire
#     X_train = train_data.drop(['vitesse_vent_(km/h)'], axis=1)
#     y_train = train_data['vitesse_vent_(km/h)']


#     model = LinearRegression()
#     model.fit(X_train, y_train)

#     # Prédiction
#     X_test = test_data.drop(['vitesse_vent_(km/h)'], axis=1)
#     y_test = test_data['vitesse_vent_(km/h)']
#     predictions = model.predict(X_test)

#     # Calcul du MSE
#     mse = mean_squared_error(y_test, predictions)
#     logger.info(f"MSE sur l'ensemble de test: {round(mse, 2)}(km/h)²")
#     # Calcul du RMSE
#     # Le MSE est exprimé dans le carré de l'unité de la variable cible, on calcul sa racine carré
#     rmse = np.sqrt(mse)
#     resultats.append(rmse)
#     logger.info(f"RMSE sur l'ensemble de test: {round(rmse,2)}km/h")

#     # Tracé
#     plt.figure(figsize=(10, 6))
#     plt.plot(y_test.values, label='Valeurs réelles')
#     plt.plot(predictions, color='red', label='Prédictions')
#     plt.title('Prédictions vs Valeurs Réelles de la Vitesse du Vent')
#     plt.legend()
#     plt.show()

#     return resultats

# # Resultat en prenant les mois heures minute du 1juin au 30 septembre
# # RMSE sur l'ensemble de test: 3.78km/h

# # Resultat en prenant les mois heures minute du 1juin au 30 septembre et en filtrant les données du jour de 8h à 18h
# # RMSE sur l'ensemble de test: 3.84km/h

# # Resultat en prenant les mois heures minute sur tout le dataset
# # RMSE sur l'ensemble de test: 7.48km/h


# %%
# import pandas as pd
# import numpy as np
# from sklearn.linear_model import LinearRegression
# import matplotlib.pyplot as plt
# from sklearn.metrics import mean_squared_error
# import logging



# def preparer_donnees(df, params):
#     """
#     Prépare les données pour la modélisation en filtrant les dates, extrayant les composants temporels,
#     et en appliquant un encodage one-hot sur les données temporelles.

#     :param df: DataFrame contenant les données à préparer.
#     :param params: Dictionnaire contenant les paramètres de filtre.
#     :return: DataFrame préparé avec les dummies des composants temporels.
#     """
#     df['date'] = pd.to_datetime(df['date'])
#     # Filtrage mensuel
#     if 'filtre_mensuel' in params:
#         df = df[df['date'].dt.month.isin(params['filtre_mensuel'])]

#     # Filtrage horaire
#     if 'filtre_horaire' in params:
#         plage_horaire = params['filtre_horaire']
#         df = df[(df['date'].dt.hour >= plage_horaire[0]) & (df['date'].dt.hour <= plage_horaire[1])]

#     # Suppression des colonnes inutiles
#     if 'colonnes_to_drop' in params:
#         df = df.drop(params['colonnes_to_drop'], axis=1)

#     # Extraction et dummification des composants temporels
#         #creation des colonnes
#     df['mois'] = df['date'].dt.month
#     df['heure'] = df['date'].dt.hour
#     df['minute'] = df['date'].dt.minute
#     df = pd.get_dummies(df, columns=['mois', 'heure', 'minute'])

#     return df


# def prediction_vent_avec_filtre(df, params):
#     resultats=[]
#     # Préparation des données
#     df_prepared = preparer_donnees(df, params)
#     df_prepared.index = pd.to_datetime(df_prepared.index)


#     # Division des données (assurez-vous que la colonne 'vitesse_vent_(km/h)' est bien dans votre df_prepared)
#     train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='index')

#     # Modèle de régression linéaire
#     X_train = train_data.drop(['vitesse_vent_(km/h)'], axis=1)
#     y_train = train_data['vitesse_vent_(km/h)']


#     model = LinearRegression()
#     model.fit(X_train, y_train)

#     # Prédiction
#     X_test = test_data.drop(['vitesse_vent_(km/h)'], axis=1)
#     y_test = test_data['vitesse_vent_(km/h)']
#     predictions = model.predict(X_test)

#     # Calcul du MSE
#     mse = mean_squared_error(y_test, predictions)
#     logger.info(f"MSE sur l'ensemble de test: {round(mse, 2)}(km/h)²")
#     # Calcul du RMSE
#     # Le MSE est exprimé dans le carré de l'unité de la variable cible, on calcul sa racine carré
#     rmse = np.sqrt(mse)
#     # Enregistrement des résultats avec détails des filtres
#     details_filtres = f"Mois: {params['filtre_mensuel']}, Heures: {params.get('filtre_horaire', 'Toutes')}, Colonnes supprimées: {params.get('colonnes_to_drop', 'Aucune')}"
#     resultats.append((rmse, details_filtres))

#     # Affichage des résultats
#     print(f"RMSE: {rmse} - Filtres: {details_filtres}")

#     # Tracé
#     plt.figure(figsize=(10, 6))
#     plt.plot(y_test.values, label='Valeurs réelles')
#     plt.plot(predictions, color='red', label='Prédictions')
#     plt.title('Prédictions vs Valeurs Réelles de la Vitesse du Vent')
#     plt.legend()
#     plt.show()

#     return resultats


# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import logging



def preparer_donnees(df, filtre_mensuel, filtre_horaire, colonnes_to_drop):
    """
    Prépare les données pour la modélisation en filtrant les dates, extrayant les composants temporels,
    et en appliquant un encodage one-hot sur les données temporelles.

    Args:
        df: DataFrame contenant les données à préparer.
        filtre_mensuel: Liste des mois à inclure dans l'analyse.
        filtre_horaire: Tuple contenant les heures de début et de fin à inclure dans l'analyse.
        colonnes_to_drop: Liste des noms des colonnes à supprimer du DataFrame.

    Returns:
        DataFrame préparé avec les dummies des composants temporels.
    """
    try:
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'].dt.month.isin(filtre_mensuel)]
        df = df[(df['date'].dt.hour >= filtre_horaire[0]) & (df['date'].dt.hour <= filtre_horaire[1])]

        df['mois'] = df['date'].dt.month
        df['heure'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

        # Suppression des colonnes inutiles pour la modélisation
        colonnes_a_supprimer = ['station', 'date'] + colonnes_to_drop
        for col in colonnes_a_supprimer:
            if col in df.columns:
                df.drop(col, axis=1, inplace=True)

        df = pd.get_dummies(df, columns=['mois', 'heure', 'minute'])
        # #suppression des colonnes, en plus de la colonne date
        # df = df.drop( colonnes_to_drop, axis=1, errors='ignore')
        # # df = df.drop( colonnes_to_drop, axis=1)
        # df = df.drop(['station', 'date'], axis=1)
        return df
    except Exception as e:
        logger.error(f"Erreur lors de la préparation des données: {e}")
        return pd.DataFrame()


def prediction_vent_avec_filtre(df_original, params):

    i=0
    resultats = []
    colonne_to_predict=params['colonne_to_predict']
    plages_mensuelles = params["plages_mensuelles"]
    plages_horaires = params["plages_horaires"]
    colonnes_possibles_a_supprimer = params["colonnes_possibles_a_supprimer"]
    logger.debug(f"\n plages_mensuelles:\n{plages_mensuelles} ")
    logger.debug(f"\n plages_horaires:\n{plages_horaires} ")
    logger.debug(f"\n colonnes_possibles_a_supprimer:\n{colonnes_possibles_a_supprimer} ")

    #test la presence de la colonne à predire dans le df
    if colonne_to_predict not in df_original.columns.tolist():
        return
    # unite_colonne_to_predict =[colonne[colonne.find('('):] if '(' in colonne else '' for colonne in [colonne_to_predict]]
    unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''
    logger.debug(f"\n unite_colonne_to_predict:\n{unite_colonne_to_predict} ")

    for filtre_mensuel in plages_mensuelles:
        for filtre_horaire in plages_horaires:
            for colonnes_to_drop in colonnes_possibles_a_supprimer:
                df = df_original.copy()
                logger.debug(f"\n filtre_mensuel:\n{filtre_mensuel} ")
                logger.debug(f"\n filtre_horaire:\n{filtre_horaire} ")
                logger.debug(f"\n colonnes_to_drop:\n{colonnes_to_drop} ")
                logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
                df_prepared = preparer_donnees(df, filtre_mensuel, filtre_horaire, colonnes_to_drop)
                logger.debug(f"\n liste colonnes:\n{df_prepared.columns.tolist()} ")
                # Appliquer split_time_series, entraîner le modèle, calculer et enregistrer le RMSE
                # Préparation des données
                # df_prepared = preparer_donnees(df, params)
                df_prepared.index = pd.to_datetime(df_prepared.index)
                logger.debug(f"\n liste colonnes:\n{df_prepared.columns.tolist()} ")
                # Division des données (assurez-vous que la colonne 'vitesse_vent_(km/h)' est bien dans votre df_prepared)
                train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='index')
                logger.debug(f"\n train_data:\n{train_data.head(2)} ")
                logger.debug(f"\n test_data:\n{test_data.head(2)} ")

                # Modèle de régression linéaire
                X_train = train_data.drop([colonne_to_predict], axis=1)
                y_train = train_data[colonne_to_predict]

                model = LinearRegression()
                model.fit(X_train, y_train)

                # Prédiction
                X_test = test_data.drop([colonne_to_predict], axis=1)
                y_test = test_data[colonne_to_predict]
                predictions = model.predict(X_test)

                # Calcul du MSE
                mse = mean_squared_error(y_test, predictions)
                logger.info(f"MSE sur l'ensemble de test: {round(mse, 2)}(km/h)²")
                # Calcul du RMSE
                # Le MSE est exprimé dans le carré de l'unité de la variable cible, on calcul sa racine carré
                rmse = np.sqrt(mse)
                # Enregistrement des résultats avec détails des filtres
                df_name = params['df_name']
                details_filtres = f"test:{i}, {df_name}, Unité:{unite_colonne_to_predict}  Mois: {filtre_mensuel}, Heures: {filtre_horaire}, Colonnes supprimées: {colonnes_to_drop}"
                resultat = ((round(rmse, 3), details_filtres))
                resultats.append(resultat)
                i+=1
                # Affichage des résultats
                print(f"RMSE: {round(rmse,3)}_{unite_colonne_to_predict} - Filtres: {details_filtres}")

                # Tracé
                # plt.figure(figsize=(10, 6))
                # plt.plot(y_test.values, label='Valeurs réelles')
                # plt.plot(predictions, color='red', label='Prédictions')
                # plt.title(f'Prédictions vs Valeurs Réelles de la {colonne_to_predict}')
                # plt.legend()
                # plt.show()
    meilleur_rmse = min(resultats, key=lambda x: x[0])
    print(f"Meilleur RMSE: {meilleur_rmse[0]} - Filtres: {meilleur_rmse[1]}")
    return resultats
    # Trouver et afficher la configuration avec le RMSE le plus bas
    # meilleur_resultat = min(resultats, key=lambda x: x[0])
    # logger.info(f"Meilleur RMSE: {meilleur_resultat[0]} avec la configuration: {meilleur_resultat[1]}")


# Exemple d'utilisation
# Assurez-vous que df est défini et que les fonctions nécessaires sont bien implémentées
# prediction_vent_avec_filtre(df)


# %%
df = dataframes_meteo_france_6_min_clean_sans_outlier["df_station_13005003"]
df = df.copy()
logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
params = {
    "colonne_to_predict":'vitesse_vent_(km/h)',
    "df_name":df_name,
    "plages_mensuelles": [[6, 7, 8, 9], [7, 8], [5, 6, 7, 8, 9, 10], [4, 5, 6, 7, 8, 9, 10]],
    "plages_horaires": [[8, 18], [7, 19], [9, 17], [10, 16], [6, 20], [0,23]],
    "colonnes_possibles_a_supprimer": [
        ['précipitations_(mm)'],
        ['direction_(°)'],
        ['humidity_(%)'],
        ['temperature_(°C)'],
        ['précipitations_(mm)', 'direction_(°)'],
        ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'],
        []  # Aucune colonne supprimée
    ],
}
# resultats=prediction_vent_avec_filtre(df, params)

# score_regression_lineaire_df_station_13005003=resultats
# RMSE: 3.76_(km/h) - Filtres: test:0, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [8, 18], Colonnes supprimées: ['précipitations_(mm)']
# RMSE: 3.736_(km/h) - Filtres: test:1, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [8, 18], Colonnes supprimées: ['direction_(°)']
# RMSE: 3.707_(km/h) - Filtres: test:2, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [8, 18], Colonnes supprimées: ['humidity_(%)']
# RMSE: 4.023_(km/h) - Filtres: test:3, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [8, 18], Colonnes supprimées: ['temperature_(°C)']
# RMSE: 3.741_(km/h) - Filtres: test:4, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)']
# RMSE: 3.837_(km/h) - Filtres: test:5, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)']
# RMSE: 3.756_(km/h) - Filtres: test:6, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [8, 18], Colonnes supprimées: []
# RMSE: 3.817_(km/h) - Filtres: test:7, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [7, 19], Colonnes supprimées: ['précipitations_(mm)']
# RMSE: 3.79_(km/h) - Filtres: test:8, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [7, 19], Colonnes supprimées: ['direction_(°)']
# RMSE: 3.748_(km/h) - Filtres: test:9, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [7, 19], Colonnes supprimées: ['humidity_(%)']
# RMSE: 4.036_(km/h) - Filtres: test:10, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [7, 19], Colonnes supprimées: ['temperature_(°C)']
# RMSE: 3.793_(km/h) - Filtres: test:11, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [7, 19], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)']
# RMSE: 3.879_(km/h) - Filtres: test:12, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [7, 19], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)']
# RMSE: 3.814_(km/h) - Filtres: test:13, df_station_13111002, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [7, 19], Colonnes supprimées: []


# %% [markdown]
# ### boucle sur tous les datasets meteo-france au pas de  6 min

# %% [markdown]
# ##### aprroche mois heure minute

# %%
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
# import logging


# def preparer_donnees(df, filtre_mensuel, filtre_horaire, colonnes_to_drop):
#     """
#     Prépare les données pour la modélisation en filtrant les dates, extrayant les composants temporels,
#     et en appliquant un encodage one-hot sur les données temporelles.

#     Args:
#         df: DataFrame contenant les données à préparer.
#         filtre_mensuel: Liste des mois à inclure dans l'analyse.
#         filtre_horaire: Tuple contenant les heures de début et de fin à inclure dans l'analyse.
#         colonnes_to_drop: Liste des noms des colonnes à supprimer du DataFrame.

#     Returns:
#         DataFrame préparé avec les dummies des composants temporels.
#     """
#     try:
#         df['date'] = pd.to_datetime(df['date'])
#         df = df[df['date'].dt.month.isin(filtre_mensuel)]
#         df = df[(df['date'].dt.hour >= filtre_horaire[0]) & (df['date'].dt.hour <= filtre_horaire[1])]

#         df['mois'] = df['date'].dt.month
#         df['heure'] = df['date'].dt.hour
#         df['minute'] = df['date'].dt.minute

#         # Suppression des colonnes inutiles pour la modélisation
#         colonnes_a_supprimer = ['station', 'date'] + colonnes_to_drop
#         for col in colonnes_a_supprimer:
#             if col in df.columns:
#                 df.drop(col, axis=1, inplace=True)

#         df = pd.get_dummies(df, columns=['mois', 'heure', 'minute'])
#         # #suppression des colonnes, en plus de la colonne date
#         # df = df.drop( colonnes_to_drop, axis=1, errors='ignore')
#         # # df = df.drop( colonnes_to_drop, axis=1)
#         # df = df.drop(['station', 'date'], axis=1)
#         return df
#     except Exception as e:
#         logger.error(f"Erreur lors de la préparation des données: {e}")
#         return pd.DataFrame()


# %%
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
# import logging

# def prediction_vent_avec_filtre(df_original, params):
#     resultats = []
#     colonne_to_predict = params['colonne_to_predict']
#     plages_mensuelles = params["plages_mensuelles"]
#     plages_horaires = params["plages_horaires"]
#     colonnes_possibles_a_supprimer = params["colonnes_possibles_a_supprimer"]
#     df_name = params['df_name']
#     i=0
#     if colonne_to_predict not in df_original.columns:
#         logger.error(f"La colonne à prédire '{colonne_to_predict}' n'est pas présente dans le DataFrame.")
#         return []
#     unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''

#     for filtre_mensuel in plages_mensuelles:
#         for filtre_horaire in plages_horaires:
#             for colonnes_to_drop in colonnes_possibles_a_supprimer:
#                 df = df_original.copy()
#                 df_prepared = preparer_donnees(df, filtre_mensuel, filtre_horaire, colonnes_to_drop)
#                 df_prepared.index = pd.to_datetime(df_prepared.index)

#                 # Supposons que split_time_series est correctement implémenté
#                 train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='index')

#                 X_train = train_data.drop([colonne_to_predict], axis=1)
#                 y_train = train_data[colonne_to_predict]
#                 X_test = test_data.drop([colonne_to_predict], axis=1)
#                 y_test = test_data[colonne_to_predict]

#                 model = LinearRegression()
#                 model.fit(X_train, y_train)
#                 predictions = model.predict(X_test)

#                 mse = mean_squared_error(y_test, predictions)
#                 rmse = np.sqrt(mse)
#                 mae = mean_absolute_error(y_test, predictions)
#                 r2 = r2_score(y_test, predictions)

#                 details_filtres = f"test:{i}, {df_name}, Unité:{unite_colonne_to_predict} - Mois: {filtre_mensuel}, Heures: {filtre_horaire}, Colonnes supprimées: {colonnes_to_drop}"
#                 resultats.append((rmse, mae, r2, details_filtres))
#                 i+=1
#                 logger.debug(f"RMSE: {rmse}{unite_colonne_to_predict}, MAE: {mae}, R2: {r2} - Filtres: {details_filtres}")

#     meilleur_rmse = min(resultats, key=lambda x: x[0])
#     logger.info(f"Meilleur RMSE: {meilleur_rmse[0]} - Filtres: {meilleur_rmse[3]}")
#     return resultats


# %%
# %%capture
# # df = dataframes_meteo_france_6_min_clean_sans_outlier["df_station_13005003"]
# liste_resultats=[]

# for df_name, df in dataframes_meteo_france_6_min_clean_sans_outlier.items():
#     df=dataframes_meteo_france_6_min_clean_sans_outlier[df_name]
#     df = df.copy()
#     logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
#     params = {
#         "heure_de_reference": 9,  # 9 heure de la journée pour la prédiction
#         "decalages_en_minutes": [40, 120, 180],  # 40 min, 2h, 3h
#         "colonne_to_predict": 'vitesse_vent_(km/h)',
#         "df_name": df_name,
#         "plages_mensuelles": [[6, 7, 8, 9], [7, 8], [5, 6, 7, 8, 9, 10], [4, 5, 6, 7, 8, 9, 10]],
#         "plages_horaires": [[8, 18], [7, 19], [9, 17], [10, 16], [6, 20], [0, 23]],
#         "colonnes_possibles_a_supprimer": [
#             ['précipitations_(mm)'],
#             ['direction_(°)'],
#             ['humidity_(%)'],
#             ['temperature_(°C)'],
#             ['précipitations_(mm)', 'direction_(°)'],
#             ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'],
#             []  # Aucune colonne supprimée
#         ],
#     }
#     name_tableau_resultat=f'score_RMSE_regression_lineaire_{df_name}'
#     resultats = prediction_vent_avec_filtre(df, params)
#     name_tableau_resultat = resultats
#     liste_resultats.append(name_tableau_resultat)
# liste_resultats


# %%
# df = dataframes_meteo_france_6_min_clean_sans_outlier["df_station_13005003"]
# df = df.copy()

# #  paramètres
# params = {
#     "filtre_mensuel": [6, 7, 8, 9],
#     "filtre_horaire": lambda df: (df['date'].dt.hour >= 8) & (df['date'].dt.hour <= 18),
#     "colonnes_to_drop": ['station', 'date', 'précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)']
# }


# resultats=prediction_vent_avec_filtre(df, params)


# %%
# # resultats
# score_regression_lineaire_df_station_13005003 = resultats

# meilleur_rmse = min(score_regression_lineaire_df_station_13005003, key=lambda x: x[0])
# print(f"Meilleur RMSE: {meilleur_rmse[0]} - Filtres: {meilleur_rmse[1]}")
# # Meilleur RMSE: 3.3128742573271173 - Filtres: Mois: [6, 7, 8, 9], Heures: [10, 16], Colonnes supprimées: []


# %%
# liste_resultats


# %%
# Aplatir la liste de listes en une seule liste de tuples, en ignorant les éléments None
liste_resultats_aplatie = [resultat for sous_liste in liste_resultats if sous_liste is not None for resultat in sous_liste]

meilleur_score = float('inf')
meilleure_description = ""

# Parcourir la liste aplaties de résultats pour trouver le meilleur score
for score, description in liste_resultats_aplatie:
    if score < meilleur_score:
        meilleur_score = score
        meilleure_description = description

# Afficher le meilleur score et la description
print(f"meilleur score: {meilleur_score}, avec {meilleure_description}")
# meilleur score: 3.313, avec test:27, df_station_13005003, Unité:(km/h)  Mois: [6, 7, 8, 9], Heures: [10, 16], Colonnes supprimées: []


# %% [markdown]
# #### prevision avec décalage horaire,  obtenir  les previsions à 40 min 2h, 3h à partir de 9h le matin

# %%
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def preparer_donnees_pour_prediction_horaires(df, plage_mensuelle, plage_horaire, colonnes_to_drop, heure_de_reference, decalages_en_minutes,
                                              colonne_to_predict):
    """
    Ajoute des colonnes décalées pour les prédictions futures spécifiques.
    """
    # colonne_to_predict = params['colonne_to_predict']
    # heure_de_reference = params['heure_de_reference']
    # decalages_en_minutes = params['decalages_en_minutes']
    df = df.copy()

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    df = df[df['date'].dt.month.isin(plage_mensuelle)]
    df = df[(df['date'].dt.hour >= plage_horaire[0]) & (df['date'].dt.hour <= plage_horaire[1])]

    df['mois'] = df['date'].dt.month
    df['heure'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute


    # df['timestamp'] = pd.to_datetime(df['date']) + pd.to_timedelta(df['heure'], unit='h') + pd.to_timedelta(df['minute'], unit='m')
    # logger.debug(f"\n df['timestamp']:\n{df['timestamp']} ")

    for decalage in decalages_en_minutes:
        # nom_colonne = f'vent_plus_{decalage}min'
        nom_colonne =f'{colonne_to_predict}_plus_{decalage}min'
        logger.debug(f"\n nom_colonne:\n{nom_colonne} ")
        df[nom_colonne] = df.groupby(df['date'].dt.date)[colonne_to_predict].shift(-decalage // 6)
        logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")

    # Filtrer pour une heure de référence spécifique pour la prédiction
    df = df[df['date'].dt.hour == heure_de_reference]
    logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
    logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")

    # Suppression des colonnes inutiles pour la modélisation
    colonnes_a_supprimer = ['station', 'date'] + colonnes_to_drop
    for col in colonnes_a_supprimer:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)
    df=df.dropna()
    logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
    return df


# %%
from unittest import result
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV


def prediction_vent_avec_filtre_et_horaires(df_original, params):


    resultats = []
    colonne_to_predict = params['colonne_to_predict']
    plages_mensuelles = params["plages_mensuelles"]
    plages_horaires = params["plages_horaires"]
    colonnes_possibles_a_supprimer = params["colonnes_possibles_a_supprimer"]
    heure_de_reference = params["heure_de_reference"]
    decalages_en_minutes = params["decalages_en_minutes"]
    df_name = params.get("df_name", "DataFrame")

    # Extraction de l'unité de la colonne à prédire pour les étiquettes des graphiques et le RMSE
    if colonne_to_predict not in df_original.columns:
        logger.error(f"La colonne à prédire '{colonne_to_predict}' n'est pas présente dans le DataFrame.")
        return []
    # unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''
    unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''



    logger.debug(f"\n unite_colonne_to_predict:\n{unite_colonne_to_predict} ")
    logger.debug(f"\n liste colonnes:\n{df_original.columns.tolist()} ")
    for plage_mensuelle in plages_mensuelles:
        logger.debug(f"\n plage_mensuelle:\n{plage_mensuelle} ")
        for plage_horaire in plages_horaires:
            logger.debug(f"\nplage_horaire :\n{plage_horaire} ")
            for colonnes_to_drop in colonnes_possibles_a_supprimer:
                logger.debug(f"\n colonnes_to_drop:\n{colonnes_to_drop} ")
                df = df_original.copy()
                df_prepared = preparer_donnees_pour_prediction_horaires(df, plage_mensuelle, plage_horaire, colonnes_to_drop, heure_de_reference,
                                                                        decalages_en_minutes, colonne_to_predict)
                df_prepared.index = pd.to_datetime(df_prepared.index)
                logger.debug(f"\n liste colonnes:\n{df_prepared.columns.tolist()} ")
                if df_prepared.empty:
                    continue  # Skip si le df préparé est vide

                # Supposons que split_time_series est correctement implémenté
                train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='index')

                for decalage in decalages_en_minutes:
                    logger.debug(f"\n decalage:\n{decalage} ")
                    nom_colonne_cible = f'{colonne_to_predict}_plus_{decalage}min'
                    # df[nom_colonne_cible] train_data[nom_colonne_cible] = train_data[colonne_to_predict].shift(-decalage)
                    X_train = train_data.drop([nom_colonne_cible], axis=1, errors='ignore')
                    y_train = train_data[nom_colonne_cible]
                    X_test = test_data.drop([nom_colonne_cible], axis=1, errors='ignore')
                    y_test = test_data[nom_colonne_cible]
                    logger.debug(f"\n X_train:\n{X_train} ")
                    logger.debug(f"\n y_train:\n{y_train} ")
                    logger.debug(f"\n X_test:\n{X_test} ")
                    logger.debug(f"\n y_test:\n{y_test} ")
                    model = LinearRegression()
                    model.fit(X_train, y_train)
                    predictions = model.predict(X_test)

                    mse = mean_squared_error(y_test, predictions)
                    rmse = np.sqrt(mse)

                    # Enregistrement des résultats avec détails des filtres
                    details_filtres = f"{df_name} - Mois: {plage_mensuelle}, Heures: {plage_horaire}, Colonnes supprimées: {colonnes_to_drop}, Prédiction pour: +{decalage}min, Unité: {unite_colonne_to_predict}"
                    resultats.append((rmse, details_filtres))

                    # Log des résultats
                    print(f"RMSE: {rmse}{unite_colonne_to_predict} - Filtres: {details_filtres}")
    return resultats


# %%
# %%capture
# df = dataframes_meteo_france_6_min_clean_sans_outlier["df_station_13005003"]
liste_resultats = []

for df_name, df in dataframes_meteo_france_6_min_clean_sans_outlier.items():
    df = dataframes_meteo_france_6_min_clean_sans_outlier[df_name]
    df = df.copy()
    logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
    params = {
        "heure_de_reference":
        9,  # 9 heure de la journée pour la prédiction
        "decalages_en_minutes": [40, 120, 180],  # 40 min, 2h, 3h
        "colonne_to_predict":        'vitesse_vent_(km/h)',
        # "colonne_to_predict":        'direction_(°)',
        "df_name":
        df_name,
        "plages_mensuelles": [[6, 7, 8, 9], [7, 8], [5, 6, 7, 8, 9, 10], [4, 5, 6, 7, 8, 9, 10]],
        "plages_horaires": [[8, 18], [7, 19], [9, 17], [10, 16], [6, 20], [0, 23]],
        "colonnes_possibles_a_supprimer": [
            ['précipitations_(mm)'],
            ['direction_(°)'],
            ['humidity_(%)'],
            ['temperature_(°C)'],
            ['précipitations_(mm)', 'direction_(°)'],
            ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'],
            []  # Aucune colonne supprimée
        ],
    }
    name_tableau_resultat = f'score_RMSE_regression_lineaire_{df_name}'
    resultats = prediction_vent_avec_filtre_et_horaires(df, params)
    name_tableau_resultat = resultats
    liste_resultats.append(name_tableau_resultat)

# resultats_meteo_france_6min_all_stations_vent = liste_resultats


# %%
# liste_resultats2


# %%
from collections import defaultdict

resultats_meteo_france_6min_all_stations_direction = liste_resultats2

liste_resultats = resultats_meteo_france_6min_all_stations_direction
# Initialisation d'un dictionnaire pour regrouper les RMSE par ensemble de paramètres
rmse_par_ensemble = defaultdict(list)

# Extraction et regroupement des RMSE par ensemble de paramètres
for triplet_rmse in liste_resultats:
    for rmse, details in triplet_rmse:
        # Clé pour regrouper: retirer la partie variable des détails ('Prédiction pour')
        cle_ensemble = details.split(", Prédiction pour:")[0]
        rmse_par_ensemble[cle_ensemble].append(rmse)

# Calculer un score agrégé (somme des RMSE) pour chaque ensemble
scores_ensembles = {cle: sum(rmses) for cle, rmses in rmse_par_ensemble.items()}

# Trouver l'ensemble de paramètres avec le score le plus bas
meilleur_ensemble = min(scores_ensembles, key=scores_ensembles.get)
meilleur_score = scores_ensembles[meilleur_ensemble]

print(f"# Meilleur ensemble de paramètres: {meilleur_ensemble}")
print(f"# Score agrégé (somme des RMSE): {meilleur_score}")


# df_station_13022003
# Meilleur ensemble de paramètres: df_station_13022003 - Mois: [5, 6, 7, 8, 9, 10], Heures: [6, 20], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)']
# Score agrégé (somme des RMSE): 8.011629065679076
# (RMSE:2.3156712228633487,"df_station_13022003 - Mois: [5, 6, 7, 8, 9, 10], Heures: [6, 20], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Prédiction pour: +40min, Unité: (km/h)"),
# (RMSE: 2.869402454031047,"df_station_13022003 - Mois: [5, 6, 7, 8, 9, 10], Heures: [6, 20], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Prédiction pour: +120min, Unité: (km/h)"),
# (RMSE:2.8265553887846804,"df_station_13022003 - Mois: [5, 6, 7, 8, 9, 10], Heures: [6, 20], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Prédiction pour: +180min, Unité: (km/h)"),
# Meilleur ensemble de paramètres: df_station_13111002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['précipitations_(mm)']
# Score agrégé (somme des RMSE): 6.967227896155137

# Meilleur ensemble de paramètres: df_station_13056002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)']
# Score agrégé (somme des RMSE): 57.83439305689105


# %%
from collections import defaultdict
import heapq


resultats_meteo_france_6min_all_stations_direction = liste_resultats2

liste_resultats = resultats_meteo_france_6min_all_stations_direction
liste_resultats = resultats_meteo_france_6min_all_stations_vent
# Initialisation d'un dictionnaire pour regrouper les RMSE par ensemble de paramètres
rmse_par_ensemble = defaultdict(list)

# Dictionnaire pour conserver les détails de chaque RMSE
details_par_ensemble = defaultdict(list)

for triplet_rmse in liste_resultats:
    for rmse, details in triplet_rmse:
        # Clé pour regrouper: retirer la partie variable des détails ('Prédiction pour')
        cle_ensemble = details.split(", Prédiction pour:")[0]
        rmse_par_ensemble[cle_ensemble].append(rmse)
        details_par_ensemble[cle_ensemble].append((rmse, details))

# Calculer un score agrégé (somme des RMSE) pour chaque ensemble
scores_ensembles = {cle: sum(rmses) for cle, rmses in rmse_par_ensemble.items()}

# Trouver les 3 ensembles de paramètres avec les scores les plus bas
trois_meilleurs_ensembles = heapq.nsmallest(3, scores_ensembles, key=scores_ensembles.get)

# Afficher les détails pour les trois meilleurs ensembles
for ensemble in trois_meilleurs_ensembles:
    score = scores_ensembles[ensemble]
    details = details_par_ensemble[ensemble]
    print(f"# Meilleur ensemble de paramètres: {ensemble}")
    print(f"# Score agrégé (somme des RMSE): {score}")
    print("# Détails:")
    for rmse, detail in sorted(details, key=lambda x: x[0]):  # Trier par RMSE si nécessaire
        print(f"# (RMSE: {rmse}, \"{detail}\")")
    print("\n")


# Meilleur ensemble de paramètres: df_station_13111002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['précipitations_(mm)']
# Score agrégé (somme des RMSE): 6.967227896155137
# Détails:
# (RMSE: 2.13942914431285, "df_station_13111002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['précipitations_(mm)'], Prédiction pour: +120min, Unité: (km/h)")
# (RMSE: 2.372933328710459, "df_station_13111002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['précipitations_(mm)'], Prédiction pour: +180min, Unité: (km/h)")
# (RMSE: 2.454865423131827, "df_station_13111002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['précipitations_(mm)'], Prédiction pour: +40min, Unité: (km/h)")



# Meilleur ensemble de paramètres: df_station_13056002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)']
# Score agrégé (somme des RMSE): 57.83439305689105
# Détails:
# (RMSE: 14.887744648698703, "df_station_13056002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)'], Prédiction pour: +120min, Unité: (°)")
# (RMSE: 16.999117295010173, "df_station_13056002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)'], Prédiction pour: +180min, Unité: (°)")
# (RMSE: 25.94753111318218, "df_station_13056002 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)'], Prédiction pour: +40min, Unité: (°)")

# Meilleur ensemble de paramètres: df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['humidity_(%)']
# Score agrégé (somme des RMSE): 58.71523744842912
# Détails:
# (RMSE: 17.790243566286055, "df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['humidity_(%)'], Prédiction pour: +40min, Unité: (°)")
# (RMSE: 19.248990507055584, "df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['humidity_(%)'], Prédiction pour: +120min, Unité: (°)")
# (RMSE: 21.676003375087486, "df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['humidity_(%)'], Prédiction pour: +180min, Unité: (°)")

# Meilleur ensemble de paramètres: df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)']
# Score agrégé (somme des RMSE): 59.108745180276884
# Détails:
# (RMSE: 18.299432848133478, "df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)'], Prédiction pour: +40min, Unité: (°)")
# (RMSE: 19.518263313564685, "df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)'], Prédiction pour: +120min, Unité: (°)")
# (RMSE: 21.291049018578715, "df_station_13022003 - Mois: [7, 8], Heures: [9, 17], Colonnes supprimées: ['temperature_(°C)'], Prédiction pour: +180min, Unité: (°)")


# %%
with open(f'{datasets_dir}/SYNOP/{schema_filename}', 'r') as json_file:
    schema = json.load(json_file)

synop_codes = list(schema['definitions']['donnees-synop-essentielles-omm_records']['properties']['fields']['properties'].keys())
# ---- Get the columns name as descriptions
#
synop_desc = list(df.columns)

# ---- Set Codes as columns name
#
df.columns = synop_codes
code2desc = dict(zip(synop_codes, synop_desc))

# ---- Count the na values by columns
#
columns_na = df.isna().sum().tolist()

# ---- Show all of that
#
df_desc = pd.DataFrame({'Code': synop_codes, 'Description': synop_desc, 'Na': columns_na})


# %% [markdown]
# #### Version intégrant d'autres modeles: RandomForestRegressor et XGboost, KNeighborsRegressor

# %%
# import pandas as pd
# import logging

# def preparer_donnees_pour_prediction_horaires(df, plage_mensuelle, plage_horaire, colonnes_to_drop, heure_de_reference, decalages_en_minutes,
#                                               colonne_to_predict):
#     """
#     Ajoute des colonnes décalées pour les prédictions futures spécifiques.
#     """

#     df = df.copy()

#     df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
#     df = df[df['date'].dt.month.isin(plage_mensuelle)]
#     df = df[(df['date'].dt.hour >= plage_horaire[0]) & (df['date'].dt.hour <= plage_horaire[1])]

#     df['mois'] = df['date'].dt.month
#     df['heure'] = df['date'].dt.hour
#     df['minute'] = df['date'].dt.minute


#     for decalage in decalages_en_minutes:
#         # nom_colonne = f'vent_plus_{decalage}min'
#         nom_colonne_decaled = f'{colonne_to_predict}_plus_{decalage}min'
#         logger.debug(f"\n nom_colonne:\n{nom_colonne_decaled} ")
#         df[nom_colonne_decaled] = df.groupby(df['date'].dt.date)[colonne_to_predict].shift(-decalage // 6)
#         logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")

#     # Filtrer pour une heure de référence spécifique pour la prédiction
#     df = df[df['date'].dt.hour == heure_de_reference]
#     logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
#     logger.debug(f"\n heure_de_reference:\n{heure_de_reference} ")

#     # Suppression des colonnes inutiles pour la modélisation
#     colonnes_a_supprimer = ['station', 'date'] + colonnes_to_drop
#     for col in colonnes_a_supprimer:
#         if col in df.columns:
#             df.drop(col, axis=1, inplace=True)
#     df = df.dropna()
#     logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
#     return df, nom_colonne_decaled


# %%
# import pandas as pd
# import logging

# # Configuration du logger pour l'exemple
# # logging.basicConfig(level=logging.DEBUG)
# # logger = logging.getLogger(__name__)


# def preparer_donnees_pour_prediction_horaires(df, plage_mensuelle, plage_horaire, colonnes_to_drop, heure_de_reference, decalages_en_minutes,
#                                               colonne_to_predict):
#     """
#     Ajoute des colonnes décalées pour les prédictions futures spécifiques.
#     """
#     df = df.copy()

#     # df.index = pd.to_datetime(df.index, unit='s')  #unité en secondes
#     # df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
#     # Vérifier si la colonne 'date' est de type datetime
#     logger.debug(f"\n plage_mensuelle:\n{plage_mensuelle} ")
#     logger.debug(f"\n plage_horaire:\n{plage_horaire} ")
#     logger.debug(f"\n heure_de_reference:\n{heure_de_reference} ")
#     logger.debug(f"\n colonnes_to_drop:\n{colonnes_to_drop} ")
#     logger.debug(f"\n decalages_en_minutes:\n{decalages_en_minutes} ")
#     logger.debug(f"\n colonne_to_predict:\n{colonne_to_predict} ")
#     if not np.issubdtype(df['date'].dtype, np.datetime64):
#         logger.debug("Conversion de la colonne 'date' en datetime.")
#         df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
#     else:
#         logger.debug("La colonne 'date' est déjà de type datetime.")

#     df = df[df['date'].dt.month.isin(plage_mensuelle)]
#     df = df[(df['date'].dt.hour >= plage_horaire[0]) & (df['date'].dt.hour <= plage_horaire[1])]
#     logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")


#     # noms_colonnes_decalees = []
#     # Calculer le pas temporel moyen en minutes
#     df.sort_values('date', inplace=True)
#     pas_temporel_moyen = (df['date'].diff().dt.total_seconds().dropna().mean() / 60).round()
#     logger.debug(f"Pas temporel moyen : {pas_temporel_moyen} minutes.")

#     df['mois'] = df['date'].dt.month
#     df['heure'] = df['date'].dt.hour
#     df['minute'] = df['date'].dt.minute

#     # for decalage in decalages_en_minutes:
#     #     nom_colonne_decaled = f'{colonne_to_predict}_plus_{decalage}min'
#     #     df[nom_colonne_decaled] = df.groupby(df['date'].dt.date)[colonne_to_predict].shift(-decalage // 6) # 6 pour un pas de 6 min
#     # noms_colonnes_decalees.append(nom_colonne_decaled)
#     for decalage in decalages_en_minutes:
#         # Ajuster le décalage en fonction du pas temporel moyen
#         decalage_en_pas = int(np.round(decalage / pas_temporel_moyen))
#         nom_colonne_decaled = f'{colonne_to_predict}_plus_{decalage}min'
#         df[nom_colonne_decaled] = df.groupby(df['date'].dt.date)[colonne_to_predict].shift(-decalage_en_pas)  # pour un pas pas_temporel_moyen


#     df = df[df['date'].dt.hour == heure_de_reference]
#     logger.debug(f"\n liste colonnes du df avant suppression des colonnes:\n{df.columns.tolist()} ")
#     logger.debug(f"\n df aprés decalage mais  avant suppression des colonnes:\n{df.head(2)} ")

#     colonnes_a_supprimer = ['station', 'date'] + colonnes_to_drop
#     df.drop(columns=colonnes_a_supprimer, errors='ignore', inplace=True)
#     df = df.dropna()
#     logger.debug(f"\n liste colonnes du df aprés decalage aprés suppression des colonnes mais avant le split_times_series:\n{df.columns.tolist()} ")
#     logger.debug(f"\n df aprés decalage aprés suppression des colonnes mais avant le split_times_series:\n{df.head(2)} ")
#     return df


# %%
import pandas as pd
import numpy as np
import logging

# # Configuration du logger pour l'exemple
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


def preparer_donnees_pour_prediction_horaires(df, plage_mensuelle, plage_horaire, colonnes_to_drop, heure_de_reference, decalages_en_minutes,
                                              colonne_to_predict):
    """
    Ajoute des colonnes décalées pour les prédictions futures spécifiques tout en conservant l'information temporelle.
    """
    df = df.copy()
    logger.debug(f"\n liste colonnes du df avant suppression des colonnes:\n{df.columns.tolist()} ")
    logger.debug(f"\n df avant decalage :\n{df.head(2)} ")

    # Assurer que 'date' est au format datetime
    if not np.issubdtype(df['date'].dtype, np.datetime64):
        logger.debug("Conversion de la colonne 'date' en datetime.")
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    else:
        logger.debug("La colonne 'date' est déjà de type datetime.")

    # Filtrage selon les plages mensuelles et horaires
    df = df[df['date'].dt.month.isin(plage_mensuelle)]
    df = df[(df['date'].dt.hour >= plage_horaire[0]) & (df['date'].dt.hour <= plage_horaire[1])]

    df['mois'] = df['date'].dt.month
    df['heure'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    logger.debug(f"\n liste colonnes du df avant suppression des colonnes:\n{df.columns.tolist()} ")
    logger.debug(f"\n df avant decalage et avant suppression des colonnes:\n{df.head(2)} ")
    # Définir 'date' comme index
    df.set_index('date', inplace=True)

    # Calcul du pas temporel moyen pour ajuster les décalages
    pas_temporel_moyen = (df.index.to_series().diff().dt.total_seconds().dropna().mean() / 60).round()
    logger.debug(f"Pas temporel moyen : {pas_temporel_moyen} minutes.")

    for decalage in decalages_en_minutes:
        decalage_en_pas = int(np.round(decalage / pas_temporel_moyen))
        nom_colonne_decaled = f'{colonne_to_predict}_plus_{decalage}min'
        df[nom_colonne_decaled] = df[colonne_to_predict].shift(-decalage_en_pas)

    # Filtrage selon l'heure de référence
    df = df[df.index.hour == heure_de_reference]

    logger.debug(f"\n liste colonnes du df avant suppression des colonnes:\n{df.columns.tolist()} ")
    logger.debug(f"\n df aprés decalage mais avant suppression des colonnes:\n{df.head(2)} ")
    # Suppression des colonnes non nécessaires, en conservant 'date' sous forme d'index
    colonnes_a_supprimer = set(['station'] + colonnes_to_drop)
    df.drop(columns=list(colonnes_a_supprimer.intersection(df.columns)), errors='ignore', inplace=True)

    df = df.dropna()
    logger.debug(f"\n liste colonnes du df aprés suppression des colonnes:\n{df.columns.tolist()} ")
    logger.debug(f"\n df aprés decalage mais  aprés suppression des colonnes:\n{df.head(2)} ")

    return df


# %%
# # # Configuration du logger pour le débogage
# # logger = logging.getLogger(__name__)
# # logging.basicConfig(level=logging.DEBUG)


# %%
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.pipeline import Pipeline
# from sklearn.neighbors import KNeighborsRegressor
# from sklearn.linear_model import LinearRegression
# from sklearn.ensemble import RandomForestRegressor
# from torch import logdet
# from xgboost import XGBRegressor
# import numpy as np
# import pandas as pd
# import logging


# def prediction_vent_avec_filtre_et_horaires(df_original, params):
#     """
#     Effectuer des prédictions de vitesse et de direction du vent à plusieurs horizons temporels.

#     :param df_original: DataFrame contenant les données météorologiques historiques.
#     :type df_original: pd.DataFrame
#     :param params: Dictionnaire contenant les paramètres de configuration pour le modèle et la prédiction.
#     :type params: dict
#     :return: Liste des résultats de prédiction, chaque élément est un dictionnaire avec les détails et le score RMSE.
#     :rtype: list

#     >>> df_test = pd.DataFrame(...)  # DataFrame exemple
#     >>> params_test = {...}  # Paramètres exemple
#     >>> resultats = prediction_vent_avec_filtre_et_horaires(df_test, params_test)
#     """
#     resultats = []
#     colonne_to_predict = params['colonne_to_predict']
#     plages_mensuelles = params["plages_mensuelles"]
#     plages_horaires = params["plages_horaires"]
#     colonnes_possibles_a_supprimer = params["colonnes_possibles_a_supprimer"]
#     heure_de_reference = params["heure_de_reference"]
#     decalages_en_minutes = params["decalages_en_minutes"]
#     df_name = params.get("df_name", "DataFrame")
#     models_types = params.get('model_type', [LinearRegression])  # par defaut utilise la regression linéaire

#     #Controle de la presence de la colonne à predire dans le dataset
#     # Extraction de l'unité de la colonne à prédire pour les étiquettes des graphiques et le RMSE
#     if colonne_to_predict not in df_original.columns:
#         logger.error(f"La colonne à prédire '{colonne_to_predict}' n'est pas présente dans le DataFrame.")
#         return []
#     # unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''
#     unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''
#     # Logger les informations importantes
#     logger.debug(f"Début de la fonction de prédiction pour la colonne: {colonne_to_predict}")
#     i = 1
#     logger.debug(f"\n test n°:\n{i} ")
#     for model_class in models_types:
#         model_name = model_class.__name__
#         logger.debug(f"Évaluation du modèle : {model_name}")

#         # Sélection et configuration initiale du modèle
#         # if model_class in [RandomForestRegressor, XGBRegressor, LinearRegression]:
#         #     model = model_class(random_state=params.get("random_state", 42))
#         #     logger.debug(f"\n model_class:\n{model_class} ")
#         #########
#         if model_class in [RandomForestRegressor, XGBRegressor]:
#             model = model_class(random_state=params.get("random_state", 42))
#             logger.debug(f"\n model_class:\n{model_class} ")
#         elif model_class == LinearRegression:
#             model = model_class()  # Pas de random_state pour LinearRegression
#             logger.debug(f"\n model_class:\n{model_class} ")
#         else:
#             logger.error(f"Modèle {model_class} non géré par la configuration.")
#             return []

#         ######### PREPARATION GRID_SEARCH ##############
#         # Préparation du dictionnaire de paramètres pour GridSearchCV
#         param_grid = {}
#         hyperparametres = {}
#         # if 'model_params' in params and model_name in params['model_params']:
#         # if 'model_params' in params:
#         #     for key, value in params['model_params'].items():
#         #         logger.debug(f"\n key:\n{key}  ------- value {value}")
#         #         if key.startswith(model_name.lower()):  # Adapter pour le modèle courant
#         #             # Extraction du nom du paramètre sans le préfixe du modèle
#         #             new_key = key.split('__')[1]
#         #             logger.debug(f"\n new_key:\n{new_key} ")
#         #             param_grid[f'regressor__{new_key}'] = value
#         #             hyperparametres[key] = value
#         #             logger.debug(f"\n hyperparametres:\n{hyperparametres} ")
#         # else:
#         #     logger.warning(f"Aucun hyperparamètre spécifié pour {model_name}. Utilisation des paramètres par défaut.")
#         #     param_grid = {}


#         ################
#         if 'model_params' in params:
#             model_params = params['model_params']
#             for key, value in model_params.items():
#                 # S'assurer que le modèle actuel a des paramètres spécifiés
#                 if key.startswith(model_name):
#                     # Adaptation du nom du paramètre pour GridSearchCV
#                     param_name = key.replace(model_name + '__', '')
#                     param_grid[f'model__{param_name}'] = value
#                     hyperparametres[param_name] = value  # Stocker sans le préfixe 'model__'
#         else:
#             logger.warning(f"Aucun hyperparamètre spécifié pour {model_name}. Utilisation des paramètres par défaut.")
#             param_grid = {}
# ################
# # Initialisation et configuration du modèle
# # model = model_class(random_state=params.get("random_state", 42))
#         grid_search = GridSearchCV(Pipeline([('model', model)]),
#                                    param_grid,
#                                    cv=params.get('cv', 3),
#                                    scoring=params.get('scoring', 'neg_mean_squared_error'),
#                                    n_jobs=-1)
#         logger.debug(f"\n model:\n{model} ")
#         logger.debug(f"\n grid_search:\n{grid_search} ")

#         ######### ITERATION SUR LES PLAGES MENSUELLES ############
#         for plage_mensuelle in plages_mensuelles:
#             logger.debug(f"\n plage_mensuelle:\n{plage_mensuelle} ")
#             for plage_horaire in plages_horaires:
#                 logger.debug(f"\nplage_horaire :\n{plage_horaire} ")
#                 for colonnes_to_drop in colonnes_possibles_a_supprimer:
#                     logger.debug(f"\n colonnes_to_drop:\n{colonnes_to_drop} ")
#                     df = df_original.copy()
#                     ######### PREPARATION df ############
#                     df_prepared = preparer_donnees_pour_prediction_horaires(df, plage_mensuelle, plage_horaire, colonnes_to_drop, heure_de_reference,
#                                                                             decalages_en_minutes, colonne_to_predict)
#                     logger.debug(f"\n df_prepared:\n{df_prepared.head(2)} ")
#                     logger.debug(f"\n liste colonnes:\n{df_prepared.columns.tolist()} ")

#                     ######### TRAIN TEST SPLIT ############
#                     # df_prepared.index = pd.to_datetime(df_prepared.index, unit='us') # 'us' pour microsecondes
#                     # df_prepared.set_index(nom_colonne_decaled, inplace=True)
#                     # df_prepared.index = pd.to_datetime(df_prepared.index)

#                     # logger.debug(f"\n nom_colonne_decaled :\n{nom_colonne_decaled} ")
#                     if df_prepared.empty:
#                         continue  # Skip si le df préparé est vide

#                     # Séparation des datasets avec la fonction split_time_series
#                     train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='index')
#                     # train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='date')

#                     ######### ITERATION SUR LES COLONNES DECALLEES ############
#                     for decalage in decalages_en_minutes:
#                         logger.debug(f"\n decalage:\n{decalage} ")
#                         nom_colonne_cible = f'{colonne_to_predict}_plus_{decalage}min'
#                         # nom_colonne_cible = nom_colonne_decaled
#                         logger.debug(f"\n nom_colonne_cible:\n{nom_colonne_cible} ")
#                         # df[nom_colonne_cible] train_data[nom_colonne_cible] = train_data[colonne_to_predict].shift(-decalage)
#                         X_train = train_data.drop([nom_colonne_cible], axis=1, errors='ignore')
#                         y_train = train_data[nom_colonne_cible]
#                         X_test = test_data.drop([nom_colonne_cible], axis=1, errors='ignore')
#                         y_test = test_data[nom_colonne_cible]
#                         logger.debug(f"\n X_train:\n{X_train} ")
#                         logger.debug(f"\n y_train:\n{y_train} ")
#                         logger.debug(f"\n X_test:\n{X_test} ")
#                         logger.debug(f"\n y_test:\n{y_test} ")
#                         model = model
#                         # model.fit(X_train, y_train)
#                         # predictions = model.predict(X_test)
#                         ###### ENTRAINNEMENT #######
#                         # Entraînement et optimisation du modèle avec GridSearchCV
#                         grid_search.fit(X_train, y_train)

#                         # Meilleur modèle après GridSearch
#                         best_model = grid_search.best_estimator_
#                         logger.debug(f"\n best_model:\n{best_model} ")

#                         ###### PREDICTIONS #######
#                         # Prédiction sur l'ensemble de test avec le meilleur modèle
#                         predictions = best_model.predict(X_test)
#                         logger.debug(f"\n predictions:\n{predictions} ")
#                         ######

#                         # # Enregistrement des résultats avec détails des filtres
#                         # details_filtres = f"{df_name} - Mois: {plage_mensuelle}, Heures: {plage_horaire}, Colonnes supprimées: {colonnes_to_drop}, Prédiction pour: +{decalage}min, Unité: {unite_colonne_to_predict}"
#                         # resultats.append((rmse, details_filtres))
#                         # Calcul des scores
#                         mse = mean_squared_error(y_test, predictions)
#                         rmse = np.sqrt(mse)
#                         mae = mean_absolute_error(y_test, predictions)
#                         r2 = r2_score(y_test, predictions)

#                         # Stockage des résultats
#                         resultats.append({
#                             'df_name': df_name,
#                             'model': model_name,
#                             'rmse': rmse,
#                             'unité': unite_colonne_to_predict,
#                             'mae': mae,
#                             'r2': r2,
#                             'plage_mensuelle': plage_mensuelle,
#                             'plage_horaire': plage_horaire,
#                             'colonnes_supprimees': colonnes_to_drop,
#                             'meilleurs_parametres': grid_search.best_params_,
#                             'hyperparametres': hyperparametres
#                         })

#                         logger.debug(
#                             f"test:{i} - {df_name}-->  RMSE: {round(rmse,3)}{unite_colonne_to_predict}, MAE: {round(mae,3)}{unite_colonne_to_predict}, R2: {round(r2*100,3)}%, Meilleurs paramètres: {grid_search.best_params_}, hyperparametre: {hyperparametres} "
#                         )
#                         i += 1

#                         # Log des résultats
#                         # print(f"RMSE: {rmse}{unite_colonne_to_predict} - Filtres: {details_filtres}")
#     return resultats


# %%
# from sklearn.model_selection import GridSearchCV
# from sklearn.pipeline import Pipeline
# import logging
# from sklearn.svm import SVR
# from sklearn.ensemble import GradientBoostingRegressor as GBR
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.tree import DecisionTreeRegressor as DTR
# from sklearn.linear_model import ElasticNet as ElasticNet
# from sklearn.linear_model import Ridge
# from sklearn.neighbors import KNeighborsRegressor
# from sklearn.linear_model import LinearRegression


# def prepare_modele_et_grid_search(model_class, params):
#     """
#     Configure et exécute GridSearchCV pour un modèle donné.

#     :param model_class: Classe du modèle à utiliser.
#     :param params: Dictionnaire de paramètres pour la configuration et GridSearch.
#     :return: Instance du model et la preparation du GridSearchCV .
#     """
#     model_name = model_class.__name__
#     logger.debug(f"Évaluation du modèle : {model_name}")

#     # if model_class in [RandomForestRegressor, XGBRegressor]:
#     #     model = model_class(random_state=params.get("random_state", 42))
#     #     logger.debug(f"\n model_class:\n{model_class} ")
#     # elif model_class == LinearRegression:
#     #     model = model_class()  # Pas de random_state pour LinearRegression
#     #     logger.debug(f"\n model_class:\n{model_class} ")
#     # else:
#     #     logger.error(f"Modèle {model_class} non géré par la configuration.")
#     #     return []
#     param_grid = {}
#     hyperparametres = {}
#     for key, value in params['model_params'].items():
#         logger.debug(f"\n key:\n{key}  ------- value {value}")
#         if key.startswith(model_name):
#             logger.debug(f"\n key.startswith(model_name):\n{key} ")
#             param_name = key.replace(model_name + '__', '')
#             param_grid[f'model__{param_name}'] = value
#             hyperparametres[param_name] = value

#     if not param_grid:
#         logger.warning(f"Aucun hyperparamètre spécifié pour {model_name}. Utilisation des paramètres par défaut.")

#     # Condition spéciale pour les modèles qui ne prennent pas `random_state`
#     if model_class in [LinearRegression, KNeighborsRegressor]:
#         model = model_class()
#     else:
#         model = model_class(random_state=params.get("random_state"))

#     grid_search = GridSearchCV(Pipeline([('model', model)]),
#                                param_grid,
#                                cv=params.get('cv', 3),
#                                scoring=params.get('scoring', 'neg_mean_squared_error'),
#                                n_jobs=-1)

#     return model, grid_search, hyperparametres


# %%
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
import logging


def prepare_modele_et_grid_search(model_class, params):
    """
    Configure et exécute GridSearchCV pour un modèle donné.

    :param model_class: Classe du modèle à utiliser.
    :param params: Dictionnaire de paramètres pour la configuration et GridSearch.
    :return: Instance du model et la preparation du GridSearchCV .
    """
    model_name = model_class.__name__
    logger.debug(f"Évaluation du modèle : {model_name}")

    param_grid = {}
    hyperparametres = {}
    for key, value in params['model_params'].items():
        logger.debug(f"\n key:\n{key}  ------- value {value}")
        if key.startswith(model_name):
            logger.debug(f"\n key.startswith(model_name):\n{key} ")
            param_name = key.replace(model_name + '__', '')
            param_grid[f'model__{param_name}'] = value
            hyperparametres[param_name] = value

    if not param_grid:
        logger.warning(f"Aucun hyperparamètre spécifié pour {model_name}. Utilisation des paramètres par défaut.")

    # Condition spéciale pour les modèles qui ne prennent pas `random_state`
    if model_class in [LinearRegression, KNeighborsRegressor, SVR]:
        model = model_class()
    else:
        model = model_class(random_state=params.get("random_state"))

    grid_search = GridSearchCV(Pipeline([('model', model)]),
                               param_grid,
                               cv=params.get('cv', 3),
                               scoring=params.get('scoring', 'neg_mean_squared_error'),
                               n_jobs=-1)

    return model, grid_search, hyperparametres


# %%
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.ensemble import GradientBoostingRegressor as GBR
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor as DTR
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression

from torch import logdet
from xgboost import XGBRegressor
import numpy as np
import pandas as pd
import logging


def prediction_vent_avec_filtre_et_horaires(df_original, params):
    """
    Effectuer des prédictions de vitesse et de direction du vent à plusieurs horizons temporels.

    :param df_original: DataFrame contenant les données météorologiques historiques.
    :type df_original: pd.DataFrame
    :param params: Dictionnaire contenant les paramètres de configuration pour le modèle et la prédiction.
    :type params: dict
    :return: Liste des résultats de prédiction, chaque élément est un dictionnaire avec les détails et le score RMSE.
    :rtype: list

    >>> df_test = pd.DataFrame(...)  # DataFrame exemple
    >>> params_test = {...}  # Paramètres exemple
    >>> resultats = prediction_vent_avec_filtre_et_horaires(df_test, params_test)
    """
    resultats = []
    colonne_to_predict = params['colonne_to_predict']
    plages_mensuelles = params["plages_mensuelles"]
    plages_horaires = params["plages_horaires"]
    colonnes_possibles_a_supprimer = params["colonnes_possibles_a_supprimer"]
    heure_de_reference = params["heure_de_reference"]
    decalages_en_minutes = params["decalages_en_minutes"]
    df_name = params.get("df_name", "DataFrame")
    models_types = params.get('model_type', [LinearRegression])  # par defaut utilise la regression linéaire

    #Controle de la presence de la colonne à predire dans le dataset
    # Extraction de l'unité de la colonne à prédire pour les étiquettes des graphiques et le RMSE
    if colonne_to_predict not in df_original.columns:
        logger.error(f"La colonne à prédire '{colonne_to_predict}' n'est pas présente dans le DataFrame.")
        return []
    # unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''
    unite_colonne_to_predict = colonne_to_predict[colonne_to_predict.find('('):] if '(' in colonne_to_predict else ''
    # Logger les informations importantes
    logger.debug(f"Début de la fonction de prédiction pour la colonne: {colonne_to_predict}")
    i = 1
    logger.debug(f"\n test n°:\n{i} ")
    for model_class in models_types:

        ######################## appel fonction PREPARATION MODELES et GRID_SEARCH #####################
        model, grid_search, hyperparametres = prepare_modele_et_grid_search(model_class, params)
        model_name = model_class.__name__
        logger.debug(f"\n model:\n{model} ")
        logger.debug(f"\n grid_search:\n{grid_search} ")
        logger.debug(f"\n hyperparametres:\n{hyperparametres} ")
        ######################## fin appel fonction PREPARATION MODELES et GRID_SEARCH #####################

        ######### ITERATION SUR LES PLAGES MENSUELLES ############
        for plage_mensuelle in plages_mensuelles:
            logger.debug(f"\n plage_mensuelle:\n{plage_mensuelle} ")
            for plage_horaire in plages_horaires:
                logger.debug(f"\nplage_horaire :\n{plage_horaire} ")
                for colonnes_to_drop in colonnes_possibles_a_supprimer:
                    logger.debug(f"\n colonnes_to_drop:\n{colonnes_to_drop} ")
                    df = df_original.copy()
                    ######### PREPARATION df ############
                    df_prepared = preparer_donnees_pour_prediction_horaires(df, plage_mensuelle, plage_horaire, colonnes_to_drop, heure_de_reference,
                                                                            decalages_en_minutes, colonne_to_predict)
                    logger.debug(f"\n df_prepared:\n{df_prepared.head(2)} ")
                    logger.debug(f"\n liste colonnes:\n{df_prepared.columns.tolist()} ")

                    ######### TRAIN TEST SPLIT ############
                    if df_prepared.empty:
                        continue  # Skip si le df préparé est vide

                    # Séparation des datasets avec la fonction split_time_series
                    train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='index')
                    # train_data, val_data, test_data = split_time_series(df_prepared, train_size=0.7, val_size=0.25, date_column='date')

                    ######### ITERATION SUR LES COLONNES DECALLEES ############
                    for decalage in decalages_en_minutes:
                        logger.debug(f"\n decalage:\n{decalage} ")
                        nom_colonne_cible = f'{colonne_to_predict}_plus_{decalage}min'
                        # nom_colonne_cible = nom_colonne_decaled
                        logger.debug(f"\n nom_colonne_cible:\n{nom_colonne_cible} ")
                        # df[nom_colonne_cible] train_data[nom_colonne_cible] = train_data[colonne_to_predict].shift(-decalage)
                        X_train = train_data.drop([nom_colonne_cible], axis=1, errors='ignore')
                        y_train = train_data[nom_colonne_cible]
                        X_test = test_data.drop([nom_colonne_cible], axis=1, errors='ignore')
                        y_test = test_data[nom_colonne_cible]
                        logger.debug(f"\n X_train:\n{X_train} ")
                        logger.debug(f"\n y_train:\n{y_train} ")
                        logger.debug(f"\n X_test:\n{X_test} ")
                        logger.debug(f"\n y_test:\n{y_test} ")
                        # model = model
                        # model.fit(X_train, y_train)
                        # predictions = model.predict(X_test)
                        ###### ENTRAINNEMENT #######
                        # Entraînement et optimisation du modèle avec GridSearchCV
                        grid_search.fit(X_train, y_train)

                        # Meilleur modèle après GridSearch
                        best_model = grid_search.best_estimator_
                        logger.debug(f"\n best_model:\n{best_model} ")

                        ###### PREDICTIONS #######
                        # Prédiction sur l'ensemble de test avec le meilleur modèle
                        predictions = best_model.predict(X_test)
                        logger.debug(f"\n predictions:\n{predictions} ")
                        ######

                        # # Enregistrement des résultats avec détails des filtres
                        # details_filtres = f"{df_name} - Mois: {plage_mensuelle}, Heures: {plage_horaire}, Colonnes supprimées: {colonnes_to_drop}, Prédiction pour: +{decalage}min, Unité: {unite_colonne_to_predict}"
                        # resultats.append((rmse, details_filtres))
                        # Calcul des scores
                        mse = mean_squared_error(y_test, predictions)
                        rmse = np.sqrt(mse)
                        mae = mean_absolute_error(y_test, predictions)
                        r2 = r2_score(y_test, predictions)

                        # Stockage des résultats
                        resultats.append({
                            'df_name': df_name,
                            'model': model_name,
                            'rmse': rmse,
                            'unité': unite_colonne_to_predict,
                            'mae': mae,
                            'r2': r2,
                            'plage_mensuelle': plage_mensuelle,
                            'plage_horaire': plage_horaire,
                            'colonnes_supprimees': colonnes_to_drop,
                            'meilleurs_parametres': grid_search.best_params_,
                            'hyperparametres': hyperparametres
                        })

                        logger.debug(
                            f"\ntest:{i} - {df_name}-->  RMSE: {round(rmse,3)}{unite_colonne_to_predict}, MAE: {round(mae,3)}{unite_colonne_to_predict}, R2: {round(r2*100,3)}%, Meilleurs paramètres: {grid_search.best_params_}, hyperparametre: {hyperparametres} \n"
                        )
                        i += 1

                        # Log des résultats
                        # print(f"RMSE: {rmse}{unite_colonne_to_predict} - Filtres: {details_filtres}")
    return resultats


# %%
# dataframes_meteo_france_6_min_clean_sans_outlier


# %%
%%capture   captureSVR
# df = dataframes_meteo_france_6_min_clean_sans_outlier["df_station_13005003"]
liste_resultats = []


for df_name, df in dataframes_meteo_france_6_min_clean_sans_outlier.items():
    df = dataframes_meteo_france_6_min_clean_sans_outlier[df_name]
    df = df.copy()
    logger.debug(f"\n liste colonnes:\n{df.columns.tolist()} ")
    logger.debug(f"\n df:\n{df.head(2)} ")
    params = {
        "heure_de_reference":
        9,
        "decalages_en_minutes": [40, 120, 180],
        "colonne_to_predict":
        'vitesse_vent_(km/h)',
        # "colonne_to_predict": 'direction_(°)',
        "df_name":
        df_name,
        "plages_mensuelles": [[6, 7, 8, 9], [7, 8], [5, 6, 7, 8, 9, 10], [4, 5, 6, 7, 8, 9, 10]],
        "plages_horaires": [[8, 18], [7, 19], [9, 17], [10, 16], [6, 20], [0, 23]],
        "colonnes_possibles_a_supprimer": [
            ['précipitations_(mm)'],
            ['direction_(°)'],
            ['humidity_(%)'],
            ['temperature_(°C)'],
            ['précipitations_(mm)', 'direction_(°)'],
            ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'],
            []  # Aucune colonne supprimée
        ],
        # liste des modeles machine learning
        #     "model_type": [ KNeighborsRegressor],
        #     # "model_type": [RandomForestRegressor, LinearRegression, XGBRegressor, KNeighborsRegressor],
        #     # liste des hyperparamétres
        #     "model_params": {
        #         'RandomForestRegressor__n_estimators': [100, 200],
        #         'RandomForestRegressor__max_depth': [None, 10, 20],
        #         'LinearRegression__fit_intercept': [True, False],
        #         'XGBRegressor__learning_rate': [0.01, 0.1],
        #         'XGBRegressor__max_depth': [3, 5, 7],
        #         'KNeighborsRegressor__n_neighbors': [5, 10],
        #         'KNeighborsRegressor__weights': ['uniform', 'distance'],
        #         'cv': 3,
        #         'scoring': 'neg_mean_squared_error',
        #     },
        # "random_state":  42,
        # }
        # liste des modeles machine learning
        # "model_type": [RandomForestRegressor, LinearRegression, XGBRegressor, KNeighborsRegressor, SVR, GBR, DTR, ElasticNet, Ridge],
        "model_type": [SVR],
        # liste des hyperparamétres
        "model_params": {
            # MODELE D'ENSEMBLE
            # RandomForestRegressor modele d'ensemble d'arbres de décision, combine plusieurs arbres de décision
            'RandomForestRegressor__n_estimators': [100, 200],
            'RandomForestRegressor__max_depth': [None, 10, 20],
            # XGBRegressor modele ( Xgboost eXtreme Gradient Boosting) d'ensemble type gradient boosting,modele de régression non linéaire,
            # ajoute séquentiellement des modèles faibles, utilise une fonction de perte spécifique et une régularisation pour optimiser les performances du modèle.
            'XGBRegressor__learning_rate': [0.01, 0.1],
            'XGBRegressor__max_depth': [3, 5, 7],
            # modèle d'ensemble qui combine plusieurs arbres de régression
            'GBR__n_estimators': [50, 100, 200],
            'GBR__learning_rate': [0.01, 0.1, 0.2],
            'GBR__max_depth': [3, 5, 7],
            # CLUSTERING modele de régression non linéaire
            # KNeighborsRegressor Clustering modèle des k plus proches voisins (KNeighbors) prédiction non paramétrique
            'KNeighborsRegressor__n_neighbors': [5, 10],
            'KNeighborsRegressor__weights': ['uniform', 'distance'],
            # SVM apprentissage automatique, modele de régression non linéaire
            # Support Vector Regressor méthode de régression basée sur les machines à vecteurs de support (SVM)
            'SVR__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
            'SVR__C': [0.1, 1, 10],
            'SVR__epsilon': [0.1, 0.2, 0.5],
            #REGRESSION
            # Decision Tree Regressor modèle d'apprentissage automatique Modèle d'arbres de décision
            'DTR__max_depth': [None, 5, 10],
            'DTR__min_samples_split': [2, 5, 10],
            'DTR__min_samples_leaf': [1, 2, 4],
            #REGRESSION LINEAIRE
            # modele utilisant la regression linaire simple
            'LinearRegression__fit_intercept': [True, False],
            # modele utilisant la regression linaire regularisé avec penalité L2
            'Ridge__alpha': [0.1, 0.5, 1.0],
            'Ridge__fit_intercept': [True, False],
            'Ridge__solver': ['auto', 'svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga'],
            # modele utilisant la regression linaire regularisé avec penalité L1(lasso) et L2 (ridge)
            'ElasticNet__alpha': [0.1, 0.5, 1.0],
            'ElasticNet__l1_ratio': [0.1, 0.5, 0.9],
            'ElasticNet__fit_intercept': [True, False],
            'cv': 3,
            'scoring': 'neg_mean_squared_error',
        },
        "random_state":42,
    }
    name_tableau_resultat = f'score_RMSE_regression_lineaire_{df_name}'
    resultats = prediction_vent_avec_filtre_et_horaires(df, params)
    name_tableau_resultat = resultats
    liste_resultats.append(name_tableau_resultat)

# liste_resultats
resultats_meteo_france_6min_all_stations_vent_svr = liste_resultats
# 17h pour obtenir les resultats
# 600 min pour le test2


# %%
# resultats_meteo_france_6min_all_stations_vent_all_modeles=resultats_meteo_france_6min_all_stations_vent
# resultats_meteo_france_6min_all_stations_vent_all_modeles


# %%
# from collections import defaultdict
# def top3_resultats_modeles_par_modele(resultats):
#     """
#     Affiche les trois meilleurs ensembles de configurations pour chaque modèle utilisé,
#     basés sur le score RMSE moyen le plus bas, incluant également les scores MAE et R² ainsi que
#     les paramètres et hyperparamètres pour chaque ensemble, avec le nom de la station météo.
#     """
#     # Regroupement des résultats par modèle
#     resultats_par_modele = defaultdict(list)
#     for resultat in resultats:
#         for res in resultat:
#             modele = res['model']
#             resultats_par_modele[modele].append(res)

#     # Pour chaque modèle, sélectionner les 3 meilleures configurations basées sur le RMSE,
#     # et en cas d'égalité sur RMSE, utiliser MAE comme critère secondaire (favoriser le plus petit MAE)
#     for modele, res_modele in resultats_par_modele.items():
#         # Trier les configurations d'abord par RMSE croissant puis par MAE croissant
#         top3 = sorted(res_modele, key=lambda x: (x['rmse'], x['mae'],-x['r2']))[:3]

#         print(f"# Meilleurs ensembles de paramètres pour le modèle: {modele}")
#         for config in top3:
#             # Inclure le nom de la station météo dans les détails
#             print(f"## RMSE: {config['rmse']:.3f}, MAE: {config['mae']:.3f}, R2: {config['r2']*100:.3f}%, "
#                   f"Détails: Station: {config['df_name']}, Plage mensuelle: {config['plage_mensuelle']}, "
#                   f"Plage horaire: {config['plage_horaire']}, Colonnes supprimées: {config['colonnes_supprimees']}, "
#                   f"Paramètres: {config['meilleurs_parametres']}")
#         print("\n")




# %%
# resultats_meteo_france_6min_all_stations_vent_all_modeles


# %% [markdown]
# #### Extraction du top 3 de la liste des résultats

# %%
from collections import defaultdict


def top3_resultats_modeles_par_modele(resultats):
    """
    Affiche les trois meilleurs ensembles de configurations pour chaque modèle utilisé,
    basés sur le score RMSE moyen le plus bas, incluant également les scores MAE et R² ainsi que
    les paramètres et hyperparamètres pour chaque ensemble, avec le nom de la station météo.
    """
    # Regroupement des résultats par modèle
    resultats_par_modele = defaultdict(list)
    for groupe_resultat in resultats:
        for resultat in groupe_resultat:
            modele = resultat['model']
            resultats_par_modele[modele].append(resultat)

    # Pour chaque modèle, sélectionner les 3 meilleures configurations basées sur le RMSE,
    # le MAE, et favoriser le plus grand R² en cas d'égalité
    for modele, res_modele in resultats_par_modele.items():
        # Trier les configurations d'abord par RMSE croissant, puis par MAE croissant, et enfin par R² décroissant
        top3 = sorted(res_modele, key=lambda x: (x['rmse'], x['mae'], -x['r2']))[:3]

        print(f"# Meilleurs ensembles de paramètres pour le modèle: {modele}")
        for config in top3:
            # Inclure le nom de la station météo dans les détails
            print(f"## RMSE: {config['rmse']:.3f}, MAE: {config['mae']:.3f}, R2: {config['r2']*100:.3f}%, "
                  f"Détails: Station: {config.get('station_name', 'N/A')}, Plage mensuelle: {config.get('plage_mensuelle', 'N/A')}, "
                  f"Plage horaire: {config.get('plage_horaire', 'N/A')}, Colonnes supprimées: {config.get('colonnes_supprimees', 'N/A')}, "
                  f"Paramètres: {config.get('meilleurs_parametres', 'N/A')}")
        print("\n")


# %%
top3_resultats_modeles_par_modele(resultats_meteo_france_6min_all_stations_vent_svr)



# %%
top3_resultats_modeles_par_modele(resultats_meteo_france_6min_all_stations_vent_kneighbors)
# Meilleurs ensembles de paramètres pour le modèle: resultats_meteo_france_6min_all_stations_vent_all_modeles2
## RMSE: 1.078, MAE: 0.821, R2: 88.470%, Détails: Station: N/A, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Paramètres: {'model__n_neighbors': 10, 'model__weights': 'distance'}
## RMSE: 1.175, MAE: 0.939, R2: 95.685%, Détails: Station: N/A, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Paramètres: {'model__n_neighbors': 5, 'model__weights': 'distance'}
## RMSE: 1.198, MAE: 0.889, R2: 88.059%, Détails: Station: N/A, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Paramètres: {'model__n_neighbors': 5, 'model__weights': 'distance'}


# %%
top3_resultats_modeles_par_modele(resultats_meteo_france_6min_all_stations_vent_all_modeles)
# Meilleurs ensembles de paramètres pour le modèle: RandomForestRegressor
## RMSE: 1.109, MAE: 0.877, R2: 98.957%, Détails: Station: df_station_13054001, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [9, 17], Colonnes supprimées: ['précipitations_(mm)'], Paramètres: {}
## RMSE: 1.124, MAE: 0.887, R2: 98.929%, Détails: Station: df_station_13054001, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [9, 17], Colonnes supprimées: ['temperature_(°C)'], Paramètres: {}
## RMSE: 1.126, MAE: 0.897, R2: 98.926%, Détails: Station: df_station_13054001, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [9, 17], Colonnes supprimées: [], Paramètres: {}

# Meilleurs ensembles de paramètres pour le modèle: LinearRegression
## RMSE: 0.851, MAE: 0.660, R2: 98.435%, Détails: Station: df_station_13074003, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['humidity_(%)'], Paramètres: {}
## RMSE: 0.851, MAE: 0.660, R2: 98.435%, Détails: Station: df_station_13074003, Plage mensuelle: [7, 8], Plage horaire: [9, 17], Colonnes supprimées: ['humidity_(%)'], Paramètres: {}
## RMSE: 0.851, MAE: 0.654, R2: 98.435%, Détails: Station: df_station_13074003, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Paramètres: {}

# Meilleurs ensembles de paramètres pour le modèle: XGBRegressor
## RMSE: 1.180, MAE: 0.924, R2: 94.653%, Détails: Station: df_station_13091002, Plage mensuelle: [5, 6, 7, 8, 9, 10], Plage horaire: [9, 17], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Paramètres: {}
## RMSE: 1.191, MAE: 0.929, R2: 94.552%, Détails: Station: df_station_13091002, Plage mensuelle: [5, 6, 7, 8, 9, 10], Plage horaire: [9, 17], Colonnes supprimées: ['direction_(°)'], Paramètres: {}
## RMSE: 1.199, MAE: 0.916, R2: 98.781%, Détails: Station: df_station_13054001, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [9, 17], Colonnes supprimées: ['direction_(°)'], Paramètres: {}

#test du 10 avril 17h
# Meilleurs ensembles de paramètres pour le modèle: RandomForestRegressor
## RMSE: 0.977, MAE: 0.754, R2: 90.538%, Détails: Station: df_station_13022003, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)'], Paramètres: {'model__max_depth': 10, 'model__n_estimators': 200}
## RMSE: 0.978, MAE: 0.752, R2: 90.513%, Détails: Station: df_station_13022003, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: [], Paramètres: {'model__max_depth': 10, 'model__n_estimators': 200}
## RMSE: 0.983, MAE: 0.751, R2: 90.416%, Détails: Station: df_station_13022003, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['temperature_(°C)'], Paramètres: {'model__max_depth': 10, 'model__n_estimators': 200}

# Meilleurs ensembles de paramètres pour le modèle: LinearRegression
## RMSE: 0.799, MAE: 0.620, R2: 98.110%, Détails: Station: df_station_13074003, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['humidity_(%)'], Paramètres: {'model__fit_intercept': False}
## RMSE: 0.799, MAE: 0.621, R2: 98.107%, Détails: Station: df_station_13074003, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Paramètres: {'model__fit_intercept': True}
## RMSE: 0.800, MAE: 0.621, R2: 98.105%, Détails: Station: df_station_13074003, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: [], Paramètres: {'model__fit_intercept': False}

# Meilleurs ensembles de paramètres pour le modèle: XGBRegressor
## RMSE: 0.990, MAE: 0.769, R2: 90.282%, Détails: Station: df_station_13022003, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: [], Paramètres: {}
## RMSE: 1.040, MAE: 0.798, R2: 89.281%, Détails: Station: df_station_13022003, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['temperature_(°C)'], Paramètres: {}
## RMSE: 1.046, MAE: 0.790, R2: 89.138%, Détails: Station: df_station_13022003, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)'], Paramètres: {}

# autre methode pour faire le trie ds résultats
# Meilleurs ensembles de paramètres pour le modèle: RandomForestRegressor
## RMSE: 0.977, MAE: 0.754, R2: 90.538%, Détails: Station: N/A, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)'], Paramètres: {'model__max_depth': 10, 'model__n_estimators': 200}
## RMSE: 0.978, MAE: 0.752, R2: 90.513%, Détails: Station: N/A, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: [], Paramètres: {'model__max_depth': 10, 'model__n_estimators': 200}
## RMSE: 0.983, MAE: 0.751, R2: 90.416%, Détails: Station: N/A, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['temperature_(°C)'], Paramètres: {'model__max_depth': 10, 'model__n_estimators': 200}

# Meilleurs ensembles de paramètres pour le modèle: LinearRegression
## RMSE: 0.799, MAE: 0.620, R2: 98.110%, Détails: Station: N/A, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['humidity_(%)'], Paramètres: {'model__fit_intercept': False}
## RMSE: 0.799, MAE: 0.621, R2: 98.107%, Détails: Station: N/A, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)', 'direction_(°)', 'humidity_(%)', 'temperature_(°C)'], Paramètres: {'model__fit_intercept': True}
## RMSE: 0.800, MAE: 0.621, R2: 98.105%, Détails: Station: N/A, Plage mensuelle: [7, 8], Plage horaire: [8, 18], Colonnes supprimées: [], Paramètres: {'model__fit_intercept': False}

# Meilleurs ensembles de paramètres pour le modèle: XGBRegressor
## RMSE: 0.990, MAE: 0.769, R2: 90.282%, Détails: Station: N/A, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: [], Paramètres: {}
## RMSE: 1.040, MAE: 0.798, R2: 89.281%, Détails: Station: N/A, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['temperature_(°C)'], Paramètres: {}
## RMSE: 1.046, MAE: 0.790, R2: 89.138%, Détails: Station: N/A, Plage mensuelle: [6, 7, 8, 9], Plage horaire: [8, 18], Colonnes supprimées: ['précipitations_(mm)'], Paramètres: {}


# %% [markdown]
# ##### sauvegarde des resultats

# %%
# path=path_sauve_modeles_meteo_france_6min
# liste_resultats
# liste_model = [
#     liste_resultats2, resultats, resultats_meteo_france_6min_all_stations, resultats_meteo_france_6min_all_stations_vent,
#     resultats_meteo_france_6min_all_stations_direction
# ]
# liste_name_model = [
#     "liste_resultats2", "resultats", "resultats_meteo_france_6min_all_stations", "resultats_meteo_france_6min_all_stations_vent",
#     "resultats_meteo_france_6min_all_stations_direction"
# ]
# for model in liste_model:
#     # logger.debug(f"\n model:\n{model} ")
#     for model_name in liste_name_model:
#         # logger.debug(f"\n model_name:\n{model_name} ")
#         model=pd.DataFrame(model)
#         # Correction et construction des chemins de fichier
#         file_basename = os.path.join(path, f"{model_name}").replace('\\', '/')
#         # Créer le dossier si nécessaire
#         # os.makedirs(os.path.dirname(file_basename), exist_ok=True)
#         model.to_pickle(f"{file_basename}.pkl")
#         # save_dataframe(model, model_name,path)
#         logger.info(f"\n le model {model.info()} est sauvegardé sous le nom \n{model_name} dans le repertoire \n{path}")


# %% [markdown]
# ##### charge les resultats

# %%
# path = path_sauve_modeles_meteo_france_6min


# liste_name_model = [
#     "liste_resultats2", "resultats", "resultats_meteo_france_6min_all_stations", "resultats_meteo_france_6min_all_stations_vent",
#     "resultats_meteo_france_6min_all_stations_direction"
# ]

# for model_name in liste_name_model:
#     # logger.debug(f"\n model_name:\n{model_name} ")
#     model = pd.DataFrame(model)
#     # Correction et construction des chemins de fichier
#     file_basename = os.path.join(path, f"{model_name}.pkl").replace('\\', '/')
#     # logger.debug(f"\n file_basename:\n{file_basename} ")
#     model_name = pd.read_pickle(file_basename)
#     logger.info(f"\n le model {model.info()} est chargé sous le nom \n{model_name} depuis le repertoire \n{path}")
# # projet_meteo\Projet_Meteo\Modeles\sauvegarde_modeles\model_meteo_france_6min


# %% [markdown]
# #####  sauve charge model pickle avec une seule fonction

# %%


# %%
from sauve_charge_df_csv_json_pkl import sauve_charge_pickle

# sauve résultats modele
path = path_sauve_modeles_meteo_france_6min
model_name = "resultats_meteo_france_6min_all_stations_vent_svr"
path = os.path.join(path, f"{model_name}.pkl").replace('\\', '/')
name_file = resultats_meteo_france_6min_all_stations_vent_svr
sauve_charge_pickle(path, name_file=name_file, true_for_load=False, is_file=True)

#charge tous les modeles du repertoire
path = path_sauve_modeles_meteo_france_6min
# sauve_charge_pickle(path, name_file=None,true_for_load=True, is_file=False)
# print(path)

#charge un modele
model_name = "resultats_meteo_france_6min_all_stations_vent_all_modeles2"
path = os.path.join(path, f"{model_name}.pkl").replace('\\', '/')

# resultats_meteo_france_6min_all_stations_vent_all_modeles=sauve_charge_pickle(path, name_file=None,true_for_load=True, is_file=True)

# print(path)


# %%
resultats_meteo_france_6min_all_stations_vent.info()


# %% [markdown]
# ## SARIMAX

# %% [markdown]
# ###  Prunage ACP des df
#
# Le prunage, est une technique pour optimiser les modèles d'arbres de décision. L'Analyse en Composantes Principales (ACP), en revanche, est une méthode statistique qui transforme les données en composantes orthogonales de manière à réduire le nombre de variables et à mettre en évidence les plus significatives, utilisée pour l'analyse de données et la visualisation

# %% [markdown]
#

# %%
df_meteo_france_13009 = load_dataframe("01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59_1", path_data_meteo_france_upload_data_depuis_api, format_type='csv', sep=";")


# %%
df_meteo_france_13009


# %%
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif


def prunage_df(data, colonne='vitesse_(km/h)', acp_component=2, k=6):
    """
    Applique PCA pour réduire la dimensionnalité des données et utilise SelectKBest pour identifier les caractéristiques les plus informatives.
    Applique PCA et SelectKBest pour réduire la dimensionnalité des données
    et comparer les méthodes basées sur la variance expliquée et les scores ANOVA F-value.


    :param data: DataFrame contenant les données.
    :param colonne: Nom de la colonne cible pour SelectKBest.
    :k nombre de k paramétres pour selectkBest
    :return: None
    """
    selected_features = []  # Initialisez à une liste vide
    scores = []  # Initialisez à une liste vide
    # faire une copie du dataframe
    data=data.copy()
    try:
        # Liste des colonnes à supprimer
        cols_to_drop = ['station', 'POSTE', 'DATE']
        # Supprimer les colonnes de la liste si elles existent dans le DataFrame
        data.drop(columns=[col for col in cols_to_drop if col in data.columns], inplace=True)

        # Vérifier si 'date' est dans les colonnes et la convertir en datetime
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)
        logger.debug(f" colonnes aprés suppresiions {df.columns.tolist()}")

        # Ajuster n_components pour PCA et k pour SelectKBest selon le nombre de colonnes
        n_cols = data.shape[1] - 1  # Exclure la colonne cible
        n_component_max = min(n_cols, 10)  # PCA n_components ne doit pas dépasser le nombre de colonnes
        n_component_min=2
        n_component = max(n_component_min, min(acp_component, n_component_max))
        logger.debug(f"n_component :{n_component}")


        k_min = 2  # SelectKBest k  doit avoir une taille mini de 2
        k_max = min(k, n_cols - 1)  # SelectKBest k ne doit pas dépasser le nombre de colonnes - 1
        # k=k_min if k < k_min else k
        # k=k_max if k> k_max else k
        k = max(k_min, min(k, k_max))
        logger.debug(f"k :{k}")
        # ACP
        # Suppression de la colonne cible des données pour PCA
        data_for_pca = data.drop(columns=[colonne])

        # Création et ajustement du modèle PCA
        pca = PCA(n_components=n_component)
        pca.fit(data_for_pca)
        pca_variance_explained = pca.explained_variance_ratio_
        # Affichage des résultats
        variance_list_ACP = []
        logger.info("PCA Variance Explained:")
        for i, variance in enumerate(pca_variance_explained, 1):
            variance_list_ACP.append(variance)
            logger.info(f"PC{i}: {variance:.4f}")

        # SELECTKBEST
        # Préparation des données pour SelectKBest
        X = data.drop(columns=[colonne])
        y = data[colonne]

        # Calcul des scores ANOVA F-value avec SelectKBest
        kbest = SelectKBest(score_func=f_classif, k=k)
        kbest.fit(X, y)

        # Affichage des noms des colonnes des caractéristiques sélectionnées
        selected_features = X.columns[kbest.get_support()]
        scores = kbest.scores_[kbest.get_support()].tolist()

        # logger.debug("Noms des features sélectionnées :", selected_features.tolist())
        logger.debug(f"Noms des features sélectionnées :{selected_features}" )


        # Affichage des scores d'information pour les caractéristiques sélectionnées
        logger.debug(f"Scores d'information pour les features sélectionnées : {scores}" )
        # logger.debug("Scores d'information pour les features sélectionnées :", kbest.scores_[kbest.get_support()].tolist())

    except Exception as e:
        logger.error(f"Une erreur est survenue : {e}")
        # Ici, retourner selected_features et scores même s'ils sont vides
        # assure que la fonction se termine proprement sans erreurs de référence non définie
        return selected_features, scores
    # liste_col = selected_features.tolist()

    return variance_list_ACP,selected_features, scores


# %% [markdown]
# ### prunage de mobilis

# %%

# test

data=df_clean_7col
# Noms des features sélectionnées : ['humidity_(%)', 'temperature_(°C)', 'direction_(°)', 'rafale_(km/h)']
# Scores d'information pour les features sélectionnées : [2.3274957137516807, 1.7501298686799882, 2.052926112796495, 382.22239124091436]
data=df_clean_12col
# Noms des features sélectionnées : ['wave_amplitude_(m)', 'direction_(°)', 'rafale_(km/h)', 'vitesse_surface_(km/h)']
# Scores d'information pour les features sélectionnées : [3.6220416671023536, 1.7338180629993725, 199.59388346579624, 1.7723010749662798]


# data="C:\programmation\IA\Projet_Meteo\projet_meteo\Projet_Meteo\Datasets\meteo_france\upload_dataset_depuis_api\13001009\horaire\01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59\01-Jan-2004_at_00h00_to_31-Dec-2004_at_23h59_1.csv"
# data=df_clean_7col
data=df
prunage_df(data,colonne='vitesse_(km/h)')


# %% [markdown]
# ### prunage meteo france

# %% [markdown]
# traite les colonnes du df de meteo france, en faisant une colonne moyenne pour la vitesse, direction, temeprature, humidité
#
# Supprime la colonne station, mais la date au format datetime et en index

# %%
df = df_13005003_01jan2014_01mar2024.copy()
# Convertir la colonne 'date' en datetime si ce n'est pas déjà fait
# df['date'] = pd.to_datetime(df['date'])
# Définir la colonne 'date' comme nouvel index du DataFrame
# df.set_index('date', inplace=True)


# %%
import pandas as pd
import numpy as np




# df = df_13005003_01jan2014_01mar2024.copy()
# Convertir la colonne 'date' en datetime si ce n'est pas déjà fait
# df['date'] = pd.to_datetime(df['date'])
# Définir la colonne 'date' comme nouvel index du DataFrame
# df.set_index('date', inplace=True)

df.columns.tolist()
logger.debug(f"colonnes  {df.columns.tolist()}")
# df.head(2)
# df.info()
df = df.dropna()
# df.info()

cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
# ______________________________
#test avec les colonnes moyennées
# ______________________________
# # La colonne d'intérêt
col_interet = 'vitesse_vent_moyen_at_1_m_(km/h)'
#on ne garde qu'une seule colonne vitesse, celle à predire
# retirer les autres colonnes de vitesse du vent
cols_a_conserver = [col for col in cols_num if "vitesse" not in col or col == col_interet]
logger.debug(f"cols_a_conserver  {cols_a_conserver}")
# lancement fonction
variance_list_ACP1, selected_features1, scores1 = prunage_df(df[cols_a_conserver], colonne=col_interet, acp_component=2, k=2)
logger.warning(f"\n variance_list_ACP1:\n{variance_list_ACP1} \n")
logger.warning(f"\n liste_col1:\n{selected_features1} \n")
logger.warning(f"\n scores1:\n{scores1} \n")

# ______________________________
#test avec les colonnes moyennées
# ______________________________
# Filtrer les colonnes: inclure toutes les colonnes numériques sauf celles contenant "vitesse", sauf la colonne d'intérêt
cols_vitesse = [col for col in cols_num if "vitesse"  in col.lower() ]
cols_humidity = [col for col in cols_num if "humidi" in col.lower()]
cols_temperature = [col for col in cols_num if "temp" in col.lower()]
cols_direction = [col for col in cols_num if "direction" in col.lower()]
cols_heure = [col for col in cols_num if "heure" in col.lower()]

logger.debug(f"cols_humidity :\n{cols_humidity} \n")
logger.debug(f" cols_temperature:\n{cols_temperature} \n")
logger.debug(f" cols_vitesse:\n{cols_vitesse} \n")
logger.debug(f"cols_direction:\n{cols_direction} \n")

# Création des colonnes moyennes pour chaque catégorie
if cols_humidity:  # Vérification si la liste n'est pas vide
    df['mean_humidity'] = df[cols_humidity].mean(axis=1)
if cols_temperature:
    df['mean_temperature'] = df[cols_temperature].mean(axis=1)
if cols_direction:
    df['mean_direction'] = df[cols_direction].mean(axis=1)
if cols_vitesse:
    df['mean_vitesse'] = df[cols_vitesse].mean(axis=1)

# Suppression des colonnes qui ont servi à calculer les moyennes
df.drop(columns=cols_humidity + cols_temperature + cols_direction + cols_vitesse + cols_heure, inplace=True)
logger.debug(f"colonnes  {df.columns.tolist()}")
# selection des colonnes
cols_num_to_conserved = df.select_dtypes(include=[np.number]).columns.tolist()
logger.debug(f"cols_a_conserver  {cols_num_to_conserved}")

# La colonne d'intérêt
col_interet = "mean_vitesse"
# lancement fonction
variance_list_ACP, selected_features, scores = prunage_df(df[cols_num_to_conserved], colonne=col_interet, acp_component=2, k=2)

logger.warning(f"\n variance_list_ACP:\n{variance_list_ACP} \n")
logger.warning(f"\n liste_col:\n{selected_features} \n")
logger.warning(f"\n scores:\n{scores} \n")
# Vitesse du vent à 1m (km/h)


# %% [markdown]
# ## Analyse preliminaire PACF

# %%
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import pandas as pd


def analyse_preliminaire_series_temporelles(data, freq='M'):
    """
    Effectue une analyse préliminaire d'une série temporelle.

    :param data: Series pandas contenant les données de série temporelle.
    :param freq: La fréquence de la série temporelle (ex. 'M' pour mensuelle, 'Q' pour trimestrielle).
    """
    data=data.copy()


    # # Assurer que l'index est de type datetime
    # if not isinstance(data.index, pd.DatetimeIndex):
    #     # Vérifier si 'date' est dans les colonnes et la convertir en datetime
    #     if 'date' in data.columns:
    #         data['date'] = pd.to_datetime(data['date'])
    #         data.set_index('date', inplace=True)
    #     else:
    #         raise logger.error("L'index du DataFrame doit être de type pd.DatetimeIndex.")

    # # Liste des colonnes à supprimer
    # cols_to_drop = ['station', 'POSTE', 'DATE']
    # # Supprimer les colonnes de la liste si elles existent dans le DataFrame
    # data.drop(columns=[col for col in cols_to_drop if col in data.columns], inplace=True)

    # Tracé de la série temporelle
    plt.figure(figsize=(14, 7))
    plt.plot(data)
    plt.title('Série Temporelle')
    plt.xlabel('Temps')
    plt.ylabel('Valeurs')
    plt.show()

    # Décomposition saisonnière
    decomposition = seasonal_decompose(data, model='additive', period=freq)
    decomposition.plot()
    plt.show()

    # Fonction d'autocorrélation (ACF)
    plt.figure(figsize=(14, 7))
    plot_acf(data, lags=40)
    plt.title('Autocorrélation (ACF)')
    plt.show()

    # Fonction d'autocorrélation partielle (PACF)
    plt.figure(figsize=(14, 7))
    plot_pacf(data, lags=40, method='ywm')
    plt.title('Autocorrélation Partielle (PACF)')
    plt.show()


# test
# 'data' est une Series pandas avec un index DatetimeIndex
# data=mon_df
# analyse_preliminaire_series_temporelles(data, freq=12) # pour une série temporelle mensuelle


# %%
df=mon_df.copy()
df.columns.tolist()
# ['station',
#  'date',
#  'précipitation_1_heures_(mm)',
#  'température_(°C)',
#  'température_point_de_rosée_(°C)',
#  'température_mini_(°C)',
#  'heure_tps_mini',
#  'température_maxi_(°C)',
#  'heure_tps_max',
#  'durée_gel_(mn)',
#  'température_mini_à_10cm_(°C)',
#  'vent_moyen_à_1_m_(m/s)',
#  'Direction',
#  'vent_max_à_10_m_(m/s)',
#  'direction_vent_max_à_10m',
#  'heure_vent_max_à_10m',
#  'vent_max(m/s)',
#  'direction_vent_max',
#  'heure_vent_max',
#  'humidité_(%)',
#  'humidité_mini(%)',
#  'heure_humidité',
#  'humidité_max_(%)',
#  'heure_humidité_max_(%)',
#  'humidité_absolue_2_m_(%)',
#  'humidité_sup_a_40%_(%)',
#  'humidité_sup_a_80%_(%)',
#  'température_sol_(°C)',
#  'Enthalpie_énergie_totale_système_atmosphérique']


# %%
# analyse_preliminaire_series_temporelles(df["vitesse_(km/h)"], freq=1)
# df = df_13001009_01jan2014_01mar2024.copy()
col = df["vitesse_vent_moyen_at_1_m_(km/h)"]

# Forward Fill
# col.fillna(method='ffill', inplace=True)
col.ffill(inplace=True)

# Backward Fill
# col.fillna(method='bfill', inplace=True)
col.bfill(inplace=True)
# Interpolation
col.interpolate(inplace=True)

print(f"\n colonnes :{df.columns.tolist()}")
analyse_preliminaire_series_temporelles(col, freq=1)


# %% [markdown]
# ### test de stationnarité par Dickey-Fuller

# %%
from statsmodels.tsa.stattools import adfuller


def tester_stationnarite(serie):
    """
    Teste la stationnarité d'une série temporelle.

    :param serie: Pandas Series contenant les données temporelles.
    :return: Résultats du test ADF, y compris la statistique de test, la valeur p, et les valeurs critiques.
    """
    resultat_adf = adfuller(serie)
    print('Statistique ADF : %f' % resultat_adf[0])
    print('Valeur-p : %f' % resultat_adf[1])
    print('Valeurs Critiques :')
    for cle, valeur in resultat_adf[4].items():
        print('\t%s: %.3f' % (cle, valeur))

    if resultat_adf[1] > 0.05:
        print(f"La série n'est pas stationnaire. car p= {resultat_adf[1]:.3%} est > à 0.05")
    else:
        print(f"La série est stationnaire, car p= {resultat_adf[1]:.3%} est < à 0.05")


# %%
# serie_a_tester = df_sans_outlier['vitesse_(km/h)']
# tester_stationnarite(serie_a_tester)


# %%
# serie_a_tester = df_sans_outlier['rafale_(km/h)']
# tester_stationnarite(serie_a_tester)


# %%
for col in df.select_dtypes(include=[np.number]).columns:
    print(f"Testing stationarity for column: {col}")
    serie_a_tester = df[col]
    tester_stationnarite(serie_a_tester)
    print("\n")


# %%
df = df_13001009_01jan2014_01mar2024.copy()
col = df["vitesse_vent_moyen_at_1_m_(km/h)"]

# Liste des colonnes à supprimer
cols_to_drop = ['station', 'POSTE', 'series_name']

# Supprimer les colonnes de la liste si elles existent dans le DataFrame
df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)

#suppression des na
df=df.dropna()

# Vérifier si 'date' est dans les colonnes et la convertir en datetime
if 'date' in data.columns:
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
logger.debug(f" colonnes aprés suppresiions {df.columns.tolist()}")

# Forward Fill Example:
col.fillna(method='ffill', inplace=True)
# Backward Fill Example:
col.fillna(method='bfill', inplace=True)
# Interpolation Example:
col.interpolate(inplace=True)
print(f"\n colonnes :{df.columns.tolist()}")

for col in df.select_dtypes(include=[np.number]).columns:
    print(f"Testing stationarity for column: {col}")
    serie_a_tester = df[col]
    tester_stationnarite(serie_a_tester)
    print("\n")


# %% [markdown]
# ### Analyse graphique de la stationarité

# %%
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# Créer les subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Tracer l'ACF
plot_acf(df['vitesse_(km/h)'], lags=30, zero=True, ax=ax1)
ax1.set_title('ACF - Vitesse du vent')
ax1.set_xlabel('Lag')
ax1.set_ylabel('Corrélation')
ax1.grid(True)

# Ajuster les graduations sur l'axe x pour l'ACF
ax1.set_xticks(np.arange(0, 31, 1))

# Tracer le PACF
plot_pacf(df['vitesse_(km/h)'], lags=30, zero=True, ax=ax2)
ax2.set_title('PACF - Vitesse  du vent')
ax2.set_xlabel('Lag')
ax2.set_ylabel('Corrélation partielle')
ax2.grid(True)

# Ajuster les graduations sur l'axe x pour le PACF
ax2.set_xticks(np.arange(0, 31, 1))

# Ajuster les subplots
plt.tight_layout()

# Afficher le graphique
plt.show()


# %% [markdown]
# ### Rendre si necessaire la serie stationnaire par différenciation

# %%
def rendre_stationnaire(serie):
    """
    Rend une série temporelle stationnaire par différenciation.

    :param serie: Pandas Series contenant les données temporelles.
    :return: Série temporelle différenciée.
    """
    return serie.diff().dropna()


# %%
df2 = rendre_stationnaire(df.select_dtypes(include=[np.number]))


# %% [markdown]
# ### Train test pour série temporelle

# %%
import pandas as pd
import numpy as np


def split_time_series(data, train_size=0.7, val_size=0.25, date_column='date'):
    """
    Divise les données de série temporelle en ensembles d'entraînement, de validation et de test
    basés sur des proportions spécifiques, après avoir converti la colonne de date spécifiée en datetime
    et l'avoir définie comme index si nécessaire. Inclut la journalisation des tailles des ensembles.

    :param data: DataFrame pandas contenant la série temporelle.
    :param train_size: Proportion de l'ensemble d'entraînement.
    :param val_size: Proportion de l'ensemble de validation.
    :param date_column: Nom de la colonne de date à convertir et à utiliser comme index.
    :return: Trois DataFrames pour l'entraînement, la validation et le test.
    """
    # Vérification et ajustement de l'index
    if not isinstance(data.index, pd.DatetimeIndex):
        if date_column in data.columns:
            data[date_column] = pd.to_datetime(data[date_column])
            data.set_index(date_column, inplace=True)
        else:
            logger.error(f"La colonne spécifiée '{date_column}' n'existe pas dans le DataFrame."    )
            raise ValueError( f"La colonne spécifiée '{date_column}' n'existe pas dans le DataFrame."  )

    if train_size + val_size >= 1:
        logger.error("La somme des tailles d'entraînement et de validation doit être inférieure à 1." )
        raise ValueError("La somme des tailles d'entraînement et de validation doit être inférieure à 1.")

    # Calcul des indices de coupure
    n = len(data)
    train_end = int(n * train_size)
    val_end = int(n * (train_size + val_size))

    # Division des données
    train_data = data.iloc[:train_end]
    val_data = data.iloc[train_end:val_end]
    test_data = data.iloc[val_end:]

    # Journalisation des tailles des ensembles
    logger.info(f"Taille de l'ensemble d'entraînement : {len(train_data)}")
    logger.info(f"Taille de l'ensemble de validation : {len(val_data)}")
    logger.info(f"Taille de l'ensemble de test : {len(test_data)}")

    return train_data, val_data, test_data


# Exemple d'utilisation:
# Assurez-vous de remplacer 'votre_fichier.csv' et 'date' par vos propres valeurs
# data = pd.read_csv('votre_fichier.csv')
# train_data,


# %%
df


# %%
# df['date'] = pd.to_datetime(df['date'])
# df.set_index('date', inplace=True)
train_data, val_data, test_data = split_time_series(df,
                                                    train_size=0.7,
                                                    val_size=0.2,
                                                    date_column='date')


# %%
train_data


# %%
val_data


# %%
test_data


# %% [markdown]
# ### Méthodologie Box-Jenkins pour ARIMA
# La méthodologie Box-Jenkins implique l'identification, l'estimation et la vérification des modèles ARIMA.
#
# Identification des ordres:
# - p (AR),
# - d (différenciation),
# - q (MA) à l'aide des graphiques ACF (AutoCorrelation Function) et PACF (Partial AutoCorrelation Function).

# %%
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def identifier_parametres_arima(serie):
    """
    Identifie visuellement les paramètres ARIMA d'une série temporelle.

    :param serie: Pandas Series stationnaire.
    """
    plt.figure(figsize=(10, 6))
    plt.subplot(211)
    plot_acf(serie, ax=plt.gca(), lags=40)
    plt.subplot(212)
    plot_pacf(serie, ax=plt.gca(), lags=40)
    plt.show()


# %%
identifier_parametres_arima(train_data["vitesse_(km/h)"])


# %%
identifier_parametres_arima(train_data["direction_(°)"])


# %% [markdown]
# ### pipeline SARIMAX

# %%
from statsmodels.tsa.statespace.sarimax import SARIMAX


def pipeline_sarimax(data, ordre, saisonnalite):
    """
    Crée un pipeline pour trouver les hyperparamètres du modèle SARIMAX.

    :param data: DataFrame ou Series contenant les données.
    :param ordre: Tuple représentant l'ordre (p, d, q) du modèle ARIMA.
    :param saisonnalite: Tuple représentant la saisonnalité (P, D, Q, S).
    :return: Modèle SARIMAX ajusté.
    """
    model = SARIMAX(data, order=ordre, seasonal_order=saisonnalite)
    result = model.fit()
    return result


# %%
# result = pipeline_sarimax(
#     df,
#     (),
# )


# %%
import itertools
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings


def recherche_hyperparametres_sarimax(data, p_range, d_range, q_range,
                                      s_range):
    """
    Recherche les meilleurs hyperparamètres pour le modèle SARIMAX.
    """
    meilleurs_resultats = float("inf")
    meilleurs_parametres = None  # Initialisez à None

    pdq_combinations = list(itertools.product(p_range, d_range, q_range))
    saisonnalite_combinations = [(x[0], x[1], x[2], s)
                                 for x in pdq_combinations for s in s_range]

    for parametres in pdq_combinations:
        for parametres_saisonnalite in saisonnalite_combinations:
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    model = SARIMAX(data,
                                    order=parametres,
                                    seasonal_order=parametres_saisonnalite)
                    result = model.fit()

                if result.aic < meilleurs_resultats:
                    meilleurs_resultats = result.aic
                    meilleurs_parametres = (parametres,
                                            parametres_saisonnalite)

                logger.info(f'ARIMA{parametres}x{  parametres_saisonnalite} - AIC:{result.aic}'                )

            except Exception as e:
                continue

    # Vérification si les meilleurs paramètres ont été trouvés
    if meilleurs_parametres is not None:
        logger.info(f'Meilleur modèle: ARIMA{meilleurs_parametres[0]}x{meilleurs_parametres[1]} - AIC: {meilleurs_resultats}' )
        return SARIMAX(data,
                       order=meilleurs_parametres[0],
                       seasonal_order=meilleurs_parametres[1]).fit()
    else:
        print("Aucun modèle n'a pu être ajusté avec les paramètres fournis.")
        return None


# # Exemple d'utilisation
# data = train_data['vitesse_(km/h)']
# meilleurs_modele = recherche_hyperparametres_sarimax(data, p_range=[0, 1, 2], d_range=[0, 1], q_range=[0, 1, 2], s_range=[0, 12])


# %%
# Exemple d'utilisation
data = train_data['vitesse_(km/h)']
# meilleurs_modele = recherche_hyperparametres_sarimax(data,
                                                    #  p_range=[0, 1, 2],
                                                    #  d_range=[0, 1],
                                                    #  q_range=[0, 1, 2],
                                                    #  s_range=[0, 12])
#  résultat en 98 min
# Meilleur modèle: ARIMA(2, 1, 1)x(0, 0, 0, 0) - AIC: 42566.484576861214


# %%
data = train_data['vitesse_(km/h)']
# meilleurs_modele = recherche_hyperparametres_sarimax(data,
                                                    #  p_range=[3, 4, 5],
                                                    #  d_range=[0, 1],
                                                    #  q_range=[3, 4, 5],
                                                    #  s_range=[0, 6])

# 688 min
# ARIMA(5, 1, 5)x(5, 1, 5, 6) - AIC:42639.36229136215
# Meilleur modèle: ARIMA(4, 0, 5)x(4, 1, 4, 6) - AIC: 42571.929467473594


# %%
train_data


# %% [markdown]
# ### fonction qui affiche les graphiques liés au modèle SARIMAX,
# dont:
#  - les scores du modèle et
#  - les graphiques ACF (Autocorrelation Function)
#  - PACF (Partial Autocorrelation Function),
#
# Cette fonction suppose le modèle SARIMAX soit déja ajusté

# %%
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def afficher_diagnostics_sarimax(modele, lags=40):
    """
    Affiche les diagnostics d'un modèle SARIMAX, incluant le score AIC,
    ainsi que les graphiques ACF et PACF des résidus.

    :param modele: le modèle SARIMAX ajusté.
    :param lags: le nombre de retards à inclure dans les graphiques ACF et PACF.
    """
    # Affichage du score AIC
    print(f"Score AIC: {modele.aic}")

    # Extraction des résidus
    residus = modele.resid

    # Création de la figure pour les graphiques
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # Graphique ACF
    plot_acf(residus, lags=lags, ax=axes[0])
    axes[0].set_title("Autocorrelation Function")

    # Graphique PACF
    plot_pacf(residus, lags=lags, ax=axes[1], method='ywm')
    axes[1].set_title("Partial Autocorrelation Function")

    # Afficher les graphiques
    plt.tight_layout()
    plt.show()


# Exemple d'utilisation:
# modele_sarimax = SARIMAX(...).fit()
# afficher_diagnostics_sarimax(modele_sarimax)


# %%
meilleur_modele = SARIMAX(df['vitesse_(km/h)'],
                          order=(2, 1, 1),
                          seasonal_order=(0, 0, 0, 0),
                          enforce_stationarity=False,
                          enforce_invertibility=False)

resultats = meilleur_modele.fit()
afficher_diagnostics_sarimax(resultats)


# %%
meilleur_modele = SARIMAX(df['direction_(°)'],
                          order=(2, 1, 1),
                          seasonal_order=(0, 0, 0, 0),
                          enforce_stationarity=False,
                          enforce_invertibility=False)

resultats = meilleur_modele.fit()
afficher_diagnostics_sarimax(resultats)


# %% [markdown]
# ## Approche par ARIMA car il semble que nous n'ayons pas de saisonnalité dans le df

# %%
import itertools
from statsmodels.tsa.arima.model import ARIMA
import warnings


def recherche_hyperparametres_arima(data, p_range, d_range, q_range):
    """
    Recherche les meilleurs hyperparamètres pour le modèle ARIMA.
    """
    meilleurs_resultats = float("inf")
    meilleurs_parametres = None  # Initialisez à None

    pdq_combinations = list(itertools.product(p_range, d_range, q_range))

    for parametres in pdq_combinations:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                model = ARIMA(data, order=parametres)
                result = model.fit()

            if result.aic < meilleurs_resultats:
                meilleurs_resultats = result.aic
                meilleurs_parametres = parametres

            print(f'ARIMA{parametres} - AIC:{result.aic}')

        except Exception as e:
            continue

    # Vérification si les meilleurs paramètres ont été trouvés
    if meilleurs_parametres is not None:
        print(f'Meilleur modèle: ARIMA{meilleurs_parametres} - AIC: {meilleurs_resultats}' )
        return ARIMA(data, order=meilleurs_parametres).fit()
    else:
        print("Aucun modèle n'a pu être ajusté avec les paramètres fournis.")
        return None


# Exemple d'utilisation
# Assurez-vous que train_data est votre DataFrame et 'vitesse_(km/h)' la colonne cible
# data = train_data['vitesse_(km/h)']
# meilleurs_modele = recherche_hyperparametres_arima(data, p_range=[0, 1, 2], d_range=[0, 1], q_range=[0, 1, 2])


# %%
# Assurez-vous que train_data est votre DataFrame et 'vitesse_(km/h)' la colonne cible
data = train_data['vitesse_(km/h)']
meilleurs_modele = recherche_hyperparametres_arima(data,
                                                   p_range=[2, 1, 1],
                                                   d_range=[0, 1],
                                                   q_range=[0, 1, 2])
# 1 min
# ARIMA(1, 1, 2) - AIC:42588.17025183867
# Meilleur modèle: ARIMA(1, 0, 2) - AIC: 42559.473341610465


# %%
data = train_data['direction_(°)']
meilleurs_modele = recherche_hyperparametres_arima(data,
                                                   p_range=[2, 1, 1],
                                                   d_range=[0, 1],
                                                   q_range=[0, 1, 2])
# ARIMA(1, 1, 2) - AIC:-16613.022539697413
# Meilleur modèle: ARIMA(2, 0, 2) - AIC: -16689.948372385094


# %% [markdown]
# ### ARIMA avec la fonction pmdArima

# %%
import pmdarima as pm


def ajuster_auto_arima_diurne(train_data, target_column):
    """
    Ajuste automatiquement un modèle ARIMA sur la colonne cible du dataset, en tenant compte
    des variations diurnes pour des données au pas de 10 minutes.

    :param train_data: DataFrame pandas contenant les données d'entraînement.
    :param target_column: La colonne cible (variable à prédire) dans le DataFrame.
    :return: Le modèle ARIMA ajusté.
    """
    # Sélection de la colonne cible
    y = train_data[target_column]

    # Ajustement du modèle ARIMA avec une potentialité de variation diurne
    modele_arima = pm.auto_arima(
        y,
        seasonal=True,  # Explorer la composante saisonnière
        m=24,  # Nombre de périodes de 10 min dans une journée
        d=None,  # Laisser pmdarima déterminer d
        D=1,  # Tester avec D=1, vu la variation diurne supposée
        max_p=2,
        max_q=2,
        max_P=2,
        max_Q=2,
        max_D=1,
        trace=True,  # Afficher le processus de recherche
        error_action='ignore',  # Ne pas arrêter sur des erreurs de convergence
        suppress_warnings=True,  # Supprimer les avertissements
        stepwise=True)  # Utiliser l'algorithme stepwise

    logging.info(modele_arima.summary())
    return modele_arima


# Exemple d'utilisation
# Remplacer 'train_data' par votre DataFrame et 'vitesse_(km/h)' par la colonne cible de votre choix
# modele_arima_ajuste = ajuster_auto_arima_diurne(train_data, 'vitesse_(km/h)')


# %%
train_data


# %%
data = train_data
modele_arima_ajuste = ajuster_auto_arima_diurne(train_data, 'vitesse_(km/h)')
modele_arima_ajuste
#  ARIMA(2,0,2)(1,1,1)[144] intercept   : AIC=inf, Time=6430.11 sec
#  ARIMA(0,0,0)(0,1,0)[144] intercept   : AIC=100765.465, Time=81.50 sec
# Performing stepwise search to minimize aic
#  ARIMA(2,0,2)(1,1,1)[24] intercept   : AIC=inf, Time=403.60 sec
#  ARIMA(0,0,0)(0,1,0)[24] intercept   : AIC=-15560.423, Time=3.63 sec
#  ARIMA(1,0,0)(1,1,0)[24] intercept   : AIC=-51507.835, Time=64.61 sec
#  ARIMA(0,0,1)(0,1,1)[24] intercept   : AIC=-29560.577, Time=41.46 sec
#  ARIMA(0,0,0)(0,1,0)[24]             : AIC=-15562.347, Time=2.29 sec
#  ARIMA(1,0,0)(0,1,0)[24] intercept   : AIC=-47740.368, Time=6.65 sec
#  ARIMA(1,0,0)(2,1,0)[24] intercept   : AIC=-52983.633, Time=350.20 sec
#  ARIMA(1,0,0)(2,1,1)[24] intercept   : AIC=inf, Time=492.25 sec
#  ARIMA(1,0,0)(1,1,1)[24] intercept   : AIC=inf, Time=100.12 sec
#  ARIMA(0,0,0)(2,1,0)[24] intercept   : AIC=-15833.619, Time=75.39 sec
#  ARIMA(2,0,0)(2,1,0)[24] intercept   : AIC=-53024.361, Time=476.26 sec
#  ARIMA(2,0,0)(1,1,0)[24] intercept   : AIC=-51569.533, Time=62.95 sec
#  ARIMA(2,0,0)(2,1,1)[24] intercept   : AIC=inf, Time=588.83 sec
#  ARIMA(2,0,0)(1,1,1)[24] intercept   : AIC=inf, Time=98.57 sec
#  ARIMA(2,0,1)(2,1,0)[24] intercept   : AIC=-53023.449, Time=601.38 sec
#  ARIMA(1,0,1)(2,1,0)[24] intercept   : AIC=-53028.062, Time=614.76 sec
#  ARIMA(1,0,1)(1,1,0)[24] intercept   : AIC=-51572.005, Time=77.84 sec
#  ARIMA(1,0,1)(2,1,1)[24] intercept   : AIC=inf, Time=693.66 sec
#  ARIMA(1,0,1)(1,1,1)[24] intercept   : AIC=inf, Time=117.39 sec
#  ARIMA(0,0,1)(2,1,0)[24] intercept   : AIC=-29687.499, Time=230.13 sec
#  ARIMA(1,0,2)(2,1,0)[24] intercept   : AIC=-53018.092, Time=572.23 sec
#  ARIMA(0,0,2)(2,1,0)[24] intercept   : AIC=-37425.462, Time=476.40 sec
#  ARIMA(2,0,2)(2,1,0)[24] intercept   : AIC=-52944.422, Time=655.27 sec
#  ARIMA(1,0,1)(2,1,0)[24]             : AIC=-53030.050, Time=120.95 sec
#  ARIMA(1,0,1)(1,1,0)[24]             : AIC=-51573.865, Time=20.13 sec
#  ARIMA(1,0,1)(2,1,1)[24]             : AIC=inf, Time=291.86 sec
#  ARIMA(1,0,1)(1,1,1)[24]             : AIC=inf, Time=74.22 sec
#  ARIMA(0,0,1)(2,1,0)[24]             : AIC=-29689.407, Time=54.95 sec
#  ARIMA(1,0,0)(2,1,0)[24]             : AIC=-52985.611, Time=103.84 sec
#  ARIMA(2,0,1)(2,1,0)[24]             : AIC=-53025.439, Time=118.15 sec
#  ARIMA(1,0,2)(2,1,0)[24]             : AIC=-53031.011, Time=185.04 sec
#  ARIMA(1,0,2)(1,1,0)[24]             : AIC=-51574.954, Time=25.58 sec
#  ARIMA(1,0,2)(2,1,1)[24]             : AIC=inf, Time=389.06 sec
#  ARIMA(1,0,2)(1,1,1)[24]             : AIC=inf, Time=135.23 sec
#  ARIMA(0,0,2)(2,1,0)[24]             : AIC=-37427.381, Time=141.00 sec
#  ARIMA(2,0,2)(2,1,0)[24]             : AIC=-53034.431, Time=182.50 sec
#  ARIMA(2,0,2)(1,1,0)[24]             : AIC=-51573.792, Time=39.23 sec


# %% [markdown]
# ### Modele VARMAX

# %% [markdown]
# #### Fonction reduction ACP

# %%
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def appliquer_acp(df, n_components=None):
    """
    Applique l'ACP sur le DataFrame et retourne les composantes principales.

    :param df: DataFrame pandas contenant les données.
    :param n_components: Nombre de composantes principales à conserver.
    :return: DataFrame des composantes principales.
    """
    # Standardisation des données
    df_std = StandardScaler().fit_transform(df)

    # ACP
    pca = PCA(n_components=n_components)
    composantes_principales = pca.fit_transform(df_std)

    # Création d'un DataFrame pour les composantes principales
    cols = [f'PC{i+1}' for i in range(composantes_principales.shape[1])]
    df_pca = pd.DataFrame(data=composantes_principales, columns=cols, index=df.index)

    return df_pca


# %% [markdown]
# #### Fonction recherche des meilleurs hyperparametres

# %%
import itertools
from statsmodels.tsa.statespace.varmax import VARMAX
from sklearn.metrics import mean_squared_error

def recherche_hyperparametres_varmax(data, p_range, q_range, d=1, saison=None):
    """
    Recherche les meilleurs hyperparamètres pour le modèle VARMAX.

    :param data: DataFrame des données d'entraînement.
    :param p_range: Intervalle des valeurs de p à tester.
    :param q_range: Intervalle des valeurs de q à tester.
    :param d: Ordre de différenciation (suppose une stationnarité après d différenciations).
    :param saison: Paramètres saisonniers sous la forme (P,D,Q,s).
    :return: Meilleurs paramètres et résultat.
    """
    meilleurs_resultats = float("inf")
    meilleurs_parametres = None

    for p in p_range:
        for q in q_range:
            try:
                modele_varmax = VARMAX(data, order=(p,d,q), seasonal_order=saison, enforce_stationarity=False, enforce_invertibility=False)
                resultats_varmax = modele_varmax.fit(disp=False)

                # Utilisez votre critère de sélection ici, par exemple AIC
                if resultats_varmax.aic < meilleurs_resultats:
                    meilleurs_resultats = resultats_varmax.aic
                    meilleurs_parametres = (p, d, q, saison)

            except:
                continue

    print(f"Meilleurs Paramètres: {meilleurs_parametres}, AIC: {meilleurs_resultats}")
    return meilleurs_parametres


# %%


# %% [markdown]
# #### Fonction ajustement modele VARIMAX au pas horaire

# %%
import pandas as pd
from statsmodels.tsa.statespace.varmax import VARMAX
from statsmodels.tsa.stattools import adfuller
import numpy as np


def ajuster_varmax_horaire(df):
    """
    Ajuste un modèle VARMAX sur un dataset transformé au pas horaire avec ACP.

    :param df: DataFrame pandas contenant les données d'entraînement.
    :param n_components: Nombre de composantes principales à utiliser dans l'ACP.
    :return: Le modèle VARMAX ajusté.
    """
    # Application de l'ACP
    df_acp = appliquer_acp(df, n_components=n_components)
    df=df_acp.copy()
    # Assurer que l'index est de type datetime et que les données sont au pas horaire
    df.index = pd.to_datetime(df.index)
    df = df.resample('h').mean()  # Aggrégation horaire par la moyenne

    # Tester la stationnarité de chaque variable
    def tester_stationnarite(serie):
        resultat = adfuller(serie.dropna(), autolag='AIC')
        return resultat[1]  # Retourne la p-value du test ADF

    # Appliquer une différenciation si nécessaire pour atteindre la stationnarité
    variables_a_differencier = [
        col for col in df.columns if tester_stationnarite(df[col]) > 0.05
    ]
    for col in variables_a_differencier:
        df[col] = df[col].diff().dropna()

    df.dropna(inplace=True)  # Éliminer les possibles NaN après différenciation

    # Sélection des variables pour le modèle VARMAX (peut nécessiter ajustement)
    variables = df.columns

    # Ajustement du modèle VARMAX
    m = 144,  # Nombre de périodes de 10 min dans une journée
    # Remplacer 'order=(2, 2)' par vos paramètres AR et MA, 'seasonal_order=(1, 1, 1, 144)' par vos paramètres saisonniers
    modele_varmax = VARMAX(df[variables],
                           order=(2, 2),
                           seasonal_order=(1, 0, 2, m),
                           trend='c')
    resultats_varmax = modele_varmax.fit(disp=False)

    print(resultats_varmax.summary())
    return resultats_varmax


# %%
train_data.columns.tolist()
print(f"\n train_data.columns.tolist():\n{train_data.columns.tolist()} \n")


# %% [markdown]
# #### Fonction globale

# %%
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.varmax import VARMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import itertools
from sklearn.impute import SimpleImputer



def appliquer_acp(df, variance_expliquee_seuil=0.95,n_components=5):
    df_std = StandardScaler().fit_transform(df)
    pca = PCA()
    pca.fit(df_std)
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cumsum >= variance_expliquee_seuil) + 1
    pca = PCA(n_components=n_components)
    composantes_principales = pca.fit_transform(df_std)
    cols = [f'PC{i+1}' for i in range(composantes_principales.shape[1])]
    df_pca = pd.DataFrame(data=composantes_principales, columns=cols, index=df.index)
    return df_pca


def ajuster_varmax_horaire(df, p_range, range_d, q_range, n_components=None):
    df.index = pd.to_datetime(df.index)
    df = df.resample('h').mean()
    imputer = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
    df_imputed = imputer.fit_transform(df)
    df_imputed = pd.DataFrame(df_imputed, columns=df.columns, index=df.index)
    df=df_imputed.copy()
    df_pca = appliquer_acp(df, n_components=n_components)

    def tester_stationnarite(serie):
        resultat = adfuller(serie.dropna(), autolag='AIC')
        return resultat[1]

    variables_a_differencier = [col for col in df_pca.columns if tester_stationnarite(df_pca[col]) > 0.05]
    for col in variables_a_differencier:
        df_pca[col] = df_pca[col].diff().dropna()

    df_pca.dropna(inplace=True)
    variables = df_pca.columns

    meilleurs_resultats = float("inf")
    meilleurs_parametres = None
    for d in range_d:
        for p in p_range:
            for q in q_range:
                try:
                    modele_varmax = VARMAX(df_pca[variables], order=(p,0,q), trend='c')
                    resultats_varmax = modele_varmax.fit(disp=False)

                    if resultats_varmax.aic < meilleurs_resultats:
                        meilleurs_resultats = resultats_varmax.aic
                        meilleurs_parametres = (p, q)

                except:
                    continue

    print(f"Meilleurs Paramètres: {meilleurs_parametres}, AIC: {meilleurs_resultats}")
    modele_varmax = VARMAX(df_pca[variables], order=meilleurs_parametres, trend='c')
    resultats_varmax = modele_varmax.fit(disp=False)
    print(resultats_varmax.summary())

    return resultats_varmax


# %%

# Exemple de plage de valeurs pour p et q
p_range = [0,1, 2, 3,4]
q_range = [0,1, 2, 3,4]
range_d = [0,1, 2]


# Utilisation de la fonction ajustée
resultats_varmax = ajuster_varmax_horaire(train_data, p_range,range_d, q_range, n_components=5)


# %%


# %%
# data_filtred = train_data[['wave_amplitude_(m)', 'wave_period_(s)', 'direction_de_surface_(°)', 'pression_(bar)',  'direction_(°)', 'vitesse_(km/h)', 'rafale_(km/h)']]
# resultats_varmax = ajuster_varmax_horaire(data_filtred)


# %% [markdown]
# **Qualité du modèle**
# Log Likelihood : La log-vraisemblance **élevée**  peut indiquer un bon ajustement du modèle aux données. Cependant, ce critère seul n'est pas suffisant pour évaluer la qualité du modèle.
#
# AIC/BIC/HQIC : Les critères d'information d'Akaike (AIC), Bayesian (BIC), et Hannan-Quinn (HQIC) sont des mesures permettant d'évaluer la qualité du modèle tout en prenant en compte le nombre de paramètres. Plus ces valeurs sont **basses**, mieux c'est. Dans ce cas, elles semblent indiquer que le modèle est relativement complexe, avec potentiellement un risque de surajustement.
#
# **Tests statistiques**
#
# Ljung-Box (Q) et Prob(Q) : Ces tests servent à vérifier l'autocorrélation des résidus. Des valeurs de Prob(Q) **élevées** (proches de 1) suggèrent qu'il n'y a pas d'autocorrélation significative, ce qui est généralement bon pour un modèle VARMA.
#
# **Jarque-Bera (JB)** et **Prob(JB)** : Le test de Jarque-Bera examine la normalité des résidus en se basant sur leur skewness (asymétrie) et kurtosis (aplatissement).
#
# Des valeurs de **Prob(JB)** proches de **0** indiquent une non-normalité des résidus, ce qui est le cas ici, suggérant que les résidus ne suivent pas une distribution normale.
#
# **Heteroskedasticity (H)** et **Prob(H)** : Le test d'hétéroscédasticité évalue si la variance des résidus est constante dans le temps. Les valeurs de Prob(H) **proches de 0 ou 1** indiquent respectivement une présence ou une absence d'hétéroscédasticité. Des résultats  mixtes,  pourraient indiquer des variations dans la variance des résidus pour certaines variables.
#
# **Coefficients du modèle**
# Les coefficients pour chaque variable et pour chaque retard (L1, L2) sont accompagnés de leur erreur standard, de la valeur de **test (z)** et de la p-value (P>|z|). Dans ce cas, la plupart des coefficients semblent ne pas être statistiquement significatifs **(p-values élevées)**, ce qui peut indiquer que certaines variables explicatives ne sont **pas pertinentes** pour prédire les variables dépendantes.
#
# **Conclusions**
# Ajustement du modèle : Bien que la log-vraisemblance soit élevée, l'absence de normalité des résidus (probabilités JB proches de 0) et la non-significativité statistique de nombreux coefficients suggèrent que le modèle pourrait ne pas être bien ajusté.
#
# Complexité vs Pertinence : Les valeurs élevées d'AIC, BIC et HQIC suggèrent que le modèle est complexe, possiblement trop pour les données à disposition. Il peut être utile de simplifier le modèle ou d'examiner d'autres structures de modèle.
#
# Prédictions et implications : Malgré ces limitations, le modèle VARMA peut encore fournir des insights utiles, notamment en identifiant des relations dynamiques entre les variables. Cependant, il serait prudent de ne pas se fier uniquement à ce modèle pour des prédictions ou des décisions importantes sans examiner d'autres données ou modèles.
#
# Une analyse plus approfondie, peut-être avec des modèles alternatifs ou une réduction de la complexité du modèle actuel, pourrait être bénéfique pour améliorer la compréhension et la prédiction des séries temporelles analysées.

# %% [markdown]
# ### Prediction de varmax

# %%
df


# %%
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import matplotlib.dates as mdates

# Supposons que 'scaler' est votre MinMaxScaler qui a été ajusté sur les données d'entraînement

scaler=MinMaxScaler()
scaler.fit(df[['vitesse_(km/h)']])


# Préparer les prédictions pour les prochaines 5 heures
nombre_de_pas_a_prevoir = 5  # Par exemple pour prévoir les 5 prochaines heures
predictions = resultats_varmax.get_forecast(steps=nombre_de_pas_a_prevoir)
predictions_df = predictions.predicted_mean

# Inverser la transformation de mise à l'échelle sur les prédictions
predictions_inverses = scaler.inverse_transform(predictions_df)

# Si vous avez également mis à l'échelle les données d'entraînement, vous voudrez les inverser également pour le tracé
train_data_inverses = scaler.inverse_transform(train_data[['vitesse_(km/h)']])

# # Tracer les données d'entraînement inversées et les prédictions inversées
plt.figure(figsize=(10, 5))

# plt.plot(train_data.index[-120:], train_data_inverses[-120:], label='Données réelles', color='blue')  # Les 5 derniers jours (24*5=120)

# # Calculer l'index pour les prédictions
index_predictions = pd.date_range(start=train_data.index[-1], periods=nombre_de_pas_a_prevoir + 1, freq='6H')[1:]


# Tracer les données d'entraînement inversées
plt.plot(train_data.index[-120:], train_data_inverses[-120:], label='Données réelles', color='blue')  # Les dernières 120 heures

# Tracer les prédictions
# Supposons que index_predictions est correctement défini pour couvrir la période de prédiction
plt.plot(index_predictions, predictions_inverses[:, 0], label='Prédictions', color='red', linestyle='--')

# Formater l'axe des x pour afficher les dates et les heures
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Interval d'une étiquette toutes les 12 heures
plt.gcf().autofmt_xdate()  # Rotation automatique des dates pour améliorer la lisibilité

# Ajouter des titres et légendes
plt.title('Vitesse du vent - Données réelles vs Prédictions')
plt.xlabel('Date et heure')
plt.ylabel('Vitesse du vent (km/h)')
plt.legend()

# Afficher le graphique
plt.show()


# %% [markdown]
# ### modèle VAR (Vector Autoregression)
#
# pour le dataset de meteo france et ses 40 colonnes.  A utiliser suelement aprés traitement des données

# %%
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import numpy as np


def preparer_et_ajuster_var(df):
    """
    Prépare le dataset et ajuste un modèle VAR.

    :param df: DataFrame pandas contenant les données.
    :return: Résultats de l'ajustement du modèle VAR.
    """
    # Conversion des séparateurs décimaux et gestion des types de données
    df = df.replace(',', '.', regex=True).astype(float)

    # Suppression des colonnes non numériques ou non pertinentes si nécessaire
    # df.drop(['POSTE', 'DATE', ...], axis=1, inplace=True)

    # Vérification de la stationnarité avec le test de Dickey-Fuller augmenté
    def tester_stationnarite(series):
        resultat = adfuller(series, autolag='AIC')
        return resultat[1]  # p-value

    # Appliquer le test de stationnarité et différencier les séries non stationnaires
    for column in df.columns:
        if tester_stationnarite(df[column]) > 0.05:  # Seuil de p-value à 0.05
            df[column] = df[column].diff().dropna()

    # Suppression des éventuelles lignes contenant des NaN après différenciation
    df.dropna(inplace=True)

    # Ajustement du modèle VAR
    modele_var = VAR(df)
    resultats_var = modele_var.fit(maxlags=15, ic='aic')

    print(resultats_var.summary())
    return resultats_var


# Exemple d'utilisation

# Assurez-vous d'avoir converti les colonnes DATE en datetime et de les avoir éventuellement exclues du VAR si elles ne sont pas numériques
# df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d%H')

# Ajuster le modèle VAR
# resultats_var = preparer_et_ajuster_var(df)


# %%
resultats_var = preparer_et_ajuster_var(df.drop("date", axis=1))


# %% [markdown]
# ### Modele VECM (Vector Error Correction Model)
#
# Un VECM est approprié si vos données sont cointégrées, ce qui signifie qu'il existe une relation à long terme entre les séries temporelles même si elles sont non stationnaires.
# Il est particulièrement utile pour les séries temporelles économiques où les variables sont susceptibles d'avoir des relations d'équilibre à long terme.

# %%
from statsmodels.tsa.vector_ar.vecm import VECM


def vecm_model(data):
    """
    Ajuster un modèle VECM.
    """
    model = VECM(data, k_ar_diff=1, coint_rank=1)
    results = model.fit()
    return results


# %% [markdown]
# ### Modele GARCH (Generalized Autoregressive Conditional Heteroskedasticity )
#
# Si la volatilité des données est une caractéristique importante, par exemple dans les séries temporelles financières, un modèle GARCH peut être utilisé pour modéliser et prévoir la variance conditionnelle (c'est-à-dire la volatilité)

# %%
from arch import arch_model


def garch_model(data):
    """
    Ajuster un modèle GARCH.
    """
    model = arch_model(data, vol='GARCH', p=1, q=1)
    results = model.fit()
    return results


# %% [markdown]
# ### Modele Dynamic Factor Model (DFM) :
#
# Les DFM sont utilisés pour modéliser les séries temporelles multivariées où quelques facteurs communs sous-jacents influencent toutes les séries. Ils sont utiles pour réduire la dimensionnalité des données et pour capturer les interactions entre les séries.

# %%
from statsmodels.tsa.statespace.dynamic_factor import DynamicFactor


def dfm_model(data):
    """
    Ajuster un modèle DFM.
    """
    model = DynamicFactor(data, k_factors=1, factor_order=1)
    results = model.fit()
    return results


# %% [markdown]
# ### Modele Modèle à espace d'états avec filtre de Kalman :
#
# modèles à espace d'états, souvent utilisés avec le filtre de Kalman, sont très flexibles et permettent de modéliser des séries temporelles multivariées où des relations complexes et changeantes existent entre les variables

# %%
from statsmodels.tsa.statespace.sarimax import SARIMAX


def statespace_model(data):
    """
    Ajuster un modèle à espace d'états avec filtre de Kalman.
    """
    model = SARIMAX(data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    results = model.fit()
    return results


# %% [markdown]
# ### Modele Random Forest :
#
#  forêts aléatoires (**Random Forests**) ou les machines à vecteurs de support (Support Vector Machines) pour les séries temporelles peuvent être appliquées en créant des caractéristiques retardées (lag features) comme entrée.

# %%
from sklearn.ensemble import RandomForestRegressor


def random_forest_model(data, target):
    """
    Ajuster un modèle Random Forest.
    """
    model = RandomForestRegressor(n_estimators=100)
    model.fit(data, target)
    return model


# %% [markdown]
# ### Modele XGBoost

# %%
import xgboost as xgb


def xgboost_model(data, target):
    """
    Ajuster un modèle XGBoost.
    """
    model = xgb.XGBRegressor(n_estimators=100)
    model.fit(data, target)
    return model


# %% [markdown]
# ### Modele Support Vector Machine (SVM)

# %%
from sklearn.svm import SVR


def svm_model(data, target):
    """
    Ajuster un modèle SVM.
    """
    model = SVR(kernel='rbf')
    model.fit(data, target)
    return model


# %%
df_13056002_01jan2014_01mar2024


# %% [markdown]
# ## Deep learning
# ### Modele LSTM (Long Short-Term Memory)

# %%
df = df_13056002_01jan2014_01mar2024.copy()
train_data, val_data, test_data = split_time_series(df, train_size=0.7, val_size=0.2, date_column='date')

logger.debug(f"\n liste colonnes:\n{train_data.columns.tolist()} ")


# %%
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import numpy as np


def prepare_data(data, n_steps):
    """
    Préparer les données pour le modèle LSTM.

    :param data: DataFrame contenant les données à utiliser.
    :param n_steps: Nombre de pas de temps à utiliser comme entrée pour la prédiction.
    :return: X, y où X est un tableau de données d'entrée et y est le tableau des cibles à prédire.
    """
    X, y = list(), list()
    for i in range(len(data)):
        # Trouver la fin de ce pattern
        end_ix = i + n_steps
        # Vérifier si on est au-delà de la séquence
        if end_ix > len(data) - 1:
            break
        # Rassembler les entrées et les sorties
        seq_x, seq_y = data[i:end_ix, :-1], data[end_ix - 1, -1]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


def lstm_model(train_data, n_steps):
    """
    Ajuster un modèle LSTM sur les données d'entraînement.

    :param train_data: Les données d'entraînement préparées par la fonction `prepare_data`.
    :param n_steps: Nombre de pas de temps utilisés pour chaque séquence d'entrée.
    :return: Un modèle LSTM ajusté.
    """
    # La forme des données est [échantillons, pas de temps, caractéristiques]
    n_features = train_data.shape[2]
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    # Diviser les données d'entraînement en X (entrées) et y (cibles)
    X, y = prepare_data(train_data, n_steps)

    # Ajuster le modèle
    model.fit(X, y, epochs=50, verbose=0)

    return model


# %%


# Préparation des données d'entraînement
# Supposons que `train_data_np` est votre DataFrame converti en un tableau numpy, avec la dernière colonne étant celle que vous voulez prédire.
# Vous devriez adapter cette partie pour extraire les données de votre DataFrame.
n_steps = 3  # Par exemple, utiliser les 3 dernières heures pour prédire la prochaine.
# train_data_np = train_data.to_numpy()  # Convertir le DataFrame en numpy array si ce n'est pas déjà fait.

# Appel de la fonction
model = lstm_model(train_data_np, n_steps)
model = lstm_model(train_data, n_steps)


# %%
target=
lstm_model(train_data,target,"10T")


# %% [markdown]
# ### Modele GRU
#
# les GRU (Gated Recurrent Units) sont conçus pour traiter des séquences de données comme les séries temporelles.

# %%
from keras.models import Sequential
from keras.layers import GRU, Dense


def gru_model(data, target, n_steps):
    """
    Ajuster un modèle GRU.
    """
    model = Sequential()
    model.add(GRU(50, activation='relu', input_shape=(n_steps, data.shape[1])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(data, target, epochs=50, verbose=0)
    return model


# %% [markdown]
# ### Modele CNN
#
# Convolutional Neural Networks (**CNN**) :
#
#  Bien que principalement utilisés pour l'analyse d'image, ils peuvent être appliqués aux séries temporelles pour capturer des motifs locaux

# %%
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense


def cnn_model(data, target, n_steps):
    """
    Ajuster un modèle CNN.
    """
    model = Sequential()
    model.add(
        Conv1D(filters=64,
               kernel_size=2,
               activation='relu',
               input_shape=(n_steps, data.shape[1])))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(50, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(data, target, epochs=50, verbose=0)
    return model


# %% [markdown]
# ### Modele  MARS
#
# Multivariate Adaptive Regression Splines **(MARS)**
#
# MARS est un modèle non-paramétrique qui peut être utilisé pour modéliser des relations complexes et non linéaires entre les variables.

# %%
from pyearth import Earth


def mars_model(data, target):
    """
    Ajuster un modèle MARS.
    """
    model = Earth()
    model.fit(data, target)
    return model


# %% [markdown]
# ### Modele RNN
#
#  Les réseaux de neurones récurrents (**RNN**), en particulier les variantes telles que les LSTM (Long Short-Term Memory) et les GRU (Gated Recurrent Unit), sont bien adaptés pour modéliser des données séquentielles et peuvent capturer des relations complexes dans des séries temporelles multivariées.
# Machine Learning Traditionnel:

# %%
from keras.models import Sequential
from keras.layers import LSTM, GRU


def ajuster_rnn(data, n_neurons, n_inputs, n_outputs):
    model = Sequential()
    model.add(LSTM(n_neurons, input_shape=(n_inputs, data.shape[1])))
    # Pour GRU: model.add(GRU(n_neurons, input_shape=(n_inputs, data.shape[1])))
    model.add(Dense(n_outputs))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


# %% [markdown]
# ## Modele VAR

# %%
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import warnings


def ajuster_modele_var(df):
    """
    Ajuste un modèle VAR sur un DataFrame contenant plusieurs séries temporelles interdépendantes.

    :param df: DataFrame pandas contenant les séries temporelles avec une colonne de date en index.
    :return: Objet VARResults après l'ajustement du modèle.
    """

    # Vérifier la stationnarité de chaque série temporelle
    def tester_stationnarite(serie):
        resultat_test = adfuller(serie, autolag='AIC')
        return resultat_test[1]  # p-value du test ADF

    # Tester toutes les séries pour la stationnarité
    p_values = df.apply(tester_stationnarite, axis=0)
    non_stationnaires = p_values[p_values > 0.05].index.tolist()

    if non_stationnaires:
        warnings.warn(
            f"Les séries suivantes ne sont pas stationnaires : {
                non_stationnaires}",
            UserWarning)

    # Ajuster le modèle VAR sur les données
    modele_var = VAR(df)
    resultats_var = modele_var.fit(maxlags=15, ic='aic')

    # Afficher le résumé du modèle ajusté
    print(resultats_var.summary())

    return resultats_var


# Exemple d'utilisation
# Assurez-vous que 'df' est votre DataFrame avec des séries temporelles et qu'il a une colonne de date comme index
# df = pd.read_csv('votre_fichier.csv', index_col='date', parse_dates=['date'])
# resultats_var = ajuster_modele_var(df)


# %%
resultats_var = ajuster_modele_var(df)


# %% [markdown]
# ## autres modéles à exploiter
#
# Modèles VARMA (Vector Autoregressive Moving Average):
#
# - Le modèle VARMA combine les modèles VAR et VMA et peut être utile si les séries temporelles présentent à la fois une autocorrélation et une moyenne mobile.
# - Modèles **VARMAX** (Vector Autoregressive Moving-Average with eXogenous inputs):
#
# Ce modèle étend le VARMA en incluant des variables exogènes. Si vous avez des données supplémentaires qui pourraient influencer vos séries temporelles, comme des facteurs économiques ou des événements spéciaux, le modèle VARMAX peut les prendre en compte.
#
# - Modèles **VECM** (Vector Error Correction Model):
#
# Le VECM est approprié pour les séries temporelles non stationnaires qui sont cointégrées. Si vos séries temporelles ont des tendances stochastiques communes sur le long terme, le VECM peut être un bon choix.
# Réseaux de Neurones et Deep Learning:
#
# - Les réseaux de neurones récurrents (**RNN**), en particulier les variantes telles que les LSTM (Long Short-Term Memory) et les GRU (Gated Recurrent Unit), sont bien adaptés pour modéliser des données séquentielles et peuvent capturer des relations complexes dans des séries temporelles multivariées.
# Machine Learning Traditionnel:
#
# -  forêts aléatoires (**Random Forests**) ou les machines à vecteurs de support (Support Vector Machines) pour les séries temporelles peuvent être appliquées en créant des caractéristiques retardées (lag features) comme entrée.
#
# - Modèles Basés sur les Ensembles (Ensemble Models):
#
# - Generalized Autoregressive Conditional Heteroskedasticity (**GARCH**) :
#
# Si la volatilité des données est une caractéristique importante, par exemple dans les séries temporelles financières, un modèle GARCH peut être utilisé pour modéliser et prévoir la variance conditionnelle (c'est-à-dire la volatilité).
#
# - Dynamic Factor Models (**DFM**) :
#
# Les DFM sont utilisés pour modéliser les séries temporelles multivariées où quelques facteurs communs sous-jacents influencent toutes les séries. Ils sont utiles pour réduire la dimensionnalité des données et pour capturer les interactions entre les séries.
# State Space Models and Kalman Filter :
#
# -  modèles à espace d'états, souvent utilisés avec le filtre de Kalman, sont très flexibles et permettent de modéliser des séries temporelles multivariées où des relations complexes et changeantes existent entre les variables.
#
# **Machine Learning and Ensemble Methods** :
#
# - Random Forests,
# - Gradient Boosting Machines (comme XGBoost, LightGBM), ou
# - Support Vector Machines pour les séries temporelles (SVM) : Ces méthodes peuvent être utilisées pour capter des relations non linéaires et des interactions complexes entre les variables.
#
# **Deep Learning : Des réseaux de neurones comme**
# - les LSTM (Long Short-Term Memory) ou
# - les GRU (Gated Recurrent Units) qui sont conçus pour traiter des séquences de données comme les séries temporelles.
# - Convolutional Neural Networks (CNN) : Bien que principalement utilisés pour l'analyse d'image, ils peuvent être appliqués aux séries temporelles pour capturer des motifs locaux.
#
# - Multivariate Adaptive Regression Splines **(MARS)** :
#
# MARS est un modèle non-paramétrique qui peut être utilisé pour modéliser des relations complexes et non linéaires entre les variables.

# %%


# %% [markdown]
# ## approche par utilisation de xgboost

# %%
import xgboost as xgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Supposons que train_data soit votre DataFrame

# Préparation des données
X = train_data[['temperature_(°)', 'rafale_(km/h)',
                'direction']]  # caractéristiques
y = train_data['vitesse_(km/h)']  # cible

# Division du dataset en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2,
                                                    random_state=42)

# Convertir les ensembles de données en DMatrix, une structure de données optimisée par XGBoost
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# Paramètres du modèle XGBoost
param = {
    'max_depth': 5,  # profondeur maximale de chaque arbre
    'eta': 0.3,  # taux d'apprentissage
    'objective':
    'reg:squarederror',  # objectif de régression avec erreur quadratique
    'eval_metric':
    'rmse'  # utiliser la racine de l'erreur quadratique moyenne comme métrique d'évaluation
}
num_round = 100  # nombre d'itérations de boosting

# Entraînement du modèle
bst = xgb.train(param, dtrain, num_round)

# Faire des prédictions sur l'ensemble de test
preds = bst.predict(dtest)

# Évaluer le modèle
rmse = mean_squared_error(y_test, preds, squared=False)
print(f"RMSE: {rmse}")

# Vous pouvez ajuster les paramètres et le nombre d'itérations pour améliorer le modèle


# %% [markdown]
# ## Creation d'un wrapper pour utiliser un model SARIMAX dans scikit-learn
#
# car SARIMAX de statsmodels ne suit pas directement l'API de scikit-learn

# %% [markdown]
# ### Fonction optimisation serie temporelle utilisant le wrapper SARIMAX
#
#

# %%
# import pandas as pd
# from statsmodels.tsa.statespace.sarimax import SARIMAX
# from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
# from sklearn.metrics import make_scorer, mean_squared_error, mean_absolute_error
# from sklearn.pipeline import Pipeline
# from sklearn.base import BaseEstimator, RegressorMixin
# import numpy as np

# # Définition du wrapper SARIMAX pour l'intégrer dans scikit-learn
# class SARIMAXWrapper(BaseEstimator, RegressorMixin):
#     def __init__(self, order=(1, 0, 0), seasonal_order=(0, 0, 0, 0)):
#         self.order = order
#         self.seasonal_order = seasonal_order
#         self.model = None

#     def fit(self, X, y):
#         self.model = SARIMAX(y, order=self.order, seasonal_order=self.seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
#         self.model = self.model.fit(disp=False)
#         return self

#     def predict(self, X):
#         # Dans SARIMAX, X est généralement le nombre de périodes à prédire, mais cela peut être ajusté en fonction de vos besoins
#         forecast = self.model.get_forecast(steps=len(X))
#         return forecast.predicted_mean

# def optimiser_serie_temporelle(df, date_train_end, date_test_start,
#                                nom_colonne_predire, params):
#     """
#     Fonction pour optimiser un modèle de série temporelle SARIMAX sur un DataFrame.

#     :param df: DataFrame contenant les données de la série temporelle.
#     :param date_train_end: Date de fin de l'entraînement (format 'AAAA-MM-JJ').
#     :param date_test_start: Date de début du test (format 'AAAA-MM-JJ').
#     :param params: Dictionnaire des paramètres pour GridSearchCV.
#     :return: Le modèle optimisé, scores sur les ensembles d'entraînement, de test et de validation.
#     """
#     # # Séparer les données en ensembles d'entraînement, de validation, et de test
#     # train_data = df[:date_train_end]
#     # test_data = df[date_test_start:]
#     df.index = pd.to_datetime(df.index)
#     df = df.asfreq('D')  # Utilisez 'D', 'M', ou toute autre fréquence adaptée à vos données

#     # Séparer les données en ensembles d'entraînement et de test
#     train_data = df[:date_train_end][nom_colonne_predire]
#     test_data = df[date_test_start:][nom_colonne_predire]
#     # Définir les hyperparamètres et le modèle à utiliser dans le GridSearch
#     tscv = TimeSeriesSplit(n_splits=3)
#     # Définition des métriques d'évaluation
#     scoring = {
#         'RMSE': make_scorer(mean_squared_error, squared=False),
#         'MAE': make_scorer(mean_absolute_error)
#     }

#     # Création de l'instance GridSearchCV
#     grid_search = GridSearchCV(SARIMAXWrapper(),
#                                param_grid=params,
#                                cv=tscv,
#                                scoring=scoring,
#                                refit='RMSE')

#     # Entraînement du modèle
#     grid_search.fit(np.arange(len(train_data)), train_data)

#     # Prédiction et évaluation sur l'ensemble de test
#     y_pred_test = grid_search.predict(np.arange(len(test_data)))

#     # Calcul des scores
#     scores_test = {
#         'RMSE': mean_squared_error(test_data, y_pred_test, squared=False),
#         'MAE': mean_absolute_error(test_data, y_pred_test)
#     }

#     return grid_search.best_estimator_, scores_test, train_data, test_data, y_pred_test


# %%
# import pandas as pd
# from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
# from sklearn.metrics import make_scorer, mean_squared_error, mean_absolute_error
# from sklearn.pipeline import make_pipeline
# from sklearn.compose import ColumnTransformer, make_column_selector
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.compose import ColumnTransformer, make_column_selector
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler
# from sklearn.pipeline import make_pipeline

# #

# def optimiser_serie_temporelle(df, date_train_end, date_test_start, params):
#     """
#     Fonction pour optimiser un modèle de série temporelle sur un DataFrame.
#     Importation du wrapper SARIMAX compatible avec scikit-learn au sein de la fonction
#     :param df: DataFrame contenant les données.
#     :param date_train_end: Date de fin de l'entraînement (format 'AAAA-MM-JJ').
#     :param date_test_start: Date de début du test (format 'AAAA-MM-JJ').
#     :param params: Dictionnaire des paramètres pour GridSearchCV.
#     :return: Le modèle optimisé, scores sur les ensembles d'entraînement, de test et de validation.
#     """
#     # Conversion des colonnes de date en datetime
#     df['date'] = pd.to_datetime(df['date'])
#     df.set_index('date', inplace=True)

#     # Séparation des données
#     train_data = df[:date_train_end]
#     test_data = df[date_test_start:]
#     val_data = df[date_train_end:date_test_start]

#     # Prétraitement des colonnes
#     numeric_preprocessing = make_pipeline(SimpleImputer(strategy='median'),
#                                           StandardScaler())
#     categorical_preprocessing = make_pipeline(
#         SimpleImputer(strategy='constant', fill_value='missing'),
#         OneHotEncoder())
#     preprocessor = ColumnTransformer(transformers=[
#         ('num', numeric_preprocessing,
#          make_column_selector(
#              dtype_include=['int64', 'float64'])),  # type: ignore
#         ('cat', categorical_preprocessing,
#          make_column_selector(dtype_include='object'))
#     ])

#     # # Création du pipeline final (à adapter avec votre modèle SARIMAX)
#     # final_pipeline = make_pipeline(
#     #     preprocessor,
#     #     DummyRegressor())  # Remplacez DummyRegressor par votre modèle

#     # Utilisation du wrapper SARIAMX
#     final_pipeline = make_pipeline(
#         preprocessor,
#         SARIMAXWrapper(order=(1, 1, 1),
#                        seasonal_order=(1, 1, 1, 12))  # Exemple d'ordre SARIMAX
#     )
#     # Définition des scores
#     scoring = {
#         'RMSE': make_scorer(mean_squared_error, squared=False),
#         'MAE': make_scorer(mean_absolute_error),
#         # Ajoutez d'autres scorers si nécessaire
#     }

#     # Optimisation des hyperparamètres avec GridSearchCV
#     tscv = TimeSeriesSplit(
#         n_splits=5)  # Pour la validation croisée dans le temps
#     grid_search = GridSearchCV(final_pipeline,
#                                param_grid=params,
#                                cv=tscv,
#                                scoring=scoring,
#                                refit='RMSE')

#     # Entraînement et optimisation
#     grid_search.fit(train_data.drop('target', axis=1), train_data['target'])

#     # Évaluation sur l'ensemble de test
#     y_pred_test = grid_search.predict(test_data.drop('target', axis=1))
#     y_pred_val = grid_search.predict(val_data.drop('target', axis=1))
#     y_pred_train = grid_search.predict(train_data.drop('target', axis=1))

#     # Calcul des scores
#     scores_test = {
#         score: scorer(test_data['target'], y_pred_test)
#         for score, scorer in scoring.items()
#     }
#     scores_val = {
#         score: scorer(val_data['target'], y_pred_val)
#         for score, scorer in scoring.items()
#     }
#     scores_train = {
#         score: scorer(train_data['target'], y_pred_train)
#         for score, scorer in scoring.items()
#     }

#     return grid_search.best_estimator_, scores_train, scores_val, scores_test


# %%
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import make_scorer, mean_squared_error, mean_absolute_error
from sklearn.base import BaseEstimator, RegressorMixin


class SARIMAXWrapper(BaseEstimator, RegressorMixin):
    """Wrapper SARIMAX pour l'intégration avec scikit-learn."""

    def __init__(self, order=(1, 0, 0), seasonal_order=(0, 0, 0, 0)):
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None

    def fit(self, X, y):
        """Adapter le modèle aux données."""
        logger.debug("Début de l'ajustement du modèle SARIMAX.")
        try:
            y = pd.Series(y).asfreq('10T', method='pad')
            self.model = SARIMAX(y,
                                 order=self.order,
                                 seasonal_order=self.seasonal_order,
                                 enforce_stationarity=False,
                                 enforce_invertibility=False)
            self.model = self.model.fit(disp=False)
        except Exception as e:
            logger.exception(
                "Erreur lors de l'ajustement du modèle SARIMAX: %s", e)
            raise
        return self

    def predict(self, X):
        """Prédire avec le modèle."""
        logger.debug("Début de la prédiction avec le modèle SARIMAX.")
        try:
            forecast = self.model.get_forecast(steps=len(X))
        except Exception as e:
            logger.exception(
                "Erreur lors de la prédiction avec le modèle SARIMAX: %s", e)
            raise
        return forecast.predicted_mean


def optimiser_serie_temporelle(df, date_train_end, date_test_start,
                               nom_colonne_predire, params):
    """Optimiser un modèle SARIMAX sur des données de série temporelle."""
    logger.debug("Début de l'optimisation du modèle SARIMAX.")
    try:
        df.index = pd.to_datetime(df.index)
        df = df.asfreq('10T')

        train_data = df[:date_train_end][nom_colonne_predire]
        test_data = df[date_test_start:][nom_colonne_predire]
        # Assurez-vous que les dates définissent correctement la plage d'entraînement
        print(f"Taille de l'ensemble d'entraînement: {len(train_data)}")

        # Ajustez le nombre de splits en fonction de la taille de l'ensemble d'entraînement
        if len(train_data
               ) > 3:  # Nombre minimum pour TimeSeriesSplit avec 3 splits
            tscv = TimeSeriesSplit(n_splits=3)
        else:
            # Réduire le nombre de splits si la taille de l'ensemble d'entraînement est petite
            tscv = TimeSeriesSplit(n_splits=1)  # Ou un autre nombre approprié

        # tscv = TimeSeriesSplit(n_splits=3)
        scoring = {
            'RMSE': make_scorer(mean_squared_error, squared=False),
            'MAE': make_scorer(mean_absolute_error)
        }

        grid_search = GridSearchCV(SARIMAXWrapper(),
                                   param_grid=params,
                                   cv=tscv,
                                   scoring=scoring,
                                   refit='RMSE')

        grid_search.fit(np.arange(len(train_data)), train_data.values)

        y_pred_test = grid_search.predict(np.arange(len(test_data)))

        scores_test = {
            'RMSE':
            mean_squared_error(test_data.values, y_pred_test, squared=False),
            'MAE':
            mean_absolute_error(test_data.values, y_pred_test)
        }
    except Exception as e:
        logger.exception("Erreur lors de l'optimisation du modèle SARIMAX: %s",
                         e)
        raise
    return grid_search.best_estimator_, scores_test, train_data, test_data, y_pred_test


# %%
df = df_normalized_12col.copy()


# %%
# Définition des hyperparameters pour`params`
nom_colonne_predire = 'vitesse_(km/h)'
# Utilisation de la fonction

#  hyperparamtres
params = {
    'order': [(1, 1, 1), (0, 1, 1)],
    'seasonal_order': [(1, 1, 1, 12), (0, 1, 1, 12)]
}
date_train_end = "2024-01-01"
date_test_start = "2024-02-02"

best_estimator, scores_test, train_data, test_data, y_pred = optimiser_serie_temporelle(
    df, date_train_end, date_test_start, nom_colonne_predire, params)

print("Meilleur estimateur:", best_estimator)
print("Scores sur l'ensemble de test:", scores_test)

# Meilleur estimateur: SARIMAXWrapper(order=(0, 1, 1), seasonal_order=(0, 1, 1, 12))
# Scores sur l'ensemble de test: {'RMSE': 12.389360468518772, 'MAE': 10.830748779134245}


# %% [markdown]
# ### courbe de prediction

# %%
import matplotlib.pyplot as plt
import pandas as pd


def plot_predictions(train_data,
                     test_data,
                     y_pred,
                     title="Prédictions vs Données Réelles"):
    """
    Trace les données d'entraînement et de test ainsi que les prédictions du modèle.

    :param train_data: DataFrame ou Series contenant les données d'entraînement.
    :param test_data: DataFrame ou Series contenant les données de test.
    :param y_pred: Les prédictions du modèle pour la période de test.
    :param title: Titre du graphique.
    """
    # Concaténer train_data et test_data pour avoir un index continu
    full_data = pd.concat([train_data, test_data])

    # Calculer l'index où commencent les données de test
    test_start = len(train_data)

    plt.figure(figsize=(14, 7))

    # Tracer les données d'entraînement
    plt.plot(full_data.index[:test_start],
             train_data,
             color='blue',
             label='Données d\'entraînement')

    # Tracer les données de test
    plt.plot(full_data.index[test_start:],
             test_data,
             color='green',
             label='Vérité terrain')

    # Tracer les prédictions sur les données de test
    # Assurez-vous que l'index de test_data et y_pred correspondent
    plt.plot(full_data.index[test_start:test_start + len(y_pred)],
             y_pred,
             color='red',
             linestyle='--',
             label='Prédictions')

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Valeur')
    plt.legend()
    plt.show()


# %%
# df=
# # Supposons que 'train_data' soit vos données d'entraînement et 'test_data' vos données de test.
# 'y_pred' sont les prédictions de votre modèle pour la période de test.
plot_predictions(train_data, test_data, y_pred,
                 "Prédictions SARIMAX vs Données Réelles")


# %% [markdown]
# ## LSTM

# %%
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


def creer_et_entrainer_lstm(X_train, y_train, epochs=10, batch_size=64):
    """
    Crée et entraîne un modèle LSTM.

    :param X_train: Données d'entraînement, déjà normalisées et préparées en séquences.
    :param y_train: Étiquettes d'entraînement.
    :param epochs: Nombre d'epochs pour l'entraînement.
    :param batch_size: Taille du batch pour l'entraînement.
    :return: Modèle LSTM entraîné.
    """
    model = Sequential([
        LSTM(50,
             activation='relu',
             input_shape=(X_train.shape[1], X_train.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train,
              y_train,
              epochs=epochs,
              batch_size=batch_size,
              verbose=2)
    return


# %% [markdown]
# ## TSFM(ZS)  modele de google

# %% [markdown]
# voir sur https://huggingface.co/datasets/monash_tsf
#
# papier:
#
# https://arxiv.org/html/2310.10688v2

# %%
import os

! pip3 install --upgrade --quiet google-cloud-aiplatform
!setx PATH "%PATH%;C:\Users\romar\AppData\Roaming\Python\Python311\Scripts"


# %%
# Code source

import requests
import os
import tensorflow as tf



url = "https://github.com/google-research/timesfm/archive/refs/heads/main.zip"

response = requests.get(url)

with open("timesfm.zip", "wb") as f:
    f.write(response.content)

# Modèles pré-entrainés


model_name = "timesfm_zs_wind"

model_url = "https://storage.googleapis.com/timesfm/models/" + model_name + ".h5"

model = tf.keras.models.load_model(model_url)


# %%
import tensorflow as tf
from timesfm import TimesFM

# Chargement du modèle TimesFM(ZS)
model = TimesFM.load("path/to/model")

# Définition des données d'entrée
features = {
    "date": tf.constant("2023-03-15 14:05:00"),
    "latitude": tf.constant(43.296482),
    "longitude": tf.constant(5.370078),
}

# Prédiction de la vitesse du vent
prediction = model.predict(features)

# Affichage de la prédiction
print(prediction)



