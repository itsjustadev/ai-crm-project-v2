from typing import Any
import aiohttp
import json
from abc import ABC, abstractmethod
from twilio.twiml import TwiML
from twilio.twiml.messaging_response import MessagingResponse
import asyncio
import os
from dotenv import load_dotenv
import requests

load_dotenv()
GET_EMAILS_ENDPOINT = str(os.getenv('GET_EMAILS_ENDPOINT'))
BROKER_EMAILS = str(os.getenv('BROKER_EMAILS'))
# ML_ENDPOINT = str(os.getenv('ML_ENDPOINT'))
# SEND_COMMAND_ENDPOINT = str(os.getenv('SEND_COMMAND_ENDPOINT'))
# OUT_API_KEY = str(os.getenv('OUTGOING_API_KEY'))


class AIConnection(ABC):
    def __init__(self, url: str, command_url: str, api_key: str) -> None:
        self.url = url
        self.command_url = command_url
        self.api_key = api_key

    @abstractmethod
    async def send_to_ml(self):
        pass


def get_emails_by_language(language, all_emails):
    emails = []
    try:
        brokers_emails = all_emails.get('email_list', {})
        email_list = brokers_emails.get(language, [])
        emails = email_list.copy()
    except Exception as e:
        print(str(e))
    finally:
        if not emails:
            emails.append('itsjustfortwits@gmail.com')
        return emails


def get_brokers_emails(url=GET_EMAILS_ENDPOINT):
    try:
        print(f'Отправка запроса к url: {GET_EMAILS_ENDPOINT}')
        response = requests.get(url, timeout=10)  # Выполнение GET запроса
        print(f'Status Code: {response.status_code}')
        final_result = response.json()  # Преобразование ответа из JSON
        print(f'Пришедшие emails с ML: {final_result}')
        email_list = final_result.get("email_list", {})
        if not email_list and BROKER_EMAILS:
            email_list = json.loads(BROKER_EMAILS)
        return email_list
    except Exception as e:
        print(str(e))
        return json.loads(BROKER_EMAILS)

# print(get_email_by_language('ru'))


class MLConnection(AIConnection):
    async def send_command_to_ml(self, cleaned_sender_number: str, command):
        if command == 'clear_hard':
            headers = {
                'api': self.api_key
            }
            params = {
                'user_id': cleaned_sender_number
            }
            print(f'PROCESS попытка отправки команды ML: {command}')
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(self.command_url, params=params, headers=headers) as response:
                        response_data = await response.text()
                        print(f'STATUS: {response.status}')
                        if response.status == 200:
                            print('Команды успешно отправлены ML')
                        else:
                            print('ERROR Команда не отправлена ML, но попытка была')
                        print(f'DATA: {response_data}')
                except Exception as e:
                    print(str(e))

    async def send_to_ml(self, command: str, client_id: str, client_message: str, logger):
        headers = {
            'accept': 'application/json',
            'api': self.api_key,  # API key
            'Content-Type': 'application/json'
        }
        body = {
            'command': command,
            'client_id': client_id,
            'client_message': client_message,
            "config": {
                "llm_model": "gpt-3.5-turbo",
                "temperature": 0.01,
                "system_prompt": "string"
            }
        }
        print(body)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.url, headers=headers, data=json.dumps(body)) as response:
                    response_data = await response.text()
                    print(f'STATUS: {response.status}')
                    print(f'DATA: {response_data}')
                    response_json = json.loads(response_data)  # response text
                    if logger:
                        logger.info('Ответ от ML: %s',
                                    response_json, exc_info=True)
                    return response_json
            except Exception as e:
                print(str(e))
                return {}


class Entity(ABC):
    def __init__(self, text: str) -> None:
        self.text = text


class MlService(Entity):
    def __init__(self, result_json) -> None:
        self.text = result_json.get('prediction', '')
        self.command = result_json.get('command', '')
        self.name = result_json.get('name', '')


class Bot(Entity):
    pass


class Twilio(Entity):
    def __init__(self, form_data) -> None:
        self.in_message = str(form_data.get('Body', '')).lower()
        self.sender_number = str(form_data.get('From', ''))
        self.response_template = MessagingResponse()
        self.out_message: TwiML | str
        self.final_message: Any
        self.command = ''

    def make_final_message(self, MlService: MlService, out_message):
        final_message = out_message.body(MlService.text)
        return final_message

    def parse_for_command(self):
        if self.in_message == '/clear':
            self.command = 'clear_history'
            self.in_message = ''
            return 'clear'
        elif self.in_message == '/clear_hard':
            self.command = 'clear_hard'
            self.in_message = ''
            return 'clear_hard'
