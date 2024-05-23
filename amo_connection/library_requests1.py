import asyncio
from dotenv import load_dotenv
import os
import requests
import hashlib
import hmac
import json
from datetime import datetime
import pytz
import random
import string
import time
import aiohttp
import ssl
import certifi


# amo_in_logger = logging.getLogger('amo_in_logger')
# amo_in_logger.setLevel(logging.INFO)
# # Создайте обработчик и форматтер для логгера (пример)
# file_handler = logging.FileHandler('logs/amo_in_message_log.log')
# # Добавьте обработчик к логгеру
# amo_in_logger.addHandler(file_handler)

# amo_out_logger = logging.getLogger('amo_out_logger')
# amo_out_logger.setLevel(logging.INFO)
# # Создайте обработчик и форматтер для логгера (пример)
# file_handler1 = logging.FileHandler('logs/amo_out_message_log.log')
# # Добавьте обработчик к логгеру
# amo_out_logger.addHandler(file_handler1)


# load_dotenv()
CHANNEL_SECRET = str(os.getenv('CHANNEL_SECRET'))
# SCOPE_ID = str(os.getenv('SCOPE_ID'))
ssl_context = ssl.create_default_context(cafile=certifi.where())
# amojo_id = str(os.getenv('AMOJO_ID'))
scope_id = str(os.getenv('SCOPE_ID'))
secret = str(os.getenv('CHANNEL_SECRET'))
# channel_id = str(os.getenv('CHANNEL_ID'))
# method = 'POST'
# content_type = 'application/json'
# timezone = pytz.timezone('Europe/Moscow')
# date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
# path = f'/v2/origin/custom/{scope_id}/chats'
# url = "https://amojo.amocrm.ru" + path
# path1 = f'/v2/origin/custom/{scope_id}'
# url1 = "https://amojo.amocrm.ru" + path1
# base_url = 'https://amojo.amocrm.ru'


def amo_connect_account_with_chat_channel(amojo_id, channel_id, secret):
    timezone = pytz.timezone('Europe/Moscow')
    date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')

    method = 'POST'
    content_type = 'application/json'

    base_url = 'https://amojo.amocrm.ru'
    body = {
        "account_id": amojo_id,
        "title": "ChatIntegration",
        "hook_api_version": "v2"
    }
    url_new = base_url + f'/v2/origin/custom/{channel_id}/connect'

    request_body = json.dumps(body)
    check_sum = hashlib.md5(request_body.encode()).hexdigest()
    path = f'/v2/origin/custom/{channel_id}/connect'

    str_to_sign = "\n".join([
        method,
        check_sum,
        content_type,
        date,
        path,
    ])

    signature = hmac.new(secret.encode(), str_to_sign.encode(),
                         hashlib.sha1).hexdigest()

    headers = {
        'Date': date,
        'Content-Type': content_type,
        'Content-MD5': check_sum.lower(),
        'X-Signature': signature.lower(),
    }
    response = requests.post(url_new, data=request_body, headers=headers)

    print("Status:", response.status_code)
    print(response.text)
    return response


def forming_body(chat_id, user_id, user_name):
    body = {
        "conversation_id": "skt-8e3e7640-49af-4448-a2c7-" + chat_id,
        "source": {
            "external_id": "leadgrambot"
        },
        "user": {
            "id": "skt-1376265f-86df-4c49-a0c4-" + user_id,
            "name": user_name,
            "profile": {
                "email": "example-psy.client@example.com"
            }
        }
    }
    return body


def forming_body1(chat_id, user_id, user_name, message_text):
    characters = list(string.digits + string.ascii_lowercase)
    random.shuffle(characters)
    random_sequence = ''.join(random.choices(characters, k=12))
    timestamp = int(time.time())
    msec_timestamp = int(time.time() * 1000)
    body1 = {
        "event_type": "new_message",
        "payload": {
            "timestamp": timestamp,
            "msec_timestamp": msec_timestamp,
            "msgid": "intt-" + random_sequence,
            "conversation_id": "skt-8e3e7640-49af-4448-a2c7-" + chat_id,
            "sender": {
                "id": "skt-1376265f-86df-4c49-a0c4-" + user_id,
                "profile": {
                    "email": "example-psy.client@example.com"
                },
                "name": user_name
            },
            "message": {
                "type": "text",
                "text": message_text
            },
            "silent": False
        }
    }
    return body1


def forming_body_for_files(chat_id, user_id, user_name, download_url):
    characters = list(string.digits + string.ascii_lowercase)
    random.shuffle(characters)
    random_sequence = ''.join(random.choices(characters, k=12))
    timestamp = int(time.time())
    msec_timestamp = int(time.time() * 1000)
    body1 = {
        "event_type": "new_message",
        "payload": {
            "timestamp": timestamp,
            "msec_timestamp": msec_timestamp,
            "msgid": "intt-" + random_sequence,
            "conversation_id": "skt-8e3e7640-49af-4448-a2c7-" + chat_id,
            "sender": {
                "id": "skt-1376265f-86df-4c49-a0c4-" + user_id,
                "profile": {
                    "email": "example-psy.client@example.com"
                },
                "name": user_name
            },
            "message": {
                "type": "file",
                "media": download_url
            },
            "silent": False
        }
    }
    return body1


