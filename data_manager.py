import os
import requests
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS_FILE = os.getenv('GOOGLE_CREDS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
SHEET_NAME = os.getenv('SHEET_NAME')
# SHEETY_PRICES_ENDPOINT = "https://api.sheety.co/61ee4ee3c079149a1cd904b876515a0f/flightDeals/prices"

#This class is responsible for talking to the Google Sheet.
class DataManager:
    def __init__(self):
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)
        self.destination_data = []

    def get_destination_data(self):
        read_range = f"'{SHEET_NAME}'!A1:C"
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=read_range)
            .execute()
        )
        values = result.get("values", [])
        if not values or len(values) < 2:
            return []

        header = values[0]
        rows = values[1:]

        def idx(col_name: str) -> int:
            return header.index(col_name)

        city_i = idx("City")
        iata_i = idx("IATA Code")
        price_i = idx("Lowest Price")

        data = []
        for row_num, row in enumerate(rows, start=2):
            city = row[city_i] if city_i < len(row) else ""
            iata = row[iata_i] if iata_i < len(row) else ""
            price = row[price_i] if price_i < len(row) else ""

            try:
                lowest = int(price)
            except (ValueError, TypeError):
                lowest = 0

            data.append(
                {
                    "id": row_num,
                    "city": city,
                    "iataCode": iata,
                    "lowestPrice": lowest,
                }
            )

        self.destination_data = data
        return data

    def update_destination_codes(self):
        updates = []
        for item in self.destination_data:
            row_num = item["id"]
            iata = item["iataCode"]
            updates.append(
                {
                    "range": f"{SHEET_NAME}!B{row_num}",
                    "values": [[iata]],
                }
            )

        body = {
            "valueInputOption": "RAW",
            "data": updates
        }

        (
            self.service.spreadsheets()
            .values()
            .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
            .execute()
        )
    def update_price_data(self):
        updates = []
        for item in self.destination_data:
            row_num = item["id"]
            lowest_price = item["lowestPrice"]
            updates.append(
                {
                    "range": f"{SHEET_NAME}!C{row_num}",
                    "values": [[lowest_price]],
                }
            )

            body = {
                "valueInputOption": "RAW",
                "data": updates
            }

            (
                self.service.spreadsheets()
                .values()
                .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
                .execute()
            )


