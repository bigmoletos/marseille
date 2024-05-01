import requests
from bs4 import BeautifulSoup
import datetime


def scrap_event(url: str) -> str:
    """Scrape les données d'un événement à partir d'une URL donnée."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extrayez le titre de l'événement
    title = soup.find('h1', class_='event-title').text.strip()

    # Extrayez la description de l'événement
    description = soup.find('div', class_='event-description').text.strip()

    # Extrayez la date et l'heure de l'événement
    date_time_str = soup.find('time', class_='event-date').text.strip()
    # Convertir la chaîne de date/heure en format structuré (ajustez selon le format)
    date_time = datetime.strptime(date_time_str, '%d %B %Y à %H:%M')

    # Extrayez le thème de l'événement (ajoutez des sélecteurs CSS spécifiques à chaque site)
    theme = soup.find('div', class_='event-category').text.strip()

    # Extrayez le lieu de l'événement (ajoutez des sélecteurs CSS spécifiques à chaque site)
    location = soup.find('div', class_='event-location').text.strip()

    # Extrayez le lien vers l'événement (ajoutez des sélecteurs CSS spécifiques à chaque site)
    event_link = soup.find('a', class_='event-link')['href']

    return {'title': title, 'description': description, 'date_time': date_time, 'theme': theme, 'location': location, 'event_link': event_link}


def main():
    # Définissez les thèmes recherchés
    themes = ['Musique', 'Théâtre', 'Conférence']

    # Définissez la plage de dates
    start_date = datetime.date(2024, 5, 1)  # Changez la date de début selon vos besoins
    end_date = datetime.date(2024, 5, 31)  # Changez la date de fin selon vos besoins

    # Liste des sites web à scrapper
    websites = [
        'https://www.meetup.com/fr-FR/find/?suggested=true&source=EVENTS&keywords=IA', 'https://www.marseille-tourisme.com/', 'https://www.myprovence.fr/',
        'https://www.sortiramarseille.fr/', 'https://madeinmarseille.net/agenda/', 'https://lafrenchtech-aixmarseille.fr/agendas/','https://lafrenchtech-grandeprovence.fr/lagenda/',
        'https://www.frenchtechcotedazur.fr/events/', 'https://medinsoft.com/actu/', 'https://medinsoft.com/event-directory/',
        'https://medinsoft.com/evenements/les-events-medinsoft/','https://lacoque-numerique.fr/'
    ]'
    # Scrapez les événements de chaque site web
    for website in websites:
        response = requests.get(website)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrayez les liens des événements (ajoutez des sélecteurs CSS spécifiques à chaque site)
        event_links = soup.find_all('a', class_='event-link')

        for event_link in event_links:
            event_url = event_link['href']

            # Scrapez les données de l'événement
            event_data = scrap_event(event_url)

            # Filtrez par thème et date
            if event_data['theme'] in themes and event_data['date_time'].date() >= start_date and event_data['date_time'].date() <= end_date:
                print(event_data)  # Affichez les données de l'événement


if __name__ == '__main__':
    main()
