from dotenv import load_dotenv
import os
import json
import requests
from amo_connection.library_access import update_token


def get_uuid(full_link):
    url = full_link
    parts = url.split('/')
    uuid_index = parts.index('download') + 2

    if len(parts) > uuid_index:
        uuid = parts[uuid_index]
    else:
        uuid = ''
    return uuid

def get_link_for_download(uuid, client_id, client_secret, redirect_url, domain_name):
    load_dotenv()
    access_token = str(os.getenv('ACCESS_TOKEN'))
    get_url = "https://drive-b.amocrm.ru/v1.0/files/" + str(uuid)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(get_url, headers=headers)

    if response.status_code != 200:
        update_token(client_id, client_secret, redirect_url, domain_name)
        response = requests.get(get_url, headers=headers)
    if response.status_code == 200:
        value = response.text
    else:
        print(f"Произошла ошибка. Код ошибки: {response.status_code}")
        print("Сообщение об ошибке:")
        value = response.text
    try:
        data_dict = json.loads(value)
        download_link = data_dict.get("_links", {}).get("download", {}).get("href")
    except Exception as e:
        print(e)
        download_link = 0
    return download_link