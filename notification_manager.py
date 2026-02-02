from dotenv import load_dotenv
import os
from twilio.rest import Client
load_dotenv()
class NotificationManager:
    #This class is responsible for sending notifications with the deal flight details.
    def __init__(self):
        self._client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        self.trip_info = []

    def send_flight_info(self, price, departure_iata, arrival_iata, outbound_date, inbound_date):
        formatted_message = f"-Low price alert! Only ${price} to fly from {departure_iata} to {arrival_iata}, on {outbound_date} until {inbound_date}"
        message = self._client.messages.create(
            from_=os.getenv('WHATSAPP_FROM'),
            body=formatted_message,
            to=os.getenv('WHATSAPP_TO'),
        )
        return message