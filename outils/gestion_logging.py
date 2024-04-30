# pylint: disable=all
from logging.handlers import RotatingFileHandler
import logging
import os
import colorlog
import warnings
import time
from pathlib import Path
from datetime import datetime
from get_path_dossier_or_files import trouver_chemin_element_depuis_workspace

logger = logging.getLogger('colorlog_example')


# def trouver_chemin_fichier(nom_fichier: str) -> Path:
#     """
#     Trouve et retourne le chemin absolu d'un fichier spécifié par son nom dans l'arborescence du workspace.

#     Args:
#         nom_fichier (str): Le nom du fichier à trouver.

#     Returns:
#         Path: Le chemin absolu vers le fichier spécifié.

#     Raises:
#         ValueError: Si le fichier spécifié n'est pas trouvé.

#     Exemple d'utilisation:
#     >>> trouver_chemin_fichier("fichier.log")  # Doctest: +SKIP
#     """
#     # Nom du dossier racine de votre workspace (à adapter selon votre configuration)
#     nom_dossier_workspace = "Projet_Meteo"

#     chemin_courant = Path().resolve()
#     chemin_workspace = None

#     # Parcourir les dossiers parents pour trouver le dossier racine du workspace
#     for parent in chemin_courant.parents:
#         if parent.name == nom_dossier_workspace:
#             chemin_workspace = parent
#             break

#     if chemin_workspace is not None:
#         # Recherche récursive du fichier dans le workspace
#         for fichier in chemin_workspace.rglob(nom_fichier):
#             logger.debug(f"Fichier trouvé : {fichier}")
#             return fichier
#         logger.error(f"Fichier '{nom_fichier}' non trouvé dans le workspace '{
#                       chemin_workspace}'.")
#         raise ValueError(f"Fichier '{nom_fichier}' non trouvé dans le workspace '{
#                          chemin_workspace}'.")
#     else:
#         logger.error(f"Le dossier workspace '{
#                       nom_dossier_workspace}' n'a pas été trouvé dans l'arborescence des dossiers actuelle.")
#         raise ValueError(f"Le dossier workspace '{
#                          nom_dossier_workspace}' n'a pas été trouvé dans l'arborescence des dossiers actuelle.")


# # Configuration basique du logging
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(message)s')




class CustomFormatter(logging.Formatter):
    """
    Un formateur personnalisé pour les logs qui inclut le fuseau horaire local dans le timestamp.

    Cette classe étend logging.Formatter et surcharge la méthode formatTime pour utiliser
    la fonction customTime, qui ajoute le décalage horaire local à la représentation de la date et l'heure.
    """
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.datefmt = datefmt

    def formatTime(self, record, datefmt=None):
        """
        Surcharge de la méthode formatTime pour utiliser la fonction customTime.

        :param record: L'enregistrement de log qui est en train d'être formaté.
        :param datefmt: Format de date optionnel, non utilisé dans cette surcharge.
        :return: Chaîne de caractères représentant la date et l'heure actuelles avec le décalage horaire local.
        """
        # Utilisation de customTime pour générer le timestamp avec le fuseau horaire local
        utc_offset = time.localtime().tm_gmtoff / 3600
        utc_offset_str = f"+{int(utc_offset):02d}:00" if utc_offset > 0 else f"{int(utc_offset):02d}:00"
        return datetime.now().strftime(f'%Y-%m-%dT%H:%M{utc_offset_str}')

