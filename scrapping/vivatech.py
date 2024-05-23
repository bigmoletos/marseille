import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

# Configuration du logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def nettoyer_nom_partenaire(nom):
    """
    Nettoyer le nom du partenaire en suivant les règles spécifiées :
    - Mettre tout en minuscule
    - Supprimer les caractères spéciaux sauf les points
    - Remplacer les points entre deux lettres et les espaces par un tiret
    - Supprimer les points de début et de fin de ligne

    :param nom: Nom du partenaire
    :return: Nom nettoyé
    """
    nom = nom.lower()  # Mettre tout en minuscule
    nom = re.sub(r'[^a-z0-9. ]', '', nom)  # Supprimer les caractères spéciaux sauf les points
    nom = re.sub(r'(?<=[a-z])\.(?=[a-z])', '-', nom)  # Remplacer les points entre deux lettres par un tiret
    nom = nom.replace(' ', '-')  # Remplacer les espaces par un tiret
    nom = nom.strip('.')  # Supprimer les points de début et de fin de ligne
    return nom


def lire_noms_partenaires(fichier_csv):
    """
    Lire les noms des partenaires à partir d'un fichier CSV et les nettoyer.

    :param fichier_csv: Chemin vers le fichier CSV contenant les noms des partenaires
    :return: Liste des noms des partenaires nettoyés
    """
    try:
        if not os.path.exists(fichier_csv):
            logger.error(f"Le fichier {fichier_csv} n'existe pas.")
            raise FileNotFoundError(f"Le fichier {fichier_csv} n'existe pas.")

        df = pd.read_csv(fichier_csv)
        # pour tester on ne prend que 5 noms
        df = df.iloc[:5]
        logger.debug(f"Colonnes du fichier CSV: {df.columns.tolist()}")

        noms_partenaires = df[df.columns[0]].apply(nettoyer_nom_partenaire).tolist()
        logger.debug(f"Noms des partenaires lus: {noms_partenaires}")
        return noms_partenaires
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


def scraper_partenaires(url):
    """
    Scraper les données d'un partenaire à partir de l'URL donnée.

    :param url: URL de la page du partenaire
    :return: Dictionnaire contenant les données du partenaire
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # nom = soup.find('h1', class_='partner-title')
        # pays = soup.find('div', class_='partner-country')
        # description = soup.find('div', class_='partner-description')

        nom = soup.find('h1', class_='font-bold text-lg xl:text-xl text-purple')
        pays = soup.find('div', class_='mt-2 text-sm xl:text-md uppercase')
        description = soup.find('div', class_='partner-description')

        logger.debug(f"\nresponse :\n{response} ")
        soup.to_csv("soup.csv", index=False, encoding='utf-8')
        # logger.debug(f"\nsoup:\n{soup} ")
        logger.debug(f"\n nom:\n{nom} ")
        logger.debug(f"\n pays :\n{pays} ")
        logger.debug(f"\n description:\n{description} ")

        return {
            'Nom': nom.get_text(strip=True) if nom else 'N/A',
            'Pays': pays.get_text(strip=True) if pays else 'N/A',
            'Lien': url,
            'Description': description.get_text(strip=True) if description else 'N/A'
        }
    except Exception as e:
        logger.error(f"Erreur lors du scraping de l'URL {url}: {e}")
        return None


def main(fichier_csv, fichier_sortie):
    """
    Fonction principale pour orchestrer le scraping et l'enregistrement des données.

    :param fichier_csv: Chemin vers le fichier CSV contenant les noms des partenaires
    :param fichier_sortie: Chemin vers le fichier CSV de sortie pour enregistrer les données
    """
    try:
        noms_partenaires = lire_noms_partenaires(fichier_csv)
        donnees_partenaires = []

        for nom in noms_partenaires:
            url = construire_url_partenaire(nom)
            donnees_partenaire = scraper_partenaires(url)
            if donnees_partenaire:
                donnees_partenaires.append(donnees_partenaire)

        df_resultats = pd.DataFrame(donnees_partenaires)
        df_resultats.to_csv(fichier_sortie, index=False, encoding='utf-8')
        logger.info(f"Données des partenaires sauvegardées dans {fichier_sortie}")

    except Exception as e:
        logger.error(f"Erreur dans la fonction principale: {e}")
        raise


if __name__ == '__main__':
    fichier_csv = 'vivatech_partner_name.csv'
    fichier_sortie = 'partners.csv'
    logger.debug(f"\n fichier_csv :\n{fichier_csv} \n")
    main(fichier_csv, fichier_sortie)
