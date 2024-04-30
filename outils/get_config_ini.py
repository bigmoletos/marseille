# pylint: disable=all
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import configparser
import re
import logging
import colorlog
from urllib.parse import quote
from outils.gestion_logging import reconfigurer_logging


# Configuration du logger
# logger.basicConfig(level=logger.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger('colorlog_example')

def lire_config_et_imprimer_cles_valeurs(chemin_fichier, theme):
    """
    Vérifie l'existence du fichier de configuration et lit les sections correspondant au thème donné.
    Logge et retourne les clés et leurs valeurs, y compris les valeurs encodées pour les clés contenant 'api_key'.
    Lit le fichier config.ini spécifié, recherche des sections contenant le thème donné
    en utilisant une expression régulière. Imprime le nom des clés et leurs valeurs présentes
    dans ces sections. Encode uniquement les valeurs des clés contenant 'api_key' pour une utilisation dans les URL,

    :param chemin_fichier: Chemin d'accès au fichier config.ini.
    :param theme: Thème pour filtrer les sections du fichier de configuration.
    :return: Dictionnaire des clés et leurs valeurs, avec encodage pour 'api_key'.
    """
    config = configparser.ConfigParser()
    cles_valeurs_trouvees = {}  # Dictionnaire pour stocker les résultats

    try:
        # Vérification de l'existence du fichier de configuration
        try:
            if not Path(chemin_fichier).is_file():
                logger.debug(f"Le chemin de '{chemin_fichier}' n'est pas correct.")
                raise FileNotFoundError(f"Le fichier '{chemin_fichier}' n'existe pas.")
        except FileNotFoundError as e:
            logger.error( f"verifiez le chemin de votre fichier config.ini   {e}"   )
            # print(e)
            return {}

        config.read(chemin_fichier)
        theme_pattern = re.compile(theme, re.IGNORECASE)  # Compilation du pattern, insensible à la casse

        sections_trouvees = False  # Flag pour vérifier si des sections correspondantes ont été trouvées
        for section in config.sections():
            if theme_pattern.search(section):
                sections_trouvees = True
                logger.info(f"Section correspondant au thème '{theme}': [{section}]")
                for cle, valeur in config[section].items():
                    # logger.debug(f"Clé: {cle}, Valeur: {valeur}")
                    cles_valeurs_trouvees[cle] = valeur
                    if 'api_key' in cle:
                        valeur_encodee = quote(valeur)
                        cles_valeurs_trouvees[f"{cle}_encoded"] = valeur_encodee

        if not sections_trouvees:
            raise ValueError(f"Aucune section correspondant au thème '{theme}' n'a été trouvée.")

    except ValueError as e:
        logger.error(e)
        # print(e)
        return {}

    except Exception as e:
        logger.error(f"Erreur inattendue lors de la lecture du fichier {chemin_fichier}: {e}")
        # print(f"Erreur inattendue: {e}")

    return cles_valeurs_trouvees




# #  récuperation de l'url de telechargement
# url_donnees_climatiques_telechargement=cles_valeurs_trouvees["url_donnees_climatiques_telechargement"].strip("'")
# logger.debug(f"\n ===== api_key_donnees_climatiques ======:\n{api_key_donnees_climatiques} \n")
# logger.debug(f"\n ====== base_url_donnees_climatiques  ======:\n{base_url_donnees_climatiques} \n")
# logger.debug(f"\n ====== endpoint_donnees_climatiques_commande  ======:\n{endpoint_donnees_climatiques_commande} \n")
# logger.debug(f"\n ===== url_donnees_climatiques_telechargement  ======:\n{url_donnees_climatiques_telechargement} \n")
