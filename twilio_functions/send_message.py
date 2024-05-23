from constants import RUS_TEMPLATE
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()
account_sid = str(os.getenv('ACCOUNT_SID'))
auth_token = str(os.getenv('TWILIO_TOKEN'))
twilio_number = str(os.getenv('TWILIO_NUMBER'))
client = Client(account_sid, auth_token)


def send_whatsapp_message(text: str, to_number: str, command):
    if command:
        text = RUS_TEMPLATE
    message = client.messages.create(
        body=text,
        # Ваш Twilio WhatsApp номер, +14155238886 - это номер sandbox
        from_='whatsapp:' + twilio_number,
        # Номер получателя, должен быть зарегистрирован в вашем WhatsApp Sandbox
        to=to_number
    )

