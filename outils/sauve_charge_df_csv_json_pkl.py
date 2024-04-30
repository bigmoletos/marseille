import os
import sys
import logging
import pandas as pd
from get_path_dossier_or_files import trouver_chemin_element_depuis_workspace
from gestion_logging import reconfigurer_logging
import logging
import pickle
# from gestion_logging import reconfigurer_logging

logger = logging.getLogger('colorlog_example')

# Configuration du logging
path_datasets = "Projet_Meteo/Datasets/meteo_france/upload_dataset_depuis_api/".replace('\\', '/')
# path_fichier_logs="projet_meteo\\Projet_Meteo\\log\\fichier.log"
params = {
    "path_datasets": path_datasets,
    # "path_fichier_logs":path_fichier_logs,
    "niveau_log": 'DEBUG',  # 'DEBUG' 'INFO' 'WARNING' 'ERROR'  'CRITICAL'
}
reconfigurer_logging(params)

# Ajout dans le path du dossier pour stocker les datasets uploadés
nom_element = "data_mobilis/upload_data_depuis_api"
path_data_mobilis_upload_data_depuis_api = trouver_chemin_element_depuis_workspace(nom_element, est_un_dossier=True)
logger.debug(f"\n path_data_mobilis_upload_data_depuis_api:\n{path_data_mobilis_upload_data_depuis_api} \n")


#------------------------------------------------------------
#------------------------------------------------------------
def conversion_dico_en_dico_flat(data, parent_key=''):
    """
    Convertit un dictionnaire potentiellement imbriqué en une liste de dictionnaires plats.
    Les clés imbriquées sont concaténées avec des underscores.
    Les listes sont déballées pour créer des lignes distinctes.
    """
    flat_dicts = []

    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                # Récurcivité pour les dictionnaires
                flat_dicts.extend(conversion_dico_en_dico_flat(v, new_key))
            elif isinstance(v, list):
                # Déballer les listes pour créer des lignes distinctes
                for item in v:
                    flat_dicts.extend(conversion_dico_en_dico_flat(item, new_key))
            else:
                flat_dicts.append({new_key: v})
    elif isinstance(data, list):
        # Si la donnée de base est une liste
        for item in data:
            flat_dicts.extend(conversion_dico_en_dico_flat(item, parent_key))
    else:
        # Cas de base, si ce n'est ni une liste ni un dictionnaire
        return [{parent_key: data}]
    logger.debug(f"flat_dicts:{flat_dicts}")
    return flat_dicts


#------------------------------------------------------------
#------------------------------------------------------------


def save_dataframe(df, df_name, path, index=False):
    """
    Sauvegarde le DataFrame au format CSV, JSON et pickle.

    Paramètres :
    - df (DataFrame) : DataFrame à sauvegarder. S'il n'est pas du type DataFrame, il sera converti.
    - df_name (str) : Nom de base du fichier pour la sauvegarde.
    - path (str) : Chemin du dossier où les fichiers seront sauvegardés.
    """
    try:
        # Conversion de `df` en DataFrame si nécessaire
        if isinstance(df, dict):
            # applatissement du dico
            df_flat = conversion_dico_en_dico_flat(df)
            # Préparation des données pour la conversion en DataFrame
            # rows = []
            # for station_id, details in df.items():0.2
            #     for fichier in details['fichiers']:
            #         rows.append({'station_id': station_id, 'fichier': fichier})
            df = pd.DataFrame.from_dict(df_flat)
            logger.debug(f"Converti de dict à DataFrame: {df.describe()}")
        elif isinstance(df, list):
            df = pd.DataFrame(df)
            logger.debug("Converti de list à DataFrame")
        elif not isinstance(df, pd.DataFrame):
            logger.error("L'objet à sauvegarder n'est pas un DataFrame, un dictionnaire, ou une liste.")
            raise ValueError("L'objet à sauvegarder doit être un DataFrame pandas, un dictionnaire ou une liste.")

        # Correction et construction des chemins de fichier
        file_basename = os.path.join(path, f"df_{df_name}").replace('\\', '/')
        logger.debug(f"Nom de base du fichier défini sur : {file_basename}")

        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(file_basename), exist_ok=True)

        # Sauvegarde en différents formats
        df.to_csv(f"{file_basename}.csv", index=index, sep=',', encoding='utf-8')
        logger.debug(f"DataFrame sauvegardé en CSV à : {file_basename}.csv")

        df.to_json(f"{file_basename}.json", date_format='iso', index=index, orient='split')
        logger.debug(f"DataFrame sauvegardé en JSON à : {file_basename}.json")

        df.to_pickle(f"{file_basename}.pkl")
        logger.debug(f"DataFrame sauvegardé en Pickle à : {file_basename}.pkl")

    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des fichiers : {e}", exc_info=True)
        raise


