import requests
import json
import urllib.parse
from urllib.parse import quote, urlencode
import logging
import requests
import urllib.parse
import pandas as pd
import numpy as np
import json
import logging
import urllib3


start_date="2024-06-12"
end_date="2024-06-14"
days_sejour="2"
max_price="100"

url=f"https://www.ryanair.com/fr/fr/cheap-flights-beta?originIata=MRS&destinationIata=ANY&isReturn=true&isMacDestination=false&promoCode=&adults=1&teens=0&children=0&infants=0&dateOut={start_date}&dateIn={end_date}&daysTrip={days_sejour}&dayOfWeek=TUESDAY&isExactDate=true&outboundFromHour=00:00&outboundToHour=23:59&inboundFromHour=00:00&inboundToHour=23:59&priceValueTo={max_price}&currency=EUR&isFlexibleDay=false"


url2=f"https://www.ryanair.com/api/farfnd/v4/roundTripFares?departureAirportIataCode=MRS&outboundDepartureDateFrom={start_date}&market=fr-fr&adultPaxCount=1&outboundDepartureDateTo={start_date}&inboundDepartureDateFrom={end_date}&inboundDepartureDateTo={end_date}&outboundDepartureTimeFrom=00:00&outboundDepartureTimeTo=23:59&priceValueTo={max_price}&currency=EUR&inboundDepartureTimeFrom=00:00&inboundDepartureTimeTo=23:59"
# print(url)

base_booking_url = "https://www.ryanair.com/fr/fr/booking/home"

# response = requests.get(
#                 url,
#                 headers={'Content-Type': 'application/json'},
#                 verify=False)


# if response.status_code == 200:
#     print(url)


# Envoyer la requête GET à l'API
response = requests.get(url2)
# print(response.status_code)
# print(response.text)

# Vérifier que la requête a réussi
if response.status_code == 200:
    try:
     data = response.json()
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        print("Réponse obtenue :")
        # print(response.text)

    # Extraire les informations de vol
    vols = []
for fare in data['fares']:
    # Extrait les codes IATA
    departure_iata = fare['outbound']['departureAirport']['iataCode']
    arrival_iata = fare['outbound']['arrivalAirport']['iataCode']
    # Extrait les dates
    departure_date = fare['outbound']['departureDate'].split('T')[0]  # Garde uniquement la date sans l'heure
    return_date = fare['inbound']['departureDate'].split('T')[0]  # Garde uniquement la date sans l'heure

    # Construire l'URL de réservation
    booking_url = f"{base_booking_url}/{departure_iata}/{arrival_iata}/{departure_date}/{return_date}/1/0/0/0"

    vol_info = {
        'Destination': fare['outbound']['arrivalAirport']['name'],
        'Prix': fare['summary']['price']['value'],
        'Devise': fare['summary']['price']['currencyCode'],
        'Date de départ': fare['outbound']['departureDate'],
        'Date de retour': fare['inbound']['departureDate'],
        'URL de réservation': booking_url  # Ajoute l'URL de réservation au dictionnaire
    }
    vols.append(vol_info)

    # Créer un DataFrame pandas à partir de la liste des vols
    df_vols = pd.DataFrame(vols)

    # Afficher le DataFrame
    print(df_vols)
else:
    print("Erreur lors de la requête à l'API")


