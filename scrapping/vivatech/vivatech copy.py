import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import unidecode
import time

# Configuration du logger
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def nettoyer_nom_partenaire(nom):
    """
    Nettoyer le nom du partenaire en suivant les règles spécifiées :
    - Mettre tout en minuscule
    - Supprimer les accents
    - Supprimer les caractères spéciaux sauf les points
    - Remplacer les points entre deux lettres et les espaces par un tiret
    - Supprimer les points de début et de fin de ligne

    :param nom: Nom du partenaire
    :return: Nom nettoyé
    """
    nom = nom.lower()  # Mettre tout en minuscule
    nom = unidecode.unidecode(nom)  # Supprimer les accents
    nom = re.sub(r'[^a-z0-9. ]', '', nom)  # Supprimer les caractères spéciaux sauf les points
    nom = re.sub(r'(?<=[a-z])\.(?=[a-z])', '-', nom)  # Remplacer les points entre deux lettres par un tiret
    nom = nom.replace(' ', '-')  # Remplacer les espaces par un tiret
    nom = nom.strip('.')  # Supprimer les points de début et de fin de ligne

    # enregistrement du fichier des partenaires avec noms corrigés
    fichier_partners_corrected = []
    df_fichier_partners_corrected = []
    fichier_partners_corrected.append(nom)
    # df_fichier_partners_corrected = pd.DataFrame(noms_partenaires)
    df_fichier_partners_corrected = pd.DataFrame(fichier_partners_corrected)
    df_fichier_partners_corrected.to_csv("fichier_partners_corrected.csv", index=False, encoding='utf-8')

    return nom, df_fichier_partners_corrected


def lire_noms_partenaires(fichier_csv, fichier_csv_initial):
    """
    Lire les noms des partenaires à partir d'un fichier CSV et les nettoyer.

    :param fichier_csv: Chemin vers le fichier CSV contenant les noms des partenaires
    :return: Liste des noms des partenaires nettoyés
    """
    try:
        if not os.path.exists(fichier_csv):
            logger.error(f"Le fichier {fichier_csv} n'existe pas.")
            raise FileNotFoundError(f"Le fichier {fichier_csv} n'existe pas.")

        df_initial = pd.read_csv(fichier_csv_initial)
        df = pd.read_csv(fichier_csv)

        # pour tester on ne prend que 5 noms
        # df = df.iloc[:5]
        # df = df.iloc[:2]
        logger.debug(f"Colonnes du fichier CSV: {df.columns.tolist()}")

        noms_partenaires = df[df.columns[0]].apply(nettoyer_nom_partenaire).tolist()
        noms_partenaires_depuis_fichier_corrigé = df_initial[df_initial.columns[0]].tolist()

        logger.debug(f"Noms des partenaires lus: {noms_partenaires}")

        return noms_partenaires, noms_partenaires_depuis_fichier_corrigé
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier CSV: {e}")
        raise


def construire_url_partenaire(nom, url_base="https://vivatechnology.com/partners/"):
    """
    Construire l'URL complète du partenaire en utilisant le nom du partenaire.

    :param nom: Nom du partenaire
    :param url_base: URL de base
    :return: URL complète
    """
    try:
        url_complet = f"{url_base}{nom}"
        logger.debug(f"URL construite pour {nom}: {url_complet}")
        return url_complet
    except Exception as e:
        logger.error(f"Erreur lors de la construction de l'URL pour {nom}: {e}")
        raise


#


def scraper_partenaires(url):
    """
    Scraper les données d'un partenaire à partir de l'URL donnée.

    :param url: URL de la page du partenaire
    :return: Dictionnaire contenant les données du partenaire
    """
    for i in range(3):  # Essayer jusqu'à 3 fois
        try:
            response = requests.get(url, timeout=10)  # Timeout de 10 secondes
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraction des données du partenaire
            nom = soup.find('h1', class_='font-bold text-lg xl:text-xl text-purple')
            pays = soup.find('div', class_='mt-2 text-sm xl:text-md uppercase')
            description = soup.find('div', class_='my-4 md:my-8 text-sm md:text-[16px] text-purple')

            logger.debug(f"\nresponse :\n{response} ")
            logger.debug(f"\n nom:\n{nom} ")
            logger.debug(f"\n pays :\n{pays} ")
            logger.debug(f"\n description:\n{description} ")

            return {
                'Nom': nom.get_text(strip=True) if nom else 'N/A',
                'Pays': pays.get_text(strip=True) if pays else 'N/A',
                'Lien': url,
                'Description': description.get_text(strip=True) if description else 'N/A'
            }
        except requests.RequestException as e:
            logger.error(f"Erreur lors du scraping de l'URL {url}: {e}")
            time.sleep(2)  # Attendre 2 secondes avant de réessayer
        except Exception as e:
            logger.error(f"Erreur non liée à la requête lors du scraping de l'URL {url}: {e}")
            return None
    return None


def main(fichier_csv, fichier_sortie, fichier_csv_initial):
    """
    Fonction principale pour orchestrer le scraping et l'enregistrement des données.

    :param fichier_csv: Chemin vers le fichier CSV contenant les noms des partenaires
    :param fichier_sortie: Chemin vers le fichier CSV de sortie pour enregistrer les données
    """
    try:
        # " utilisation du fichier non traité"
        # noms_partenaires = lire_noms_partenaires(fichier_csv_initial)

        # " utilisation du fichier déja traité"
        noms_partenaires, noms_partenaires_depuis_fichier_corrigé = lire_noms_partenaires(fichier_csv, fichier_csv_initial)
        donnees_partenaires = []

        # for nom in noms_partenaires:
        for nom in noms_partenaires_depuis_fichier_corrigé:

            url = construire_url_partenaire(nom)
            logger.debug(f"\n url:\n{url} ")
            logger.debug(f"\n nom:\n{nom} ")

            donnees_partenaire = scraper_partenaires(url)
            logger.debug(f"\n donnees_partenaire:\n{donnees_partenaire} ")

            if donnees_partenaire:
                donnees_partenaires.append(donnees_partenaire)

        df_resultats = pd.DataFrame(donnees_partenaires)
        df_resultats.to_csv(fichier_sortie, index=False, sep=";", encoding='utf-8')
        logger.info(f"Données des partenaires sauvegardées dans {fichier_sortie}")

    except Exception as e:
        logger.error(f"Erreur dans la fonction principale: {e}")
        raise


if __name__ == '__main__':
    fichier_csv_initial = 'vivatech_partner_name.csv'
    fichier_csv = 'fichier_partners_corrected.csv'
    fichier_sortie = 'partners.csv'
    logger.debug(f"\n fichier_csv :\n{fichier_csv} \n")

    main(fichier_csv, fichier_sortie, fichier_csv_initial)
