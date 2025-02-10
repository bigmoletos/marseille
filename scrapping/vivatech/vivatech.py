import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import unidecode
import time

# Configuration du logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
        if df.empty:
            logger.error(f"Le fichier {fichier_csv} est vide.")
            raise ValueError(f"Le fichier {fichier_csv} est vide.")

        logger.debug(f"Colonnes du fichier CSV: {df.columns.tolist()}")

        if 'name' not in df.columns:
            logger.error(f"La colonne 'name' est manquante dans le fichier {fichier_csv}.")
            raise KeyError(f"La colonne 'name' est manquante dans le fichier {fichier_csv}.")

        noms_partenaires = df['name'].apply(nettoyer_nom_partenaire).tolist()
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
    liste_name_partner_status400 = []
    for i in range(3):  # Essayer jusqu'à 3 fois
        try:
            response = requests.get(url, timeout=15)  # Timeout de 10 secondes
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
            time.sleep(3)  # Attendre 2 secondes avant de réessayer
            liste_name_partner_status400.append(nom)
        except Exception as e:
            logger.error(f"Erreur non liée à la requête lors du scraping de l'URL {url}: {e}")
            return None
        df_liste_name_partner_status400 = pd.DataFrame(liste_name_partner_status400)
        df_liste_name_partner_status400.to_csv('liste_name_partner_status400.csv', index=False, encoding='utf-8')
    return None


def main(fichier_csv, fichier_sortie, fichier_csv_initial):
    """
    Fonction principale pour orchestrer le scraping et l'enregistrement des données.

    :param fichier_csv: Chemin vers le fichier CSV contenant les noms des partenaires nettoyés
    :param fichier_sortie: Chemin vers le fichier CSV de sortie pour enregistrer les données
    :param fichier_csv_initial: Chemin vers le fichier CSV initial contenant les noms bruts des partenaires
    """
    try:
        # Vérifier si le fichier "fichier_partners_corrected.csv" existe et comporte plus de 1000 lignes
        if os.path.exists(fichier_csv):
            df_corrected = pd.read_csv(fichier_csv)
            if df_corrected.empty:
                logger.error(f"Le fichier {fichier_csv} est vide.")
                raise ValueError(f"Le fichier {fichier_csv} est vide.")
            if len(df_corrected) > 1000:
                logger.info(f"Le fichier {fichier_csv} existe et comporte plus de 1000 lignes. Utilisation directe pour le scraping.")
                noms_partenaires = df_corrected.iloc[:, 0].tolist()
            else:
                logger.info(f"Le fichier {fichier_csv} existe mais comporte moins de 1000 lignes. Retraitement des noms des partenaires.")
                noms_partenaires = lire_noms_partenaires(fichier_csv_initial)
                df_corrected = pd.DataFrame(noms_partenaires, columns=['name'])
                df_corrected.to_csv(fichier_csv, index=False, encoding='utf-8')
                logger.info(f"Noms des partenaires nettoyés enregistrés dans {fichier_csv}")
        else:
            logger.info(f"Le fichier {fichier_csv} n'existe pas. Traitement des noms des partenaires.")
            noms_partenaires = lire_noms_partenaires(fichier_csv_initial)
            df_corrected = pd.DataFrame(noms_partenaires, columns=['name'])
            df_corrected.to_csv(fichier_csv, index=False, encoding='utf-8')
            logger.info(f"Noms des partenaires nettoyés enregistrés dans {fichier_csv}")

        donnees_partenaires = []

        for nom in noms_partenaires:
            url = construire_url_partenaire(nom)
            logger.debug(f"\n url:\n{url} ")
            logger.debug(f"\n nom:\n{nom} ")

            donnees_partenaire = scraper_partenaires(url)
            logger.debug(f"\n donnees_partenaire:\n{donnees_partenaire} ")
            df_resultats = pd.DataFrame(donnees_partenaires)

            if donnees_partenaire:
                donnees_partenaires.append(donnees_partenaire)

                df_resultats.to_csv(fichier_sortie, index=False, sep=";", encoding='utf-8')
        # df_resultats.to_csv(fichier_sortie, index=False, sep=";", encoding='utf-8')
        logger.info(f"Données des partenaires sauvegardées dans {fichier_sortie}")

    except Exception as e:
        logger.error(f"Erreur dans la fonction principale: {e}")
        raise


if __name__ == '__main__':
    liste_noms_partner_initial = 'vivatech_partner_name.csv'
    liste_noms_partner_corrected = 'fichier_partners_corrected.csv'
    # si certains noms ne passent pas on peut reiterer sur la liste des noms qui était en erreur au tour precedent.
    liste_noms_partner_corrected = 'liste_name_partner_status400.csv'
    # 43.261629, 5.333580
    fichier_sortie = 'partners.csv'
    logger.debug(f"\n liste_noms_partner_corrected :\n{liste_noms_partner_corrected} \n")

    main(liste_noms_partner_corrected, fichier_sortie, liste_noms_partner_initial)
