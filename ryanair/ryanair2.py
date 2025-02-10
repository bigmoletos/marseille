"""
Module de scraping des vols Ryanair au départ de Marseille.

Ce module permet de rechercher les vols Ryanair disponibles au départ de Marseille
selon des critères de dates et de prix. Il utilise l'API Ryanair pour récupérer
les informations des vols et les affiche dans un DataFrame pandas.

Fonctionnalités:
- Recherche de vols aller-retour au départ de Marseille
- Filtrage par dates de départ/retour
- Filtrage par prix maximum
- Affichage des résultats dans un tableau structuré

Dépendances:
    - requests: Pour les appels API REST
    - pandas: Pour la manipulation des données tabulaires
    - json: Pour le parsing des réponses API
    - logging: Pour la journalisation des événements
    - urllib: Pour l'encodage des URLs

Installation des dépendances:
    pip install requests pandas

Exemple d'utilisation:
    >>> from ryanair2 import main
    >>> main()
    # Suivez les instructions pour saisir les dates et le prix
    # Les résultats seront affichés dans la console

Notes:
    - Les dates doivent être au format YYYY-MM-DD
    - Le prix maximum est en euros
    - L'API Ryanair peut avoir des limitations de taux d'appels
"""

try:
    import requests
except ImportError:
    raise ImportError("Le module 'requests' n'est pas installé. "
                      "Veuillez l'installer avec : pip install requests")

try:
    import pandas as pd
except ImportError:
    raise ImportError("Le module 'pandas' n'est pas installé. "
                      "Veuillez l'installer avec : pip install pandas")

import json
import urllib.parse
from urllib.parse import quote, urlencode
import logging
import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_user_inputs():
    """
    Demande à l'utilisateur de saisir les paramètres de recherche de vols.

    Cette fonction gère l'interface utilisateur pour la saisie des critères
    de recherche. Elle propose des valeurs par défaut pour faciliter les tests
    et valide le format des dates saisies.

    Returns:
        tuple: Contient dans l'ordre:
            - date_depart (str): Date de départ au format YYYY-MM-DD
            - date_retour (str): Date de retour au format YYYY-MM-DD
            - duree_sejour (str): Durée du séjour en jours
            - prix_max (str): Prix maximum en EUR

    Raises:
        ValueError: Si les dates ne sont pas au format YYYY-MM-DD
        Exception: Pour toute autre erreur de saisie

    Example:
        >>> date_dep, date_ret, duree, prix = get_user_inputs()
        === Recherche de vols Ryanair au départ de Marseille ===
        Date de départ (YYYY-MM-DD) [2025-02-12]:
        # ... suivez les instructions ...
    """
    try:
        logger.info("=== Recherche de vols Ryanair au départ de Marseille ===")

        # Valeurs par défaut
        default_date_depart = "2025-02-12"
        default_date_retour = "2025-02-14"
        default_duree = "2"
        default_prix = "100"

        # Saisie avec valeurs par défaut
        date_depart = input(
            f"Date de départ (YYYY-MM-DD) [{default_date_depart}]: "
        ) or default_date_depart
        date_retour = input(
            f"Date de retour (YYYY-MM-DD) [{default_date_retour}]: "
        ) or default_date_retour
        duree_sejour = input(
            f"Durée du séjour (en jours) [{default_duree}]: ") or default_duree
        prix_max = input(
            f"Prix maximum (en EUR) [{default_prix}]: ") or default_prix

        logger.info(f"Paramètres de recherche:")
        logger.info(f"- Date de départ: {date_depart}")
        logger.info(f"- Date de retour: {date_retour}")
        logger.info(f"- Durée du séjour: {duree_sejour} jours")
        logger.info(f"- Prix maximum: {prix_max} EUR")

        # Validation basique des dates
        if not all(len(date) == 10 for date in [date_depart, date_retour]):
            raise ValueError("Les dates doivent être au format YYYY-MM-DD")

        return date_depart, date_retour, duree_sejour, prix_max
    except ValueError as ve:
        logger.error(f"Erreur de format de date: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la saisie: {str(e)}")
        raise