def reconfigurer_logging(params):
    """
    Reconfigure le logging avec le niveau et le format spécifiés à partir du dictionnaire params,
    en ajoutant des couleurs au logs selon leur niveau de gravité.
    """
    # Assurez-vous que 'niveau_log' et 'format_log' sont définis dans params
    niveau = params['niveau_log'].upper()

    # format_log = params['format_log']
    # format_log_file = params['format_log_file']

    format_log = "%(log_color)s-log:%(asctime)s\n%(levelname)s>>>fichier=%(filename)s:ligne=%(lineno)d:fonction=%(funcName)s():'%(message)s'"
    format_log_file = ('[%(asctime)s|%(levelname)s|]>>>>>>>>> '
                       'fichier=%(filename)s| chemin=%(pathname)s|ligne=%(lineno)d|'
                       'fonction=%(funcName)s()|'
                       'processus=%(process)d|nom_processus=%(processName)s|'
                       'thread=%(threadName)s|temps_rel=%(relativeCreated)d|'
                       'message={%(message)s}|exception={%(exc_info)s}')

    # format='%(asctime)s:%(levelname)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'  # '%(asctime)s - %(levelname)s - %(message)s'

    # Définition du format de date pour la console
    datefmt_perso = '%d-%b-%Y à %Hh%M'
    # Définition du format de date pour le fichier de log
    datefmt_perso_file = '%Y-%m-%dT%H:%M%z'

    # logger = logging.getLogger()  # Obtient le logger racine
    logger.debug(f" niveau de log {niveau}")
    logger.debug(f" logger {logger}")


    # Créer un logger spécifique au lieu d'utiliser le logger global
    # logger = logging.getLogger('colorlog_example')
    logger.handlers = []  # Supprimer les handlers existants

    # Créer un formatteur avec colorlog
    formatter = colorlog.ColoredFormatter(
        format_log,
        datefmt=datefmt_perso,  # format de date
        log_colors={
            # 'DEBUG': 'bold,purple,bg_bold_yellow',
            'DEBUG': 'bold,green',
            'INFO': 'bold,purple',
            # 'INFO': 'bold,light_green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'purple,bg_bold_yellow',
        },
        secondary_log_colors={},
        style='%')

    # Formatteur sans couleur pour le fichier de log
    # file_formatter = logging.Formatter(format_log_file, datefmt=datefmt_perso_file)
    file_formatter = CustomFormatter(format_log_file,
                                     datefmt=datefmt_perso_file)

    # Créer un gestionnaire de flux qui utilise STDOUT
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Définir le niveau du gestionnaire
    stream_handler.setLevel(niveau)

    # Obtenir le logger racine et le configurer
    logger.handlers = []  # Supprime les gestionnaires existants
    logger.setLevel(niveau)  # Définit le niveau du logger
    logger.addHandler(stream_handler)  # Ajoute le nouveau gestionnaire

    # # Obtenir le chemin du répertoire où se trouve ce script
    chemin_du_script = os.path.dirname(os.path.realpath(__file__))
    logger.debug(f"chemin_du_script  {chemin_du_script}")
    # # Remonter jusqu'au répertoire racine du projet (depuis le répertoire 'outils')
    chemin_racine_projet = os.path.join(chemin_du_script, '..', '..')
    logger.debug(f"chemin_racine_projet  {chemin_racine_projet}")
    # # Normaliser le chemin pour résoudre les '..'
    chemin_racine_projet = os.path.normpath(chemin_racine_projet)
    logger.debug(f"chemin_racine_projet  {chemin_racine_projet}")
    # # Définir le chemin du fichier log relatif à la racine du projet
    # chemin_fichier_log = os.path.join(chemin_racine_projet, 'log', 'fichier.log')
    # logger.debug(f"chemin_fichier_log  {chemin_fichier_log}")

    # Utilisation de la fonction: trouver_chemin_fichier("fichier.log")
    path_fichier_log = trouver_chemin_element_depuis_workspace(
        "fichier.log", est_un_dossier=False)
    # path_fichier_log = trouver_chemin_fichier("fichier.log")
    chemin_fichier_log = path_fichier_log
    logger.info(f"path_fichier_log via fonction    {path_fichier_log}")

    try:
        # Création du dossier de log si nécessaire
        os.makedirs(os.path.dirname(chemin_fichier_log), exist_ok=True)
    except OSError as e:
        logger.error(f"Erreur lors de la création du dossier de log : {e}")
        # Utilisation d'un chemin de repli simple dans le cas d'une erreur
        chemin_fichier_log_repli = os.path.join(chemin_racine_projet,
                                                'Projet_Meteo', 'log',
                                                'fichier.log')
        logger.info(
            f"chemin_fichier_log de repli utilisé : {chemin_fichier_log_repli}"
        )
        # Mettre à jour chemin_fichier_log pour utiliser le chemin de repli
        chemin_fichier_log = chemin_fichier_log_repli

    # Parametrage fichier de log
    max_taille_fichier = 100 * 1024 * 1024  # 10 Mo,
    nb_fichiers_backup = 10  # Garde 5 fichiers log en backup,
    logger.debug(
        f"max_taille_fichier  {max_taille_fichier},nb_fichiers_backup {nb_fichiers_backup}"
    )
    # print(f"max_taille_fichier  {max_taille_fichier},nb_fichiers_backup {nb_fichiers_backup}")

    try:
        # Configuration du RotatingFileHandler avec le chemin de fichier

        handler = RotatingFileHandler(chemin_fichier_log,
                                      mode='a',
                                      maxBytes=max_taille_fichier,
                                      backupCount=nb_fichiers_backup,
                                      encoding='utf-8')
        # formatter = logging.Formatter(file_formatter)
        handler.setFormatter(file_formatter)
        logger.addHandler(handler)
    except Exception as e:
        logger.error(
            f"Erreur lors de la configuration du handler de log : {e}")

    # Fonction pour rediriger les avertissements vers le logger
    def warning_to_logging(message,
                           category,
                           filename,
                           lineno,
                           file=None,
                           line=None):
        log_message = f'{category.__name__} in {filename}:{lineno}: {message}'
        if file is not None:
            log_message += f' | File: {file}'
        if line is not None:
            log_message += f' | Line: {line}'
        logger.warning(log_message)
        # logger.warning(f'{category.__name__} in {filename}:{lineno}: {message}')

    # Configurer warnings pour utiliser warning_to_logging
    warnings.showwarning = warning_to_logging

    # Configurer le logging des avertissements au même niveau que le logger
    logging.captureWarnings(True)

    return logger

    # %d : jour du mois en deux chiffres (25)
    # %m : mois en deux chiffres (02)
    # %Y : année en quatre chiffres (2024)
    # %h : heure au format 24h en deux chiffres (17)
    # %M : minute en deux chiffres (27)
    # %S : seconde en deux chiffres (41)
