from http.client import responses
import logging
import os
from twilio.request_validator import RequestValidator
from amo_connection.library_requests1 import amo_share_incoming_message, amo_share_outgoing_message
from constants import *
import databases.databases as DB
import sys
import re
from amo_connection.library_access import amo_change_lead_status, amo_change_user_name, get_amo_user
from testing_new.get_events import *
from fastapi import HTTPException


def get_slots(email):
    busy_times = get_busy_times_with_participant(
        email)
    if busy_times is None:
        print('need authorization to google')
        raise HTTPException(
            status_code=500, detail="need authorization to google")
    print(
        f'Занятые в календаре слоты на сегодня: {busy_times}')
    free_slots = find_free_slots(busy_times)
    print(
        f'Подходящие для записи слоты на сегодня: {free_slots}')
    final_slots = get_suitable_slots(free_slots)
    return final_slots


def check_slots_exist(emails):
    print(emails)
    final_email = None
    if emails:
        for email in emails:
            final_slots = get_slots(email)
            if final_slots:
                final_email = email
                print(
                    f'Итоговый email: {final_email}')
                break
    return final_email


def add_symbols_to_number(input_string):
    # Ищем индекс первого вхождения цифры в строке
    digit_index = next(i for i, char in enumerate(
        input_string) if char.isdigit())

    # Формируем новую строку с добавленной строкой ':+' между буквами и цифрами
    result_string = input_string[:digit_index] + \
        ':+' + input_string[digit_index:]

    return result_string


def get_text_by_command(command):
    text = ''
    if command == 'completed':
        text = 'Ожидайте менеджера.'
    return text


def check_if_need_template(user_id, user_message, command):
    if DB.check_user_already_exists(user_id) and not command:
        template = ''
    else:
        template = get_first_message_template(user_message)
        DB.add_new_user(user_id)
    return template


def form_final_message_response(template: str):
    addition = ''
    if template:
        addition = f'<Message>{template}</Message>'
    response_xml = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <Response>
                {addition}
            </Response>
            """
    return response_xml


def get_first_message_template(user_message):
    # Регулярное выражение для поиска русских букв
    russian_letters = re.findall(r'[А-Яа-яЁё]', user_message)
    # Регулярное выражение для поиска нерусских букв
    non_russian_letters = re.findall(r'[^\sА-Яа-яЁё]', user_message)
    # Проверяем, больше ли русских букв, чем всех остальных символов вместе взятых
    if len(russian_letters) > len(non_russian_letters) or user_message in ('/clear', '/clear_hard'):
        template = RUS_TEMPLATE
    else:
        template = ENG_TEMPLATE
    return template


async def amo_share_client_message(sender_number, in_message):
    conversation_id = await amo_share_incoming_message(sender_number, sender_number, '', in_message, SCOPE_ID, CHANNEL_SECRET)
    DB.add_conversation_id(sender_number, conversation_id)


async def amo_share_current_messages(ml_service, twilios):
    await amo_share_outgoing_message(twilios.sender_number, twilios.sender_number, ml_service.name,
                                     ml_service.text, SCOPE_ID, CHANNEL_SECRET)


async def parse_ml_command(ml_service, twilios, logger):
    if ml_service.command == 'completed':
        logger.info(f'С ml получена команда completed: {ml_service.command}')
        ml_service.text = get_text_by_command(ml_service.command)
        logger.info(f'Изменяю текст для ml_service.text на: {ml_service.text}')
    elif ml_service.command == 'set_name':
        logger.info(f'С ml получена команда set_name: {ml_service.command}')
        lead_id = DB.get_lead_id_by_user(twilios.sender_number)
        contact_id = get_amo_user(lead_id)
        amo_change_user_name(contact_id, ml_service.name)


def remove_name_and_capitalize(text, word_to_remove):
    # Разбиваем текст на слова с учетом возможной пунктуации после первого слова
    words = text.split()
    if words:
        # Создаем паттерн для проверки первого слова с опциональной пунктуацией
        pattern = re.compile(
            rf"^{re.escape(word_to_remove)}[\.,;!\?\s]*$", re.IGNORECASE)
        if pattern.match(words[0]):
            # Удаляем первое слово
            words.pop(0)
            if words:
                # Делаем первую букву следующего слова заглавной
                words[0] = words[0].capitalize()
        return " ".join(words)
    return text


async def parse_ml_answer(ml_service, twilios, logger):
    if ml_service.command:
        logger.info(f'С ml получена команда: {ml_service.command}')
        await parse_ml_command(ml_service, twilios, logger)
    if ml_service.name:
        if ml_service.text:
            ml_service.text = remove_name_and_capitalize(
                ml_service.text, ml_service.name)
        logger.info(f'С ml получено имя: {ml_service.name}')
        await amo_share_current_messages(ml_service, twilios)
    elif ml_service.text:
        await amo_share_current_messages(ml_service, twilios)


def write_first_history(twilios, outgoing_text, logger):
    logger.info(
        f'C ml не получено имя, но получено сообщение, либо template установлен: {outgoing_text}')
    DB.add_in_first_history(twilios.sender_number, '',
                            twilios.in_message, outgoing_text, '')


def get_special_id_if_exists(twilios):
    special_user_id = None
    try:
        special_user_id = DB.get_special_user_id(twilios.sender_number)
        if special_user_id:
            special_user_id = special_user_id + \
                str(int(special_user_id[-1])+1)
        else:
            special_user_id = twilios.sender_number + \
                str(int(twilios.sender_number[-1])+1)
        DB.add_special_user_id(twilios.sender_number, special_user_id)
    except Exception as e:
        print('Ошибка в функции get_special_user_id ' + str(e))
    finally:
        return special_user_id if special_user_id else twilios.sender_number


def clean_id_from_symbols(user_id: str):
    modified_string = user_id.replace(':', '')
    modified_string = modified_string.replace('+', '')
    return modified_string


def if_special_user_id(twilios, command):
    ordinary_or_special_userid = twilios.sender_number
    if command == 'clear':
        ordinary_or_special_userid = get_special_id_if_exists(twilios)
    special_id = DB.get_special_user_id(twilios.sender_number)
    if special_id:
        ordinary_or_special_userid = special_id
    modified_string = clean_id_from_symbols(ordinary_or_special_userid)
    return modified_string


def get_logger():
    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '\n%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line %(lineno)d')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


async def amo_share_first_history(history_dict, name, scope_id, secret):
    client_id = history_dict.get('client_id')
    response_status_code = 0
    if client_id:
        for key, message in history_dict.items():
            if key.startswith('incoming'):
                response_status_code = await amo_share_incoming_message(client_id, client_id, name, message, scope_id, secret)
            elif key.startswith('outgoing'):
                response_status_code = await amo_share_outgoing_message(client_id, client_id, name, message, scope_id, secret)
    return response_status_code


def catch_exceptions_with(logger):
    # Сам декоратор, использующий переданный логгер
    def decorator(f):
        async def wrapper(*args, **kwargs):
            try:
                return await f(*args, **kwargs)
            except Exception as e:
                logger.error('ERROR '+str(e), exc_info=True)
        return wrapper
    return decorator


async def check_signature(REQUEST_URL, request, validator):
    params = await request.form()
    twilio_signature = request.headers.get('X-Twilio-Signature', None)
    if twilio_signature and validator.validate(REQUEST_URL, params, twilio_signature):
        return True
    else:
        return False
