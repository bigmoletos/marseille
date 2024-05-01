import requests
import datetime


def scrape_event_from_json(url):
    """ Scrape les données d'un événement à partir d'une URL de l'API donnée. """
    response = requests.get(url)
    event_data = response.json()  # Hypothétique extraction JSON directement
    """ Scrape les données d'un événement à partir d'une URL de l'API donnée. """
    response = requests.get(url)
    if response.status_code == 200 and response.text:  # Vérifiez que la requête a réussi et que le contenu n'est pas vide
        try:
            event_data = response.json()  # Extraction JSON
            # Extraire et afficher les informations nécessaires ici
            print(event_data)
        except ValueError as e:  # Gérer les erreurs de décodage JSON
            print(f"Erreur de décodage JSON : {e}")
    else:
        print(f"Erreur de requête ou réponse vide, status code : {response.status_code}")

    # Extraire les informations nécessaires
    for event in event_data['data']['results']['edges']:
        node = event['node']
        dateTime = node['dateTime']
        description = node['description']
        name = node['name']
        eventUrl = node['eventUrl']

        # Afficher les détails de l'événement
        print(f"Date and Time: {dateTime}, Name: {name}, Description: {description}, URL: {eventUrl}")


def main():
    url = "https://www.meetup.com/fr-FR/find/?suggested=true&source=EVENTS&keywords=IA"  # URL fictive de l'API
    scrape_event_from_json(url)


if __name__ == "__main__":
    main()