def forming_body_for_pictures(chat_id, user_id, user_name, download_url):
    characters = list(string.digits + string.ascii_lowercase)
    random.shuffle(characters)
    random_sequence = ''.join(random.choices(characters, k=12))
    timestamp = int(time.time())
    msec_timestamp = int(time.time() * 1000)
    body1 = {
        "event_type": "new_message",
        "payload": {
            "timestamp": timestamp,
            "msec_timestamp": msec_timestamp,
            "msgid": "intt-" + random_sequence,
            "conversation_id": "skt-8e3e7640-49af-4448-a2c7-" + chat_id,
            "sender": {
                "id": "skt-1376265f-86df-4c49-a0c4-" + user_id,
                "profile": {
                    "email": "example-psy.client@example.com"
                },
                "name": user_name
            },
            "message": {
                "type": "picture",
                "media": download_url
            },
            "silent": False
        }
    }
    return body1


def forming_body_answer(chat_id, user_id, user_name, outgoing_message_text):
    characters = list(string.digits + string.ascii_lowercase)
    random.shuffle(characters)
    random_sequence = ''.join(random.choices(characters, k=12))
    timestamp = int(time.time())
    msec_timestamp = int(time.time() * 1000)
    body_answer = {
        "event_type": "new_message",
        "payload": {
            "timestamp": timestamp + 1,
            "msec_timestamp": msec_timestamp + 1000,
            "msgid": "intt-" + random_sequence,
            "conversation_id": "skt-8e3e7640-49af-4448-a2c7-" + chat_id,
            "sender": {
                "id": "skt-1376265f-86df-4c49-a0c4",
                "name": "Bot",
                "ref_id": "f1910c7f-b1e0-4184-bd09-c7def2a9109a"
            },
            "receiver": {
                "id": "skt-1376265f-86df-4c49-a0c4-" + user_id,
                "name": user_name,
                "profile": {
                    "email": "example-psy.client@example.com"
                }
            },
            "message": {
                "type": "text",
                        "text": outgoing_message_text
            },
            "silent": False
        }
    }
    return body_answer


def amo_chat_create_vk(chat_id: str, user_id: str, user_name: str, secret, scope_id):
    body = forming_body(chat_id, user_id, user_name)
    method = 'POST'
    content_type = 'application/json'
    timezone = pytz.timezone('Europe/Moscow')
    date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
    path = f'/v2/origin/custom/{scope_id}/chats'
    url = "https://amojo.amocrm.ru" + path

    request_body = json.dumps(body)
    check_sum = hashlib.md5(request_body.encode()).hexdigest()

    str_to_sign = "\n".join([
        method,
        check_sum,
        content_type,
        date,
        path,
    ])

    signature = hmac.new(secret.encode(), str_to_sign.encode(),
                         hashlib.sha1).hexdigest()

    headers = {
        'Date': date,
        'Content-Type': content_type,
        'Content-MD5': check_sum.lower(),
        'X-Signature': signature.lower(),
    }
    response = requests.post(url, data=request_body, headers=headers)

    print("Status:", response.status_code)
    print(response.text)
    return response


def amo_chat_create(chat_id: str, user_id: str, user_name: str, scope_id, secret):
    body = forming_body(chat_id, user_id, user_name)
    method = 'POST'
    content_type = 'application/json'
    timezone = pytz.timezone('Europe/Moscow')
    date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
    path = f'/v2/origin/custom/{scope_id}/chats'
    url = "https://amojo.amocrm.ru" + path

    request_body = json.dumps(body)
    check_sum = hashlib.md5(request_body.encode()).hexdigest()

    str_to_sign = "\n".join([
        method,
        check_sum,
        content_type,
        date,
        path,
    ])

    signature = hmac.new(secret.encode(), str_to_sign.encode(),
                         hashlib.sha1).hexdigest()

    headers = {
        'Date': date,
        'Content-Type': content_type,
        'Content-MD5': check_sum.lower(),
        'X-Signature': signature.lower(),
    }
    response = requests.post(url, data=request_body, headers=headers)

    print("Status:", response.status_code)
    print(response.text)
    return response


# amo_chat_create('122324', '122324', 'Alex', scope_id, secret)


# amo_share_incoming_message()


