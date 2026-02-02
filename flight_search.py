from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
load_dotenv()

IATA_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations/cities"
FLIGHT_ENDPOINT = "https://test.api.amadeus.com/v2/shopping/flight-offers"
TOKEN_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"

class FlightSearch:
    def __init__(self):
        self._api_key = os.getenv('AMADEUS_API_KEY')
        self._api_secret = os.getenv('AMADEUS_API_SECRET')
        self._token = self._get_new_token()
    #This class is responsible for talking to the Flight Search API.
    # def _get_new_token(self):
    #     header = {'Content-Type': 'application/x-www-form-urlencoded'}
    #     body = {
    #         "grant_type": "client_credentials",
    #         "client_id": self._api_key,
    #         "client_secret": self._api_secret,
    #     }
    #     response = requests.post(url=TOKEN_ENDPOINT, headers=header, data=body)
    #     response.raise_for_status()
    #     print(f"Your token is {response.json()['access_token']}")
    #     print(f"Your token expires in {response.json()['expires_in']} seconds")
    #     return response.json()["access_token"]
    def _get_new_token(self):
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret
        }
        response = requests.post(url=TOKEN_ENDPOINT, headers=header, data=body)
        # New bearer token. Typically expires in 1799 seconds (30min)
        print(f"Your token is {response.json()['access_token']}")
        print(f"Your token expires in {response.json()['expires_in']} seconds")
        return response.json()['access_token']

    def get_destination_code(self, city_name):

        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "keyword": city_name,
            "max": 2,
        }
        response = requests.get(url=IATA_ENDPOINT, headers=headers, params=query)

        try:
            code = response.json()["data"][0]["iataCode"]
        except IndexError:
            print(f"IndexError: No airport code found for {city_name}.")
            return "N/A"
        except KeyError:
            print(f"KeyError: No airport code found for {city_name}.")
            return "Not Found"

        return code

    def search_for_flights(self, origin, destination, departure_date, return_date):
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        six_months_out = tomorrow + timedelta(days=180)

        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "returnDate": return_date,
            "adults": 1,
            "currencyCode": "USD",
            "max": 10,
        }
        response = requests.get(url=FLIGHT_ENDPOINT, headers=headers, params=query)
        if response.status_code != 200:
            print("STATUS:", response.status_code) 
            print("BODY:", response.text)
            return None
        data = response.json().get("data", [])
        if not data:
            return None

        prices = [float(o["price"]["grandTotal"]) for o in data[:10]]
        cheapest = min(prices)

        offers = response.json().get("data", [])
        price_list = []

        return {
            "cheapest_price": min(prices),
            "prices": prices,
            "offers": data,
        }
        print(len(response.json()["data"]))
