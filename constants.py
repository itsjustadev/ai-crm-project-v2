import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
OUT_API_KEY = str(os.getenv('OUTGOING_API_KEY'))
IN_API_KEY = str(os.getenv('INCOMING_API_KEY'))
TWILIO_TOKEN = str(os.getenv('TWILIO_TOKEN'))
REQUEST_URL = str(os.getenv('TWILIO_WEBHOOK_URL'))
ML_ENDPOINT = str(os.getenv('ML_ENDPOINT'))
CHANNEL_SECRET = str(os.getenv('CHANNEL_SECRET'))
SCOPE_ID = str(os.getenv('SCOPE_ID'))
RUS_TEMPLATE = "Добрый день! Я Сандра, менеджер компании The Honest Real Estate. Подскажите, как я могу к вам обращаться?"
ENG_TEMPLATE = "Good afternoon! I'm Sandra, the manager of The Honest Real Estate Company. Can you tell me how I can contact you?"
SEND_COMMAND_ENDPOINT = str(os.getenv('SEND_COMMAND_ENDPOINT'))
app = FastAPI()