#------------------------------------------------------------
#------------------------------------------------------------


def format_and_save_dataframe(df, df_name, path):
    """
    Formate le DataFrame en convertissant les vitesses de nœuds et mètres par seconde en km/h,
    Formate les Kelvin en Celsius
    supprimant les colonnes inutiles, ajustant le format de la date, et en arrondissant les valeurs numériques.
    Sauvegarde le DataFrame au format CSV, JSON et pickle.

    Paramètres :
    - df (DataFrame) : DataFrame à formater.
    - df_name (str) : Nom de base du fichier pour la sauvegarde.
    - path (str) : Chemin du dossier où les fichiers seront sauvegardés.

    Retourne :
    - DataFrame formaté.
    """
    try:
        # Supprimer la colonne 'series_name' si elle existe
        if 'series_name' in df.columns:
            df.drop(columns=['series_name'], inplace=True)
        # Supprimer la colonne 'date_timestamp' si elle existe
        if 'date_timestamp' in df.columns:
            df.drop(columns=['date_timestamp'], inplace=True)
        # Supprimer la colonne 'Date Timestamp [UTC]' si elle existe
        if 'Date Timestamp [UTC]' in df.columns:
            df.drop(columns=['Date Timestamp [UTC]'], inplace=True)
        # Supprimer la colonne 'direction_string_(txt)' si elle existe
        if 'direction_string_(txt)' in df.columns:
            df.drop(columns=['direction_string_(txt)'], inplace=True)

        # Convertir et formater la colonne 'date'
        # df['date'] = pd.to_datetime(df['date'], format='%Y%m%d%H')

        # Vérifier si la colonne 'date' est déjà au format souhaité
        # # Si elle est de type 'object' (chaîne de caractères), on suppose qu'elle peut déjà être au bon format
        # if 'date' in df.columns:
        #     logger.debug(f"\n ******la colonne date est presente, {df['date'].dtype} ******")
        #     if df['date'].dtype == 'object':
        #         try:
        #             # convertir en datetime pour vérifier le format
        #             # pd.to_datetime(df['date'], format='%Y%m%d%H', errors='raise')
        #             df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        #             logger.debug(f"\n ******la colonne date est presente, {df['date'].dtype}  ******")
        #             # pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        #             # Si aucune erreur, la colonne est déjà au format correct, aucune action nécessaire
        #         except ValueError as e:
        #             logger.critical(f"\n  le format n'est pas correct ou la colonne contient des valeurs qui ne correspondent pas au format:\n{e} ")
        #             pass
        #     else:
        #         # Si la colonne 'date' n'est pas de type 'object', on tente de la convertir
        #         # df['date'] = pd.to_datetime(df['date'],  errors='coerce')
        #         # df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        #         # pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        #         # Si la colonne 'date' est stockée comme des entiers (ou autre non-object), convertis les valeurs en chaînes d'abord
        #         # Puis convertis au format datetime
        #         df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d%H', errors='coerce')

        if 'date' in df.columns:
            logger.debug(f"La colonne date est présente, type actuel: {df['date'].dtype}")
            try:
                # Convertir systématiquement en chaîne de caractères avant la conversion datetime
                df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d%H%M%S', errors='coerce')
                logger.debug(f"Conversion tentative avec le format '%Y%m%d%H%M%S'")
            except Exception as e:
                logger.debug(f"Erreur lors de la conversion de la colonne date: {e}")

            # Vérifier après la conversion si des valeurs n'ont pas pu être converties
            if df['date'].isnull().any():
                logger.debug("Certaines dates n'ont pas pu être converties et sont définies comme NaT.")
            else:
                logger.info("Toutes les dates ont été converties avec succès.")

            # Contrôle des premières dates converties
            logger.debug(f"Date après conversion:\n{df['date'].head(2)}")
        else:
            logger.debug("La colonne 'date' n'est pas présente dans le DataFrame.")

        # Après la conversion, vérifie si des valeurs n'ont pas pu être converties (elles apparaîtront comme NaT)
        if df['date'].isnull().any():
            logger.debug("Certaines dates n'ont pas pu être converties et sont définies comme NaT.")
        # controle date
        logger.debug(f"\n date:\n{df['date'].head(2)} ")
        # Créer une copie pour éviter de modifier le DataFrame original lors de l'itération
        # Première boucle pour renommer et convertir les unités
        for col in list(df.columns):  # Utilisez list(df.columns) pour éviter les problèmes pendant la suppression
            logger.debug(f" df.columns.to_list()1 {df.columns.to_list()}")
            logger.debug(f" col1 {col}")
            # logger.debug(f" col1 {col}")
            # ['kn' , 'm/s' ,'nd']
            # Conversion des colonnes en colonnes numérique avec remplacement des , par des  .
            if 'kn' in col or 'm/s' in col or 'nds' in col:
                try:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
                except:
                    df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')

                conversion_factor = 1.852 if 'kn' in col else 3.6
                new_col_name = col.replace('kn', 'km/h').replace('m/s', 'km/h').replace('nds', 'km/h')
                df[new_col_name] = df[col] * conversion_factor
                df.drop(columns=[col], inplace=True)

                # if '(°K)' in col:

                #     try:
                #         logger.debug(f" traitement de la col temperature our la conversion des kelvins en celsus {col}")
                #         # Conversion des valeurs de la colonne de Kelvin en Celsus
                #         conversion_factor = 273.15
                #         new_col_name = col.replace('°K', '°C')
                #         df[new_col_name] = df[col] - conversion_factor
                #         logger.critical(f" conversion de la colonne {col}- {conversion_factor} donne en Celsius {new_col_name}")
                #         df.drop(columns=[col], inplace=True)

                #     except Exception as e:
                #         logger.error(f"\n erreur de conversion en kelvin:\n{e} ")

        if 'temperature_(°K)' in df.columns:
            # if '(°K)' in df.columns:
            try:
                logger.debug(f"Traitement de la colonne temperature pour la conversion de Kelvin en Celsus: {col}")
                # conversion de la colonne en numerique
                col = 'temperature_(°K)'
                try:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
                except:
                    df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
                # df['temperature_(°K)'] = pd.to_numeric(df['temperature_(°K)'], errors='coerce')

                # Conversion des valeurs de la colonne de Kelvin en Celsius
                # conversion_factor = 273.15
                # new_col_name = 'temperature_(°C)'
                # df[new_col_name] = df['temperature_(°K)'] - conversion_factor

                # Convertir les températures de Kelvin en Celsius
                df['temperature_(°C)'] = df['temperature_(°K)'].apply(lambda x: x - 273.15)

                # Affichage des premières lignes pour vérifier la conversion
                print(df[['temperature_(°K)', 'temperature_(°C)']].head(2))

                logger.debug(f" traitement de la col temperature our la conversion des kelvins en celsus ")
                logger.debug(f"Conversion de la colonne 'temperature_(°K)' en Celsius terminée.")

                #Suppression de la colonne car remplacée par la temperature en celsus
                df.drop(columns=['temperature_(°K)'], inplace=True)

            except Exception as e:
                logger.error(f"Erreur de conversion de Kelvin en Celsius: {e}")
        else:
            logger.debug(f"La colonne 'temperature_(°K)' n'existe pas dans le DataFrame actuel.")

        # Deuxième boucle pour la conversion des colonnes string restantes en numérique
        # Préparation d'une liste des colonnes à exclure de la conversion numérique
        cols_to_exclude = ['station', 'poste', 'POSTE', 'DATE', 'date', 'Nom français non fourni', 'inconnu']

        # Itération sur une copie stable des noms de colonnes
        for col in df.columns.to_list():  # Création d'une liste pour éviter les modifications pendant l'itération
            logger.debug(f" df.columns.to_list()2: {df.columns.to_list()}")
            logger.debug(f" col2: {col}")
            # Vérification que la colonne n'est pas dans la liste d'exclusion
            if col not in cols_to_exclude:
                # Tentative de conversion des colonnes en type numérique, si la colonne est de type object
                if df[col].dtype == object:
                    logger.debug(f"La colonne {col} est du type object.")
                    converted = False  # Indicateur pour vérifier si la conversion a réussi
                    try:
                        # Première tentative de conversion
                        df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='raise')
                        converted = True  # Marquer la conversion comme réussie
                    except Exception as e:
                        logger.error(f"Première tentative de conversion en nombre échouée pour la colonne {col}, erreur: {e}")

                    # Si la première conversion échoue, essayer une seconde méthode
                    if not converted:
                        try:
                            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='raise')
                        except Exception as e:
                            logger.error(f"Seconde tentative de conversion en nombre échouée pour la colonne {col}, erreur: {e}")

        # Arrondir les valeurs numériques à deux chiffres après la virgule
        #  Arrondir toutes les colonnes en même temps
        df = df.round(3)
        logger.debug(f"df: {df.head(2)}")

        # Construction des chemins de fichier
        # Correction du chemin pour éviter les erreurs d'échappement
        file_basename = f"{path}/df_{df_name}"
        logger.info(f"File basename set to: {file_basename}")

        # Remplacer les backslashes par des forward slashes pour éviter les erreurs d'échappement Unicode
        file_basename = file_basename.replace('\\', '/')
        # Enregistrement du df sous différents formats
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(file_basename), exist_ok=True)

        # Chemins de fichier pour chaque format
        csv_path = f"{file_basename}.csv"
        json_path = f"{file_basename}.json"
        pickle_path = f"{file_basename}.pkl"
        try:
            # Sauvegarde en CSV
            df.to_csv(csv_path, index=False)
            logger.debug(f"DataFrame saved to CSV at {csv_path}")

            # Sauvegarde en JSON
            df.to_json(json_path, date_format='iso', orient='split')
            logger.debug(f"DataFrame saved to JSON at {json_path}")

            # Sauvegarde en format Pickle
            df.to_pickle(pickle_path)
            logger.debug(f"DataFrame saved to Pickle at {pickle_path}")

        except Exception as e:
            logger.error(f"An error occurred while saving files: {e}")

        return df

    except Exception as e:
        logger.error(f"Erreur lors du formatage et de la sauvergarde du df: {e}")
        raise  # Relancer l'exception pour notifier l'erreur


