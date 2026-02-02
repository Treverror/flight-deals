import time
from pprint import pprint
from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
from datetime import datetime, timedelta

ORIGIN_IATA = "LAX"

departure_date = (datetime.now() + timedelta(days=1)).date()
return_date = departure_date + timedelta(days=5)

flight_search = FlightSearch()
data_manager = DataManager()
notification_manager = NotificationManager()

sheet_data = data_manager.get_destination_data()

prices = flight_search.search_for_flights(origin=ORIGIN_IATA, destination="TYO", departure_date=departure_date, return_date=return_date)
needs_update = False
for row in sheet_data:
    if row["iataCode"] == "":
        try:
            row["iataCode"] = flight_search.get_destination_code(row["city"])
            needs_update = True
            time.sleep(1)
        except ValueError as e:
            print(e)
            continue
if needs_update:
    data_manager.destination_data = sheet_data
    data_manager.update_destination_codes()

for row in sheet_data:
    destination = row["iataCode"]
    print(destination)
    flight_offers = flight_search.search_for_flights(
        origin=ORIGIN_IATA,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
    )
    print(flight_offers)
    cheapest_price  = flight_offers["cheapest_price"]

    if cheapest_price < row["lowestPrice"]:
        print(f"🔥 Deal found for {row['city']} {destination}: ${cheapest_price} < ${row['lowestPrice']}")
    row["lowestPrice"] = cheapest_price
    notification_manager.send_flight_info(cheapest_price, ORIGIN_IATA, destination, departure_date, return_date)


    data_manager.destination_data = sheet_data
    data_manager.update_price_data()