# #             Destination   Prix  ...       Date de départ       Date de retour
# 0              Bordeaux  40.94  ...  2024-06-12T07:25:00  2024-06-14T22:30:00
# 1                 Palma  50.74  ...  2024-06-12T23:40:00  2024-06-14T21:50:00
# 2                 Zadar  51.55  ...  2024-06-12T19:55:00  2024-06-14T16:30:00
# 3        Rome-Fiumicino  55.50  ...  2024-06-12T18:05:00  2024-06-14T20:40:00
# 4              Alicante  59.94  ...  2024-06-12T22:35:00  2024-06-14T19:30:00
# 5                Madrid  64.43  ...  2024-06-12T16:00:00  2024-06-14T18:35:00
# 6               Catania  65.04  ...  2024-06-12T05:50:00  2024-06-14T15:30:00
# 7               Palerme  66.30  ...  2024-06-12T14:55:00  2024-06-14T22:10:00
# 8               Séville  66.52  ...  2024-06-12T19:20:00  2024-06-14T21:50:00
# 9                   Fes  70.77  ...  2024-06-12T22:00:00  2024-06-14T18:30:00
# 10               Tanger  71.70  ...  2024-06-12T21:30:00  2024-06-14T13:35:00
# 11  Bruxelles-Charleroi  75.24  ...  2024-06-12T09:20:00  2024-06-14T17:15:00
# 12                 Faro  77.06  ...  2024-06-12T22:05:00  2024-06-14T07:25:00
# 13               Malaga  77.98  ...  2024-06-12T05:50:00  2024-06-14T08:20:00
# 14                Malte  86.88  ...  2024-06-12T15:40:00  2024-06-14T15:30:00
# 15             Lisbonne  92.11  ...  2024-06-12T16:00:00  2024-06-14T18:00:00
# 16                Lille  93.11  ...  2024-06-12T10:55:00  2024-06-14T17:45:00
# 17       Venise-Trévise  94.38  ...  2024-06-12T05:50:00  2024-06-14T15:30:00
# 18               Nantes  99.87  ...  2024-06-12T20:30:00  2024-06-14T09:00:00