#------------------------------------------------------------
#------------------------------------------------------------


def load_dataframe(df_name, path, format_type='csv', sep=","):
    """
    Charge globalement un DataFrame à partir d'un fichier en spécifiant le format souhaité.
    Paramètres :
    - df_name (str) : Nom de base du DataFrame à charger (sans extension).
    - path (str) : Chemin du dossier contenant le fichier.
    - format_type (str) : Format du fichier ('csv', 'json', 'pkl').
    Retourne :
    - DataFrame chargé.
    """
    # Variable globale pour stocker le DataFrame
    global_df = None
    # Construction du chemin complet du fichier
    file_basename = os.path.join(path, df_name)
    logger.debug(f" file_basename:  {file_basename}")

    try:
        # Chargement du DataFrame en fonction du format spécifié
        if format_type == 'csv':
            filepath = f"{file_basename}.csv"
            df = pd.read_csv(filepath, sep=sep)
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
            raise ValueError("Unsupported file format. Please choose 'csv', 'json', or 'h5'.")
        global_df = df  # Met à jour la variable globale avec le DataFrame chargé
        logger.info(f"DataFrame loaded from {format_type.upper()} at {filepath}")

        return global_df
    except Exception as e:
        logger.error(f"An error occurred while loading the file: {e}")
        raise e