def search_flights(start_date, end_date, days_sejour, max_price):
    """
    Recherche les vols disponibles selon les critères spécifiés via l'API Ryanair.

    Cette fonction interroge l'API Ryanair pour trouver les vols aller-retour
    disponibles depuis Marseille selon les critères fournis. Elle construit l'URL
    de requête avec les paramètres et traite la réponse JSON pour extraire les
    informations pertinentes des vols.

    Args:
        start_date (str): Date de départ au format YYYY-MM-DD
        end_date (str): Date de retour au format YYYY-MM-DD
        days_sejour (str): Durée du séjour en jours (non utilisé actuellement)
        max_price (str): Prix maximum en EUR

    Returns:
        pandas.DataFrame: DataFrame contenant les colonnes:
            - departure_iata: Code IATA aéroport de départ (ex: 'MRS')
            - arrival_iata: Code IATA aéroport d'arrivée
            - departure_date: Date et heure de départ (format ISO)
            - arrival_date: Date et heure d'arrivée (format ISO)
            - price: Prix du vol en EUR
            - booking_url: URL pour réserver le vol

    Raises:
        requests.RequestException: En cas d'erreur de communication avec l'API
        json.JSONDecodeError: En cas d'erreur de décodage de la réponse
        Exception: Pour toute autre erreur inattendue

    Notes:
        - L'API Ryanair peut avoir des limitations de taux d'appels
        - Les prix sont en EUR et incluent uniquement le vol
        - L'URL de réservation est construite pour le site français de Ryanair
    """
    try:
        url2 = f"https://www.ryanair.com/api/farfnd/v4/roundTripFares?departureAirportIataCode=MRS&outboundDepartureDateFrom={start_date}&market=fr-fr&adultPaxCount=1&outboundDepartureDateTo={start_date}&inboundDepartureDateFrom={end_date}&inboundDepartureDateTo={end_date}&outboundDepartureTimeFrom=00:00&outboundDepartureTimeTo=23:59&priceValueTo={max_price}&currency=EUR&inboundDepartureTimeFrom=00:00&inboundDepartureTimeTo=23:59"

        base_booking_url = "https://www.ryanair.com/fr/fr/booking/home"

        response = requests.get(url2)
        response.raise_for_status()

        data = response.json()
        vols = []

        for fare in data['fares']:
            vol = {
                'departure_iata':
                fare['outbound']['departureAirport']['iataCode'],
                'arrival_iata':
                fare['outbound']['arrivalAirport']['iataCode'],
                'departure_date':
                fare['outbound']['departureDate'],
                'arrival_date':
                fare['outbound']['arrivalDate'],
                'price':
                fare['outbound']['price']['value'],
                'booking_url':
                f"{base_booking_url}/{fare['outbound']['flightNumber']}"
            }
            vols.append(vol)

        return pd.DataFrame(vols)

    except requests.RequestException as re:
        logger.error(f"Erreur de requête API: {str(re)}")
        raise
    except json.JSONDecodeError as je:
        logger.error(f"Erreur de décodage JSON: {str(je)}")
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        raise


def main():
    """
    Fonction principale qui orchestre la recherche de vols.

    Cette fonction coordonne le processus complet de recherche de vols:
    1. Récupération des critères de recherche auprès de l'utilisateur
    2. Recherche des vols via l'API Ryanair
    3. Affichage des résultats ou des messages d'erreur appropriés

    La fonction gère les exceptions à haut niveau et assure une sortie
    propre en cas d'erreur.

    Returns:
        None

    Raises:
        Exception: Toute erreur non gérée est remontée après journalisation

    Example:
        >>> main()
        # Suit le processus de recherche et affiche les résultats
    """
    try:
        # Récupération des paramètres
        date_depart, date_retour, duree_sejour, prix_max = get_user_inputs()

        # Recherche des vols
        logger.info("Recherche des vols en cours...")
        df_vols = search_flights(date_depart, date_retour, duree_sejour, prix_max)

        if df_vols.empty:
            logger.warning("Aucun vol trouvé pour ces critères.")
            return

        # Affichage des résultats
        logger.info("\nVols trouvés :")
        logger.info("\n" + df_vols.to_string())
        logger.info(f"\nNombre total de vols trouvés : {len(df_vols)}")

    except Exception as e:
        logger.error(f"Erreur lors de l'exécution : {str(e)}")
        raise

if __name__ == "__main__":
    main()
