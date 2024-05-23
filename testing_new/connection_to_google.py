from google.oauth2.credentials import Credentials
import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
from fastapi import FastAPI
from fastapi import Request as fapi_Request
from fastapi import HTTPException
import uvicorn
import os
from dotenv import load_dotenv, set_key
import json

timezone = 'Europe/Moscow'
CALENDAR_ID = ''


def get_service():
    load_dotenv(override=True)
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    AUTH_USER_INFO = os.getenv('AUTHORIZED_USER_INFO')
    GOOGLE_REDIRECT_URL = os.getenv('GOOGLE_REDIRECT_URL')
    CREDENTIALS = os.getenv('CREDENTIALS')
    service = None
    try:
        creds = None
        if AUTH_USER_INFO:
            creds = Credentials.from_authorized_user_info(
                json.loads(AUTH_USER_INFO), SCOPES)
            service = googleapiclient.discovery.build(
                "calendar", "v3", credentials=creds)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                updated_creds = creds.to_json()  # Serialize the updated credentials to json
            # Update AUTHORIZED_USER_INFO in .env file
                set_key('.env', 'AUTHORIZED_USER_INFO', updated_creds,
                        quote_mode='always')
            else:
                # Создание flow для генерации URL аутентификации
                flow = InstalledAppFlow.from_client_config(
                    json.loads(CREDENTIALS), SCOPES, redirect_uri=GOOGLE_REDIRECT_URL)  # type: ignore
                auth_url, _ = flow.authorization_url(
                    prompt='consent')
                print('ОШИБКА, Необходима авторизация')
                print(
                    f"Перейдите по следующему URL для аутентификации: {auth_url}")
        return service
    except Exception as e:
        print(str(e))