# def charger_all_dataframes(dossier, sep=","):
#     """
#     Charge une copie des DataFrames depuis le dossier spécifié.

#     :param dossier: Chemin du dossier d'où charger les DataFrames.
#     :return: Dictionnaire contenant les DataFrames chargés.
#     """
#     dataframes = {}
#     global_vars = globals()  # Accéder aux variables globales
#     try:
#         for filename in os.listdir(dossier):
#             if filename.endswith(".csv"):
#                 # Enlever l'extension .csv pour obtenir le nom du DataFrame
#                 df_name = filename[:-4]
#                 # Construire le chemin complet du fichier
#                 df_path = os.path.join(dossier, filename)
#                 df = pd.read_csv(df_path, sep=sep)
#                 dataframes[df_name] = df.copy()
#                 # Définir le DataFrame comme variable globale
#                 global_vars[df_name] = df.copy()
#                 logger.info(
#                     f"Le DataFrame {df_name} a été chargé avec succès, depuis le dossier: {dossier} "
#                 )
#         return dataframes
#     except Exception as e:
#         logger.error(
#             f"Une erreur s'est produite lors du chargement des DataFrames depuis le dossier: {dossier} \n message: {e}"
#         )
#         return None


def charger_all_dataframes(dossier, default_format="pkl", sep=","):
    """
    Charge des DataFrames depuis le dossier spécifié, en filtrant pour charger uniquement les fichiers du format spécifié.

    :param dossier: Chemin du dossier d'où charger les DataFrames.
    :param default_format: Format des fichiers à charger ('csv', 'txt','json', 'pkl').
    :param sep: Séparateur de champ pour les fichiers CSV (par défaut, ',').
    :return: Dictionnaire contenant les DataFrames chargés dans le format spécifié.
    """
    dataframes = {}
    extension_map = {'txt': '.txt', 'csv': '.csv', 'json': '.json', 'pkl': '.pkl'}

    try:
        for filename in os.listdir(dossier):
            file_path = os.path.join(dossier, filename)
            _, file_extension = os.path.splitext(filename)

            # Vérifier si l'extension du fichier correspond au format désiré
            if file_extension.lower() == extension_map[default_format]:
                df_name = filename[:-(len(file_extension))]

                if default_format in ['csv', 'txt']:
                    df = pd.read_csv(file_path, sep=sep)
                elif default_format == 'json':
                    df = pd.read_json(file_path, orient='split')
                elif default_format == 'pkl':
                    df = pd.read_pickle(file_path)

                # Ajouter le DataFrame chargé au dictionnaire
                dataframes[df_name] = df
                logger.info(f"DataFrame {df_name} loaded from {default_format.upper()} at {file_path}")

        return dataframes
    except Exception as e:
        logger.error(f"Erreur lors du chargement des DataFrames depuis {dossier} : {e}")
        return None