def amo_share_incoming_file(chat_id: str, user_id: str, user_name: str, download_url: str, scope_id, secret):
    body1 = forming_body_for_files(chat_id, user_id, user_name, download_url)

    request_body = json.dumps(body1)
    check_sum = hashlib.md5(request_body.encode()).hexdigest()
    method = 'POST'
    content_type = 'application/json'
    timezone = pytz.timezone('Europe/Moscow')
    date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
    path = f'/v2/origin/custom/{scope_id}/chats'
    path1 = f'/v2/origin/custom/{scope_id}'
    url1 = "https://amojo.amocrm.ru" + path1

    str_to_sign = "\n".join([
        method,
        check_sum,
        content_type,
        date,
        path1,
    ])

    signature = hmac.new(secret.encode(), str_to_sign.encode(),
                         hashlib.sha1).hexdigest()

    headers = {
        'Date': date,
        'Content-Type': content_type,
        'Content-MD5': check_sum.lower(),
        'X-Signature': signature.lower(),
    }
    response = requests.post(url1, data=request_body, headers=headers)

    print("Status:", response.status_code)
    print(response.text)
    return response.status_code


def amo_share_incoming_picture(chat_id: str, user_id: str, user_name: str, download_url: str, scope_id, secret):
    body1 = forming_body_for_pictures(
        chat_id, user_id, user_name, download_url)
    method = 'POST'
    content_type = 'application/json'
    timezone = pytz.timezone('Europe/Moscow')
    date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
    path = f'/v2/origin/custom/{scope_id}/chats'
    path1 = f'/v2/origin/custom/{scope_id}'
    url1 = "https://amojo.amocrm.ru" + path1

    request_body = json.dumps(body1)
    check_sum = hashlib.md5(request_body.encode()).hexdigest()

    str_to_sign = "\n".join([
        method,
        check_sum,
        content_type,
        date,
        path1,
    ])

    signature = hmac.new(secret.encode(), str_to_sign.encode(),
                         hashlib.sha1).hexdigest()

    headers = {
        'Date': date,
        'Content-Type': content_type,
        'Content-MD5': check_sum.lower(),
        'X-Signature': signature.lower(),
    }
    response = requests.post(url1, data=request_body, headers=headers)

    print("Status:", response.status_code)
    print(response.text)
    return response.status_code


async def amo_share_incoming_message(chat_id: str, user_id: str, user_name: str, message_text: str, scope_id, secret):
    body1 = forming_body1(chat_id, user_id, user_name, message_text)
    # logging.basicConfig(filename='amo_logs.txt', level=logging.INFO)
    request_body = json.dumps(body1)
    check_sum = hashlib.md5(request_body.encode()).hexdigest()
    method = 'POST'
    content_type = 'application/json'
    timezone = pytz.timezone('Europe/Moscow')
    date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
    path = f'/v2/origin/custom/{scope_id}/chats'
    url = "https://amojo.amocrm.ru" + path
    path1 = f'/v2/origin/custom/{scope_id}'
    url1 = "https://amojo.amocrm.ru" + path1

    str_to_sign = "\n".join([
        method,
        check_sum,
        content_type,
        date,
        path1,
    ])

    signature = hmac.new(secret.encode(), str_to_sign.encode(),
                         hashlib.sha1).hexdigest()

    headers = {
        'Date': date,
        'Content-Type': content_type,
        'Content-MD5': check_sum.lower(),
        'X-Signature': signature.lower(),
    }
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.post(url1, data=request_body, headers=headers) as response:
            print('Попытка поделиться входящим сообщением')
            print("Status:", response.status)
            text = await response.text()
            print(text)
            response_json = json.loads(text)
            # Используем .get() для безопасного извлечения значения conversation_id
            conversation_id = response_json.get(
                'new_message', {}).get('conversation_id', '')
            return conversation_id

# conversation_id = asyncio.run(amo_share_incoming_message(
#     '12232456', '12232456', 'Alexy', 'heyyyy1', scope_id, secret))


async def amo_share_outgoing_message(chat_id: str, user_id: str, user_name: str, message_text: str, scope_id, secret):
    body2 = forming_body_answer(chat_id, user_id, user_name, message_text)

    request_body = json.dumps(body2)
    check_sum = hashlib.md5(request_body.encode()).hexdigest()
    method = 'POST'
    content_type = 'application/json'
    timezone = pytz.timezone('Europe/Moscow')
    date = datetime.now().astimezone(timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
    path = f'/v2/origin/custom/{scope_id}/chats'
    path1 = f'/v2/origin/custom/{scope_id}'
    url1 = "https://amojo.amocrm.ru" + path1
    url = "https://amojo.amocrm.ru" + path

    str_to_sign = "\n".join([
        method,
        check_sum,
        content_type,
        date,
        path1,
    ])

    signature = hmac.new(
        secret.encode(), str_to_sign.encode(), hashlib.sha1).hexdigest()

    headers = {
        'Date': date,
        'Content-Type': content_type,
        'Content-MD5': check_sum.lower(),
        'X-Signature': signature.lower(),
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.post(url1, data=request_body, headers=headers) as response:
            print('Попытка поделиться исходящим сообщением')
            print("Status:", response.status)
            text = await response.text()
            print(text)
            return response.status


# asyncio.run(amo_share_incoming_message('1223312', '1223312', 'Ivan',
#                                        'Тоже', scope_id, CHANNEL_SECRET))
# asyncio.run(amo_share_outgoing_message('122331', '122331', 'Ivan',
#                                        'Все супер', SCOPE_ID, CHANNEL_SECRET))