"""{
    "arrivalAirportCategories": null,
    "fares": [
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "BOD",
                    "name": "Bordeaux",
                    "seoName": "bordeaux",
                    "city": {
                        "name": "Bordeaux",
                        "code": "BORDEAUX",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-12T07:25:00",
                "arrivalDate": "2024-06-12T08:35:00",
                "price": {
                    "value": 20.16,
                    "valueMainUnit": "20",
                    "valueFractionalUnit": "16",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~3820~ ~~MRS~06/12/2024 07:25~BOD~06/12/2024 08:35~~",
                "flightNumber": "FR3820",
                "previousPrice": null,
                "priceUpdated": 1710484779000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "BOD",
                    "name": "Bordeaux",
                    "seoName": "bordeaux",
                    "city": {
                        "name": "Bordeaux",
                        "code": "BORDEAUX",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T22:30:00",
                "arrivalDate": "2024-06-14T23:45:00",
                "price": {
                    "value": 20.78,
                    "valueMainUnit": "20",
                    "valueFractionalUnit": "78",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6467~ ~~BOD~06/14/2024 22:30~MRS~06/14/2024 23:45~~",
                "flightNumber": "FR6467",
                "previousPrice": null,
                "priceUpdated": 1710484093000
            },
            "summary": {
                "price": {
                    "value": 40.94,
                    "valueMainUnit": "40",
                    "valueFractionalUnit": "94",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Espagne",
                    "iataCode": "PMI",
                    "name": "Palma",
                    "seoName": "palma-mallorca",
                    "city": {
                        "name": "Palma",
                        "code": "PALMA",
                        "countryCode": "es"
                    }
                },
                "departureDate": "2024-06-12T23:40:00",
                "arrivalDate": "2024-06-13T00:50:00",
                "price": {
                    "value": 25.37,
                    "valueMainUnit": "25",
                    "valueFractionalUnit": "37",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5201~ ~~MRS~06/12/2024 23:40~PMI~06/13/2024 00:50~~",
                "flightNumber": "FR5201",
                "previousPrice": null,
                "priceUpdated": 1710487508000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Espagne",
                    "iataCode": "PMI",
                    "name": "Palma",
                    "seoName": "palma-mallorca",
                    "city": {
                        "name": "Palma",
                        "code": "PALMA",
                        "countryCode": "es"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T21:50:00",
                "arrivalDate": "2024-06-14T23:05:00",
                "price": {
                    "value": 25.37,
                    "valueMainUnit": "25",
                    "valueFractionalUnit": "37",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5200~ ~~PMI~06/14/2024 21:50~MRS~06/14/2024 23:05~~",
                "flightNumber": "FR5200",
                "previousPrice": null,
                "priceUpdated": 1710484708000
            },
            "summary": {
                "price": {
                    "value": 50.74,
                    "valueMainUnit": "50",
                    "valueFractionalUnit": "74",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Croatie",
                    "iataCode": "ZAD",
                    "name": "Zadar",
                    "seoName": "zadar",
                    "city": {
                        "name": "Zadar",
                        "code": "ZADAR",
                        "countryCode": "hr"
                    }
                },
                "departureDate": "2024-06-12T19:55:00",
                "arrivalDate": "2024-06-12T21:25:00",
                "price": {
                    "value": 26.18,
                    "valueMainUnit": "26",
                    "valueFractionalUnit": "18",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5177~ ~~MRS~06/12/2024 19:55~ZAD~06/12/2024 21:25~~",
                "flightNumber": "FR5177",
                "previousPrice": null,
                "priceUpdated": 1710489346000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Croatie",
                    "iataCode": "ZAD",
                    "name": "Zadar",
                    "seoName": "zadar",
                    "city": {
                        "name": "Zadar",
                        "code": "ZADAR",
                        "countryCode": "hr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T16:30:00",
                "arrivalDate": "2024-06-14T18:15:00",
                "price": {
                    "value": 25.37,
                    "valueMainUnit": "25",
                    "valueFractionalUnit": "37",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5176~ ~~ZAD~06/14/2024 16:30~MRS~06/14/2024 18:15~~",
                "flightNumber": "FR5176",
                "previousPrice": null,
                "priceUpdated": 1710485867000
            },
            "summary": {
                "price": {
                    "value": 51.55,
                    "valueMainUnit": "51",
                    "valueFractionalUnit": "55",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Italie",
                    "iataCode": "FCO",
                    "name": "Rome-Fiumicino",
                    "seoName": "rome-fiumicino",
                    "city": {
                        "name": "Rome",
                        "code": "ROME",
                        "macCode": "ROM",
                        "countryCode": "it"
                    }
                },
                "departureDate": "2024-06-12T18:05:00",
                "arrivalDate": "2024-06-12T19:30:00",
                "price": {
                    "value": 28.51,
                    "valueMainUnit": "28",
                    "valueFractionalUnit": "51",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~9760~ ~~MRS~06/12/2024 18:05~FCO~06/12/2024 19:30~~",
                "flightNumber": "FR9760",
                "previousPrice": null,
                "priceUpdated": 1710485681000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Italie",
                    "iataCode": "FCO",
                    "name": "Rome-Fiumicino",
                    "seoName": "rome-fiumicino",
                    "city": {
                        "name": "Rome",
                        "code": "ROME",
                        "macCode": "ROM",
                        "countryCode": "it"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T20:40:00",
                "arrivalDate": "2024-06-14T22:10:00",
                "price": {
                    "value": 26.99,
                    "valueMainUnit": "26",
                    "valueFractionalUnit": "99",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~9725~ ~~FCO~06/14/2024 20:40~MRS~06/14/2024 22:10~~",
                "flightNumber": "FR9725",
                "previousPrice": null,
                "priceUpdated": 1710484920000
            },
            "summary": {
                "price": {
                    "value": 55.50,
                    "valueMainUnit": "55",
                    "valueFractionalUnit": "50",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Espagne",
                    "iataCode": "ALC",
                    "name": "Alicante",
                    "seoName": "alicante",
                    "city": {
                        "name": "Alicante",
                        "code": "ALICANTE",
                        "countryCode": "es"
                    }
                },
                "departureDate": "2024-06-12T22:35:00",
                "arrivalDate": "2024-06-13T00:10:00",
                "price": {
                    "value": 27.31,
                    "valueMainUnit": "27",
                    "valueFractionalUnit": "31",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6495~ ~~MRS~06/12/2024 22:35~ALC~06/13/2024 00:10~~",
                "flightNumber": "FR6495",
                "previousPrice": null,
                "priceUpdated": 1710484685000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Espagne",
                    "iataCode": "ALC",
                    "name": "Alicante",
                    "seoName": "alicante",
                    "city": {
                        "name": "Alicante",
                        "code": "ALICANTE",
                        "countryCode": "es"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T19:30:00",
                "arrivalDate": "2024-06-14T21:05:00",
                "price": {
                    "value": 32.63,
                    "valueMainUnit": "32",
                    "valueFractionalUnit": "63",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6496~ ~~ALC~06/14/2024 19:30~MRS~06/14/2024 21:05~~",
                "flightNumber": "FR6496",
                "previousPrice": null,
                "priceUpdated": 1710496561000
            },
            "summary": {
                "price": {
                    "value": 59.94,
                    "valueMainUnit": "59",
                    "valueFractionalUnit": "94",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Espagne",
                    "iataCode": "MAD",
                    "name": "Madrid",
                    "seoName": "madrid",
                    "city": {
                        "name": "Madrid",
                        "code": "MADRID",
                        "countryCode": "es"
                    }
                },
                "departureDate": "2024-06-12T16:00:00",
                "arrivalDate": "2024-06-12T17:45:00",
                "price": {
                    "value": 29.99,
                    "valueMainUnit": "29",
                    "valueFractionalUnit": "99",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5447~ ~~MRS~06/12/2024 16:00~MAD~06/12/2024 17:45~~",
                "flightNumber": "FR5447",
                "previousPrice": null,
                "priceUpdated": 1710485682000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Espagne",
                    "iataCode": "MAD",
                    "name": "Madrid",
                    "seoName": "madrid",
                    "city": {
                        "name": "Madrid",
                        "code": "MADRID",
                        "countryCode": "es"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T18:35:00",
                "arrivalDate": "2024-06-14T20:20:00",
                "price": {
                    "value": 34.44,
                    "valueMainUnit": "34",
                    "valueFractionalUnit": "44",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5446~ ~~MAD~06/14/2024 18:35~MRS~06/14/2024 20:20~~",
                "flightNumber": "FR5446",
                "previousPrice": null,
                "priceUpdated": 1710485051000
            },
            "summary": {
                "price": {
                    "value": 64.43,
                    "valueMainUnit": "64",
                    "valueFractionalUnit": "43",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Italie",
                    "iataCode": "CTA",
                    "name": "Catania",
                    "seoName": "catania",
                    "city": {
                        "name": "Catane",
                        "code": "CATANIA",
                        "countryCode": "it"
                    }
                },
                "departureDate": "2024-06-12T05:50:00",
                "arrivalDate": "2024-06-12T07:45:00",
                "price": {
                    "value": 28.99,
                    "valueMainUnit": "28",
                    "valueFractionalUnit": "99",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~4063~ ~~MRS~06/12/2024 05:50~CTA~06/12/2024 07:45~~",
                "flightNumber": "FR4063",
                "previousPrice": null,
                "priceUpdated": 1710489322000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Italie",
                    "iataCode": "CTA",
                    "name": "Catania",
                    "seoName": "catania",
                    "city": {
                        "name": "Catane",
                        "code": "CATANIA",
                        "countryCode": "it"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T15:30:00",
                "arrivalDate": "2024-06-14T17:35:00",
                "price": {
                    "value": 36.05,
                    "valueMainUnit": "36",
                    "valueFractionalUnit": "05",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~4064~ ~~CTA~06/14/2024 15:30~MRS~06/14/2024 17:35~~",
                "flightNumber": "FR4064",
                "previousPrice": null,
                "priceUpdated": 1710485243000
            },
            "summary": {
                "price": {
                    "value": 65.04,
                    "valueMainUnit": "65",
                    "valueFractionalUnit": "04",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Italie",
                    "iataCode": "PMO",
                    "name": "Palerme",
                    "seoName": "palermo",
                    "city": {
                        "name": "Palerme",
                        "code": "PALERMO",
                        "countryCode": "it"
                    }
                },
                "departureDate": "2024-06-12T14:55:00",
                "arrivalDate": "2024-06-12T16:35:00",
                "price": {
                    "value": 30.25,
                    "valueMainUnit": "30",
                    "valueFractionalUnit": "25",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6785~ ~~MRS~06/12/2024 14:55~PMO~06/12/2024 16:35~~",
                "flightNumber": "FR6785",
                "previousPrice": null,
                "priceUpdated": 1710484717000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Italie",
                    "iataCode": "PMO",
                    "name": "Palerme",
                    "seoName": "palermo",
                    "city": {
                        "name": "Palerme",
                        "code": "PALERMO",
                        "countryCode": "it"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T22:10:00",
                "arrivalDate": "2024-06-14T23:55:00",
                "price": {
                    "value": 36.05,
                    "valueMainUnit": "36",
                    "valueFractionalUnit": "05",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6786~ ~~PMO~06/14/2024 22:10~MRS~06/14/2024 23:55~~",
                "flightNumber": "FR6786",
                "previousPrice": null,
                "priceUpdated": 1710483969000
            },
            "summary": {
                "price": {
                    "value": 66.30,
                    "valueMainUnit": "66",
                    "valueFractionalUnit": "30",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Espagne",
                    "iataCode": "SVQ",
                    "name": "Séville",
                    "seoName": "seville",
                    "city": {
                        "name": "Séville",
                        "code": "SEVILLE",
                        "countryCode": "es"
                    }
                },
                "departureDate": "2024-06-12T19:20:00",
                "arrivalDate": "2024-06-12T21:20:00",
                "price": {
                    "value": 34.43,
                    "valueMainUnit": "34",
                    "valueFractionalUnit": "43",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~3106~ ~~MRS~06/12/2024 19:20~SVQ~06/12/2024 21:20~~",
                "flightNumber": "FR3106",
                "previousPrice": null,
                "priceUpdated": 1710485688000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Espagne",
                    "iataCode": "SVQ",
                    "name": "Séville",
                    "seoName": "seville",
                    "city": {
                        "name": "Séville",
                        "code": "SEVILLE",
                        "countryCode": "es"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T21:50:00",
                "arrivalDate": "2024-06-14T23:55:00",
                "price": {
                    "value": 32.09,
                    "valueMainUnit": "32",
                    "valueFractionalUnit": "09",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~3107~ ~~SVQ~06/14/2024 21:50~MRS~06/14/2024 23:55~~",
                "flightNumber": "FR3107",
                "previousPrice": null,
                "priceUpdated": 1710486786000
            },
            "summary": {
                "price": {
                    "value": 66.52,
                    "valueMainUnit": "66",
                    "valueFractionalUnit": "52",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Maroc",
                    "iataCode": "FEZ",
                    "name": "Fes",
                    "seoName": "fez",
                    "city": {
                        "name": "Fes",
                        "code": "FEZ",
                        "countryCode": "ma"
                    }
                },
                "departureDate": "2024-06-12T22:00:00",
                "arrivalDate": "2024-06-12T23:15:00",
                "price": {
                    "value": 38.02,
                    "valueMainUnit": "38",
                    "valueFractionalUnit": "02",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5162~ ~~MRS~06/12/2024 22:00~FEZ~06/12/2024 23:15~~",
                "flightNumber": "FR5162",
                "previousPrice": null,
                "priceUpdated": 1710485702000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Maroc",
                    "iataCode": "FEZ",
                    "name": "Fes",
                    "seoName": "fez",
                    "city": {
                        "name": "Fes",
                        "code": "FEZ",
                        "countryCode": "ma"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T18:30:00",
                "arrivalDate": "2024-06-14T21:45:00",
                "price": {
                    "value": 32.75,
                    "valueMainUnit": "32",
                    "valueFractionalUnit": "75",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5163~ ~~FEZ~06/14/2024 18:30~MRS~06/14/2024 21:45~~",
                "flightNumber": "FR5163",
                "previousPrice": null,
                "priceUpdated": 1710484650000
            },
            "summary": {
                "price": {
                    "value": 70.77,
                    "valueMainUnit": "70",
                    "valueFractionalUnit": "77",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Maroc",
                    "iataCode": "TNG",
                    "name": "Tanger",
                    "seoName": "tangier",
                    "city": {
                        "name": "Tanger",
                        "code": "TANGIER",
                        "countryCode": "ma"
                    }
                },
                "departureDate": "2024-06-12T21:30:00",
                "arrivalDate": "2024-06-12T22:45:00",
                "price": {
                    "value": 37.71,
                    "valueMainUnit": "37",
                    "valueFractionalUnit": "71",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6007~ ~~MRS~06/12/2024 21:30~TNG~06/12/2024 22:45~~",
                "flightNumber": "FR6007",
                "previousPrice": null,
                "priceUpdated": 1710485710000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Maroc",
                    "iataCode": "TNG",
                    "name": "Tanger",
                    "seoName": "tangier",
                    "city": {
                        "name": "Tanger",
                        "code": "TANGIER",
                        "countryCode": "ma"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T13:35:00",
                "arrivalDate": "2024-06-14T16:45:00",
                "price": {
                    "value": 33.99,
                    "valueMainUnit": "33",
                    "valueFractionalUnit": "99",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6008~ ~~TNG~06/14/2024 13:35~MRS~06/14/2024 16:45~~",
                "flightNumber": "FR6008",
                "previousPrice": null,
                "priceUpdated": 1710494824000
            },
            "summary": {
                "price": {
                    "value": 71.70,
                    "valueMainUnit": "71",
                    "valueFractionalUnit": "70",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Belgique",
                    "iataCode": "CRL",
                    "name": "Bruxelles-Charleroi",
                    "seoName": "bruxelles-charleroi",
                    "city": {
                        "name": "Charleroi",
                        "code": "CHARLEROI",
                        "countryCode": "be"
                    }
                },
                "departureDate": "2024-06-12T09:20:00",
                "arrivalDate": "2024-06-12T11:00:00",
                "price": {
                    "value": 30.25,
                    "valueMainUnit": "30",
                    "valueFractionalUnit": "25",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~4839~ ~~MRS~06/12/2024 09:20~CRL~06/12/2024 11:00~~",
                "flightNumber": "FR4839",
                "previousPrice": null,
                "priceUpdated": 1710484394000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Belgique",
                    "iataCode": "CRL",
                    "name": "Bruxelles-Charleroi",
                    "seoName": "bruxelles-charleroi",
                    "city": {
                        "name": "Charleroi",
                        "code": "CHARLEROI",
                        "countryCode": "be"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T17:15:00",
                "arrivalDate": "2024-06-14T19:00:00",
                "price": {
                    "value": 44.99,
                    "valueMainUnit": "44",
                    "valueFractionalUnit": "99",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6316~ ~~CRL~06/14/2024 17:15~MRS~06/14/2024 19:00~~",
                "flightNumber": "FR6316",
                "previousPrice": null,
                "priceUpdated": 1710494792000
            },
            "summary": {
                "price": {
                    "value": 75.24,
                    "valueMainUnit": "75",
                    "valueFractionalUnit": "24",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Portugal",
                    "iataCode": "FAO",
                    "name": "Faro",
                    "seoName": "faro",
                    "city": {
                        "name": "Faro",
                        "code": "FARO",
                        "countryCode": "pt"
                    }
                },
                "departureDate": "2024-06-12T22:05:00",
                "arrivalDate": "2024-06-12T23:20:00",
                "price": {
                    "value": 34.07,
                    "valueMainUnit": "34",
                    "valueFractionalUnit": "07",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5795~ ~~MRS~06/12/2024 22:05~FAO~06/12/2024 23:20~~",
                "flightNumber": "FR5795",
                "previousPrice": null,
                "priceUpdated": 1710484704000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Portugal",
                    "iataCode": "FAO",
                    "name": "Faro",
                    "seoName": "faro",
                    "city": {
                        "name": "Faro",
                        "code": "FARO",
                        "countryCode": "pt"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T07:25:00",
                "arrivalDate": "2024-06-14T10:40:00",
                "price": {
                    "value": 42.99,
                    "valueMainUnit": "42",
                    "valueFractionalUnit": "99",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~5794~ ~~FAO~06/14/2024 07:25~MRS~06/14/2024 10:40~~",
                "flightNumber": "FR5794",
                "previousPrice": null,
                "priceUpdated": 1710488156000
            },
            "summary": {
                "price": {
                    "value": 77.06,
                    "valueMainUnit": "77",
                    "valueFractionalUnit": "06",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Espagne",
                    "iataCode": "AGP",
                    "name": "Malaga",
                    "seoName": "malaga",
                    "city": {
                        "name": "Malaga",
                        "code": "MALAGA",
                        "countryCode": "es"
                    }
                },
                "departureDate": "2024-06-12T05:50:00",
                "arrivalDate": "2024-06-12T07:50:00",
                "price": {
                    "value": 32.13,
                    "valueMainUnit": "32",
                    "valueFractionalUnit": "13",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~7776~ ~~MRS~06/12/2024 05:50~AGP~06/12/2024 07:50~~",
                "flightNumber": "FR7776",
                "previousPrice": null,
                "priceUpdated": 1710487512000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Espagne",
                    "iataCode": "AGP",
                    "name": "Malaga",
                    "seoName": "malaga",
                    "city": {
                        "name": "Malaga",
                        "code": "MALAGA",
                        "countryCode": "es"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T08:20:00",
                "arrivalDate": "2024-06-14T10:20:00",
                "price": {
                    "value": 45.85,
                    "valueMainUnit": "45",
                    "valueFractionalUnit": "85",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~7775~ ~~AGP~06/14/2024 08:20~MRS~06/14/2024 10:20~~",
                "flightNumber": "FR7775",
                "previousPrice": null,
                "priceUpdated": 1710491143000
            },
            "summary": {
                "price": {
                    "value": 77.98,
                    "valueMainUnit": "77",
                    "valueFractionalUnit": "98",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Malte",
                    "iataCode": "MLA",
                    "name": "Malte",
                    "seoName": "malte",
                    "city": {
                        "name": "Malte",
                        "code": "MALTA",
                        "countryCode": "mt"
                    }
                },
                "departureDate": "2024-06-12T15:40:00",
                "arrivalDate": "2024-06-12T17:35:00",
                "price": {
                    "value": 39.21,
                    "valueMainUnit": "39",
                    "valueFractionalUnit": "21",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~7796~ ~~MRS~06/12/2024 15:40~MLA~06/12/2024 17:35~~",
                "flightNumber": "FR7796",
                "previousPrice": null,
                "priceUpdated": 1710485700000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Malte",
                    "iataCode": "MLA",
                    "name": "Malte",
                    "seoName": "malte",
                    "city": {
                        "name": "Malte",
                        "code": "MALTA",
                        "countryCode": "mt"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T15:30:00",
                "arrivalDate": "2024-06-14T17:35:00",
                "price": {
                    "value": 47.67,
                    "valueMainUnit": "47",
                    "valueFractionalUnit": "67",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~7795~ ~~MLA~06/14/2024 15:30~MRS~06/14/2024 17:35~~",
                "flightNumber": "FR7795",
                "previousPrice": null,
                "priceUpdated": 1710484734000
            },
            "summary": {
                "price": {
                    "value": 86.88,
                    "valueMainUnit": "86",
                    "valueFractionalUnit": "88",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Portugal",
                    "iataCode": "LIS",
                    "name": "Lisbonne",
                    "seoName": "lisbon",
                    "city": {
                        "name": "Lisbonne",
                        "code": "LISBON",
                        "countryCode": "pt"
                    }
                },
                "departureDate": "2024-06-12T16:00:00",
                "arrivalDate": "2024-06-12T17:20:00",
                "price": {
                    "value": 40.47,
                    "valueMainUnit": "40",
                    "valueFractionalUnit": "47",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~2078~ ~~MRS~06/12/2024 16:00~LIS~06/12/2024 17:20~~",
                "flightNumber": "FR2078",
                "previousPrice": null,
                "priceUpdated": 1710485683000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Portugal",
                    "iataCode": "LIS",
                    "name": "Lisbonne",
                    "seoName": "lisbon",
                    "city": {
                        "name": "Lisbonne",
                        "code": "LISBON",
                        "countryCode": "pt"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T18:00:00",
                "arrivalDate": "2024-06-14T21:15:00",
                "price": {
                    "value": 51.64,
                    "valueMainUnit": "51",
                    "valueFractionalUnit": "64",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~2077~ ~~LIS~06/14/2024 18:00~MRS~06/14/2024 21:15~~",
                "flightNumber": "FR2077",
                "previousPrice": null,
                "priceUpdated": 1710484514000
            },
            "summary": {
                "price": {
                    "value": 92.11,
                    "valueMainUnit": "92",
                    "valueFractionalUnit": "11",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "LIL",
                    "name": "Lille",
                    "seoName": "lille",
                    "city": {
                        "name": "Lille",
                        "code": "LILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-12T10:55:00",
                "arrivalDate": "2024-06-12T12:30:00",
                "price": {
                    "value": 30.04,
                    "valueMainUnit": "30",
                    "valueFractionalUnit": "04",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6005~ ~~MRS~06/12/2024 10:55~LIL~06/12/2024 12:30~~",
                "flightNumber": "FR6005",
                "previousPrice": null,
                "priceUpdated": 1710486581000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "LIL",
                    "name": "Lille",
                    "seoName": "lille",
                    "city": {
                        "name": "Lille",
                        "code": "LILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T17:45:00",
                "arrivalDate": "2024-06-14T19:25:00",
                "price": {
                    "value": 63.07,
                    "valueMainUnit": "63",
                    "valueFractionalUnit": "07",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6006~ ~~LIL~06/14/2024 17:45~MRS~06/14/2024 19:25~~",
                "flightNumber": "FR6006",
                "previousPrice": null,
                "priceUpdated": 1710484251000
            },
            "summary": {
                "price": {
                    "value": 93.11,
                    "valueMainUnit": "93",
                    "valueFractionalUnit": "11",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "Italie",
                    "iataCode": "TSF",
                    "name": "Venise-Trévise",
                    "seoName": "venise-trevise",
                    "city": {
                        "name": "Venise",
                        "code": "VENICE",
                        "macCode": "VEN",
                        "countryCode": "it"
                    }
                },
                "departureDate": "2024-06-12T05:50:00",
                "arrivalDate": "2024-06-12T07:05:00",
                "price": {
                    "value": 24.29,
                    "valueMainUnit": "24",
                    "valueFractionalUnit": "29",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~2959~ ~~MRS~06/12/2024 05:50~TSF~06/12/2024 07:05~~",
                "flightNumber": "FR2959",
                "previousPrice": null,
                "priceUpdated": 1710485711000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "Italie",
                    "iataCode": "TSF",
                    "name": "Venise-Trévise",
                    "seoName": "venise-trevise",
                    "city": {
                        "name": "Venise",
                        "code": "VENICE",
                        "macCode": "VEN",
                        "countryCode": "it"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T15:30:00",
                "arrivalDate": "2024-06-14T16:55:00",
                "price": {
                    "value": 70.09,
                    "valueMainUnit": "70",
                    "valueFractionalUnit": "09",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~2960~ ~~TSF~06/14/2024 15:30~MRS~06/14/2024 16:55~~",
                "flightNumber": "FR2960",
                "previousPrice": null,
                "priceUpdated": 1710485173000
            },
            "summary": {
                "price": {
                    "value": 94.38,
                    "valueMainUnit": "94",
                    "valueFractionalUnit": "38",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        },
        {
            "outbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "NTE",
                    "name": "Nantes",
                    "seoName": "nantes",
                    "city": {
                        "name": "Nantes",
                        "code": "NANTES",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-12T20:30:00",
                "arrivalDate": "2024-06-12T22:00:00",
                "price": {
                    "value": 34.56,
                    "valueMainUnit": "34",
                    "valueFractionalUnit": "56",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6772~ ~~MRS~06/12/2024 20:30~NTE~06/12/2024 22:00~~",
                "flightNumber": "FR6772",
                "previousPrice": null,
                "priceUpdated": 1710486581000
            },
            "inbound": {
                "departureAirport": {
                    "countryName": "France",
                    "iataCode": "NTE",
                    "name": "Nantes",
                    "seoName": "nantes",
                    "city": {
                        "name": "Nantes",
                        "code": "NANTES",
                        "countryCode": "fr"
                    }
                },
                "arrivalAirport": {
                    "countryName": "France",
                    "iataCode": "MRS",
                    "name": "Marseille Provence",
                    "seoName": "marseille",
                    "city": {
                        "name": "Marseille",
                        "code": "MARSEILLE",
                        "countryCode": "fr"
                    }
                },
                "departureDate": "2024-06-14T09:00:00",
                "arrivalDate": "2024-06-14T10:25:00",
                "price": {
                    "value": 65.31,
                    "valueMainUnit": "65",
                    "valueFractionalUnit": "31",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "flightKey": "FR~6477~ ~~NTE~06/14/2024 09:00~MRS~06/14/2024 10:25~~",
                "flightNumber": "FR6477",
                "previousPrice": null,
                "priceUpdated": 1710493788000
            },
            "summary": {
                "price": {
                    "value": 99.87,
                    "valueMainUnit": "99",
                    "valueFractionalUnit": "87",
                    "currencyCode": "EUR",
                    "currencySymbol": "€"
                },
                "previousPrice": null,
                "newRoute": false,
                "tripDurationDays": 2
            }
        }
    ],
    "nextPage": null,
    "size": 19
}

"""