# def sauve_charge_pickle(path, name_file=None, true_for_load=True, is_file=False):
#     """
#     Fonction pour sauvegarder ou charger des objets Python depuis/vers des fichiers pickle.
#     Charge ou sauvegarde un fichier .pkl si is_file=True. Charge tous les fichiers .pkl dans un répertoire ou sauvegarde l'objet dans le répertoire spécifié si is_file=False.

#     Args:
#         path (str): Chemin vers le fichier ou le répertoire.
#         objet (object, optional): Objet Python à sauvegarder. Requis si true_for_load=False.
#         true_for_load (bool): Si True, charge les objets depuis pickle. Sinon, sauvegarde les objets. Par défaut à True.
#         is_file (bool): Si True, traite `path` comme le chemin d'un fichier unique. Sinon, traite `path` comme un répertoire. Par défaut à False.
#     """
#     if true_for_load:
#         if is_file:
#             if not path.endswith('.pkl'):
#                 logger.error("L'extension du fichier doit être '.pkl'. Veuillez ajouter l'extension au chemin.")
#                 return None
#             try:
#                 with open(path, 'rb') as file:
#                     obj = pickle.load(file)
#                 logger.info(f"Objet chargé avec succès depuis {path}")
#                 return obj
#             except Exception as e:
#                 logger.error(f"Erreur lors du chargement du fichier {path}: {e}")
#                 return None
#         else:
#             objets_charges = {}
#             if os.path.isdir(path):
#                 for filename in os.listdir(path):
#                     if filename.endswith('.pkl'):
#                         full_path = os.path.join(path, filename)
#                         try:
#                             with open(full_path, 'rb') as file:
#                                 obj = pickle.load(file)
#                             logger.info(f"Objet chargé avec succès depuis {full_path}")
#                             objets_charges[filename] = obj
#                         except Exception as e:
#                             logger.error(f"Erreur lors du chargement du fichier {full_path}: {e}")
#                 return objets_charges
#             else:
#                 logger.error(f"Le chemin spécifié n'est pas un répertoire valide: {path}")
#                 return None
#     else:
#         # Sauvegarde d'un objet dans un fichier pickle
#         if is_file:
#             try:
#                 with open(path, 'wb') as file:
#                     pickle.dump(name_file, file)
#                 logger.info(f"Objet sauvegardé avec succès sous {path}")
#             except Exception as e:
#                 logger.error(f"Erreur lors de la sauvegarde de l'objet sous {path}: {e}")
#         else:
#             logger.error("La sauvegarde d'un objet dans un répertoire sans spécifier un nom de fichier n'est pas supportée.")




