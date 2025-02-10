"""
Module de scraping des vols Ryanair avec interface web Streamlit.

Version améliorée du module ryanair2.py avec:
- Interface web Streamlit pour la saisie et l'affichage
- Tests de validation des URLs et des résultats
- Liens de réservation cliquables
- Visualisation interactive des données

Dépendances:
    - requests: Pour les appels API REST
    - pandas: Pour la manipulation des données
    - streamlit: Pour l'interface web
    - pytest: Pour les tests unitaires
"""

import streamlit as st
import requests
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
import pytest

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_page():
    """Configure la page Streamlit."""
    st.set_page_config(
        page_title="Recherche Vols Ryanair - Marseille",
        page_icon="✈️",
        layout="wide"
    )
    st.title("🛫 Recherche de vols Ryanair - Marseille")
    st.markdown("""
    Recherchez les vols Ryanair au départ de Marseille selon vos critères.
    Double-cliquez sur un vol pour accéder à la page de réservation.
    """)

def get_default_dates():
    """Retourne les dates par défaut pour la recherche."""
    today = datetime.now()
    default_start = today + timedelta(days=7)
    default_end = default_start + timedelta(days=2)
    return default_start.date(), default_end.date()

def validate_inputs(date_depart, date_retour, duree, prix_max):
    """
    Valide les paramètres de recherche.

    Args:
        date_depart: Date de départ
        date_retour: Date de retour
        duree: Durée du séjour
        prix_max: Prix maximum

    Returns:
        bool: True si les paramètres sont valides
    """
    try:
        if date_depart >= date_retour:
            st.error("La date de retour doit être postérieure à la date de départ")
            return False

        if prix_max <= 0:
            st.error("Le prix maximum doit être positif")
            return False

        if duree <= 0:
            st.error("La durée du séjour doit être positive")
            return False

        return True

    except Exception as e:
        st.error(f"Erreur de validation: {str(e)}")
        return False

def search_flights(start_date, end_date, days_sejour, max_price):
    """
    Recherche les vols disponibles via l'API Ryanair.

    Args:
        start_date: Date de départ (str au format YYYY-MM-DD)
        end_date: Date de retour (str au format YYYY-MM-DD)
        days_sejour: Durée du séjour en jours
        max_price: Prix maximum en EUR

    Returns:
        pandas.DataFrame: DataFrame contenant les vols trouvés
    """
    try:
        url2 = f"https://www.ryanair.com/api/farfnd/v4/roundTripFares?departureAirportIataCode=MRS&outboundDepartureDateFrom={start_date}&market=fr-fr&adultPaxCount=1&outboundDepartureDateTo={start_date}&inboundDepartureDateFrom={end_date}&inboundDepartureDateTo={end_date}&outboundDepartureTimeFrom=00:00&outboundDepartureTimeTo=23:59&priceValueTo={max_price}&currency=EUR&inboundDepartureTimeFrom=00:00&inboundDepartureTimeTo=23:59"

        with st.spinner('Recherche des vols en cours...'):
            response = requests.get(url2)
            response.raise_for_status()

            data = response.json()
            vols = []

            for fare in data['fares']:
                vol = {
                    'Départ': fare['outbound']['departureAirport']['iataCode'],
                    'Arrivée': fare['outbound']['arrivalAirport']['iataCode'],
                    'Date départ': datetime.strptime(
                        fare['outbound']['departureDate'],
                        "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%d/%m/%Y %H:%M"),
                    'Prix (EUR)': fare['outbound']['price']['value'],
                    'Lien réservation': f"https://www.ryanair.com/fr/fr/booking/home/{fare['outbound']['flightNumber']}"
                }
                vols.append(vol)

            return pd.DataFrame(vols)

    except Exception as e:
        st.error(f"Erreur lors de la recherche: {str(e)}")
        logger.error(f"Erreur lors de la recherche: {str(e)}")
        raise

def display_results(df):
    """
    Affiche les résultats dans une interface interactive.

    Args:
        df: DataFrame contenant les vols
    """
    if df.empty:
        st.warning("Aucun vol trouvé pour ces critères")
        return

    st.success(f"🎉 {len(df)} vol(s) trouvé(s)")

    # Ajout des liens cliquables
    df_display = df.copy()
    df_display['Lien réservation'] = df_display['Lien réservation'].apply(
        lambda x: f'<a href="{x}" target="_blank">Réserver</a>'
    )

    # Affichage du tableau avec liens cliquables
    st.markdown(
        df_display.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    # Statistiques
    st.subheader("📊 Statistiques")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Prix moyen", f"{df['Prix (EUR)'].mean():.2f} €")
    with col2:
        st.metric("Prix minimum", f"{df['Prix (EUR)'].min():.2f} €")

    # Graphique des prix par destination
    st.subheader("📈 Prix par destination")
    prix_dest = df.groupby('Arrivée')['Prix (EUR)'].mean()
    st.bar_chart(prix_dest)

def main():
    """Application principale Streamlit."""
    setup_page()

    # Sidebar pour les filtres
    st.sidebar.header("🔍 Critères de recherche")

    # Dates par défaut
    default_start, default_end = get_default_dates()

    # Formulaire de recherche
    with st.sidebar.form("search_form"):
        date_depart = st.date_input(
            "Date de départ",
            value=default_start,
            min_value=datetime.now().date()
        )

        date_retour = st.date_input(
            "Date de retour",
            value=default_end,
            min_value=date_depart
        )

        duree = st.number_input(
            "Durée du séjour (jours)",
            min_value=1,
            value=2
        )

        prix_max = st.number_input(
            "Prix maximum (EUR)",
            min_value=1,
            value=100
        )

        submitted = st.form_submit_button("🔎 Rechercher")

    if submitted:
        if validate_inputs(date_depart, date_retour, duree, prix_max):
            try:
                df = search_flights(
                    date_depart.strftime("%Y-%m-%d"),
                    date_retour.strftime("%Y-%m-%d"),
                    duree,
                    prix_max
                )
                display_results(df)

            except Exception as e:
                st.error("Une erreur est survenue lors de la recherche")
                logger.error(f"Erreur: {str(e)}")

# Tests
def test_url_format():
    """Vérifie que les URLs générées sont valides."""
    df = search_flights("2025-02-12", "2025-02-14", "2", "100")
    for url in df['Lien réservation']:
        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.netloc == "www.ryanair.com"
        assert parsed.path.startswith("/fr/fr/booking/home")

def test_price_coherence():
    """Vérifie que les prix respectent les critères."""
    max_price = "100"
    df = search_flights("2025-02-12", "2025-02-14", "2", max_price)
    assert all(df['Prix (EUR)'] <= float(max_price))

if __name__ == "__main__":
    main()