def sauve_charge_pickle(path, name_file=None, true_for_load=True, is_file=False):
    """
    Fonction pour sauvegarder ou charger des name_files Python depuis/vers des fichiers pickle.
    Charge ou sauvegarde un fichier .pkl si is_file=True. Charge tous les fichiers .pkl dans un répertoire ou sauvegarde l'name_file dans le répertoire spécifié si is_file=False.

    Args:
        path (str): Chemin vers le fichier ou le répertoire.
        name_file (object, optional): name_file Python à sauvegarder. Requis si true_for_load=False.
        true_for_load (bool): Si True, charge les name_files depuis pickle. Sinon, sauvegarde les name_files. Par défaut à True.
        is_file (bool): Si True, traite `path` comme le chemin d'un fichier unique. Sinon, traite `path` comme un répertoire. Par défaut à False.
    """
    if true_for_load:
        if is_file:
            try:
                with open(path, 'rb') as file:
                    obj = pickle.load(file)
                logger.info(f"name_file chargé avec succès depuis {path}")
                return obj
            except Exception as e:
                logger.error(f"Erreur lors du chargement du fichier {path}: {e}")
                return None
        else:
            name_files_charges = {}
            try:
                for filename in os.listdir(path):
                    if filename.endswith('.pkl'):
                        full_path = os.path.join(path, filename)
                        with open(full_path, 'rb') as file:
                            obj = pickle.load(file)
                        name_files_charges[filename] = obj
                logger.info("name_files chargés avec succès depuis le répertoire")
                return name_files_charges
            except Exception as e:
                logger.error(f"Erreur lors du chargement des fichiers dans {path}: {e}")
                return None
    else:
        if is_file:
            # Vérifier si le fichier existe et ajouter un suffixe "_x" si nécessaire
            base_path, extension = os.path.splitext(path)
            counter = 1
            while os.path.exists(path):
                path = f"{base_path}_{counter}{extension}"
                counter += 1

            try:
                with open(path, 'wb') as file:
                    pickle.dump(name_file, file)
                logger.info(f"name_file sauvegardé avec succès sous {path}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde de l'name_file sous {path}: {e}")
        else:
            logger.error("La sauvegarde d'un name_file dans un répertoire sans spécifier un nom de fichier n'est pas supportée.")
