from fastapi import Header, HTTPException, BackgroundTasks
from fastapi import Request as fapi_Request
from fastapi.responses import PlainTextResponse
import uvicorn
from api_connection.to_ml_request import *
from helpers import *
from constants import *
from amo_connection.library_access import *
from pydantic import BaseModel
from testing_new.google_meet import *
from testing_new.get_events import *
from twilio_functions.send_message import send_whatsapp_message
import urllib.parse
import databases.databases as DB

# Перед запуском задать twilio webhook url!
ai_connection = MLConnection(ML_ENDPOINT, SEND_COMMAND_ENDPOINT, OUT_API_KEY)
validator = RequestValidator(TWILIO_TOKEN)
logger_in_out = get_logger()
all_emails = {'email_list': None}
fields_dictionary = {
    "Категория": 111111,
    "Тип объекта": 111111,
    "Бюджет клиента": 111111,
    "Ожидаемая дата сделки": 111111,
    "Язык": 111111
}


class ShareInfoRequest(BaseModel):
    user_id: str
    field_name: str
    value: str


class GetSlotsRequest(BaseModel):
    user_id: str
    language: str
    command: str


class SetMeetingRequest(BaseModel):
    user_id: str
    language: str
    command: str
    meeting_start: str
    meeting_end: str


def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8080)


async def twilio_request_handling(twilios: Twilio, command):
    '''
    Дальнейшая обработка пришедшего вебхука от Twilio
    '''
    try:
        # отправка входящего сообщения в амо
        await amo_share_client_message(twilios.sender_number, twilios.in_message)
        # отправка сообщения в ML
        logger_in_out.info(f'Команда: {command}')
        ordinary_or_special_userid = if_special_user_id(twilios, command)
        logger_in_out.info(
            f'INPUT: id {ordinary_or_special_userid}, входящее сообщение: {twilios.in_message}', exc_info=True)
        result_json = await ai_connection.send_to_ml(twilios.command, ordinary_or_special_userid, twilios.in_message, logger_in_out)
        logger_in_out.info(f'Пришедший ответ от ML: {result_json}')
    # разбор ответа от ML
        ml_service = MlService(result_json)
        await update_token(client_id, client_secret, redirect_url, domain_name)
        await parse_ml_answer(ml_service, twilios, logger_in_out)
        if not ml_service.text:
            logger_in_out.error(
                'Ошибка, итогового текста нет (ml_service.text пуст)')
        else:
            send_whatsapp_message(
                ml_service.text, twilios.sender_number, command)
    except Exception as e:
        logger_in_out.error('ERROR '+str(e), exc_info=True)


@app.post("/webhook1233424224441")
async def receive_message(request: fapi_Request, tasks: BackgroundTasks):
    '''
    Эндпоинт приема пришедшего вебхука от Twilio
    '''
    try:
        logger_in_out.info(
            'PROCESS Обработка запроса с пришедшем от twilio сообщением')
        if not await check_signature(REQUEST_URL, request, validator):
            logger_in_out.info(
                'Подпись signature не является ожидаемой, процесс обработки запроса остановлен')
            raise HTTPException(status_code=403, detail="Access denied")
        form_data = await request.form()  # type: ignore
        twilios = Twilio(form_data)
    # Проверка на наличие команд
        command = twilios.parse_for_command()
        template = check_if_need_template(
            twilios.sender_number, twilios.in_message, command)
    # Очищаем id от спец символов для отдачи ML
        cleaned_user_id = clean_id_from_symbols(twilios.sender_number)
    # Отправляем команду ML
        print(f'{cleaned_user_id} ')
        print(f'{twilios.in_message}')
        await ai_connection.send_command_to_ml(cleaned_user_id, command)
        if command == 'clear_hard' or command == 'clear':
            DB.delete_command_set_name(twilios.sender_number)
        if not template and command != 'clear_hard':
            tasks.add_task(twilio_request_handling, twilios, command)
        else:
            write_first_history(twilios, template, logger_in_out)
        response_xml = form_final_message_response(template)
        return PlainTextResponse(content=response_xml, media_type='application/xml')
    except Exception as e:
        logger_in_out.error('ERROR '+str(e), exc_info=True)


@app.post("/free_slots12new12")
async def get_free_slots(request: GetSlotsRequest, api_key: str = Header(...)):
    '''
    Эндпоинт для получения свободных слотов в календаре
    '''
    try:
        if api_key != IN_API_KEY:
            logger_in_out.info('Api ключ не подошел')
            raise HTTPException(status_code=401, detail="Invalid API key")
        user_number = add_symbols_to_number(request.user_id)
        lead_id = DB.get_lead_id_by_user(user_number)
        request_data = request.json()
        logger_in_out.info(
            f'PROCESS Обработка запроса на получение свободных слотов, полный номер клиента: {user_number}, lead_id: {lead_id}')
        logger_in_out.info(
            f'Пришедший запрос с api: {request_data}')
    # Проверяем API ключ
        logger_in_out.info('Api ключ подошел')
        logger_in_out.info(f'Язык для запроса email: {request.language}')
        emails = get_emails_by_language(request.language, all_emails)
        email = check_slots_exist(emails)
        print(email)
        if email:
            logger_in_out.info(f'Выбранный email: {email}')
            final_slots = get_slots(email)
            logger_in_out.info(
                f'Итоговые слоты для отправки ML: {final_slots}')
        else:
            logger_in_out.info(f'Ошибка, email не получен!: {email}')
            final_slots = []
        if final_slots == []:
            amo_change_lead_status(lead_id, '65061942')
        return {"slots": final_slots}
    except Exception as e:
        logger_in_out.error('ERROR '+str(e), exc_info=True)


def get_meeting_link(request, email):
    '''
    Получение итоговой ссылки для встречи
    '''
    time_start = request.meeting_start
    time_end = request.meeting_end
    logger_in_out.info(
        f'Время начала встречи в iso_format: {time_start}')
    logger_in_out.info(
        f'Время окончания встречи в iso_format: {time_end}')
    is_data_actual = check_date_not_previous(time_start)
    if is_data_actual:
        meeting_link = set_google_meeting(
            time_start, time_end, 'new_test_meeting', email)
    else:
        meeting_link = ''
    return meeting_link


@app.post("/set_meeting12new12")
async def set_meeting(request: SetMeetingRequest, api_key: str = Header(...)):
    '''
    Эндпоинт назначения встречи
    '''
    try:
        if api_key != IN_API_KEY:
            logger_in_out.info('Api ключ не подошел')
            raise HTTPException(status_code=401, detail="Invalid API key")
        user_number = add_symbols_to_number(request.user_id)
        lead_id = DB.get_lead_id_by_user(user_number)
        request_data = request.json()
        logger_in_out.info(
            f'PROCESS Обработка запроса на назначение встречи google_meet, полный номер клиента: {user_number}, lead_id: {lead_id}')
        logger_in_out.info(
            f'Пришедший запрос с api: {request_data}')
    # Проверяем API ключ
        logger_in_out.info('Api ключ подошел')
        emails = get_emails_by_language(request.language, all_emails)
        email = check_slots_exist(emails)
        amo_change_custom_field(
            lead_id, request.language, 1570483, 'Язык')
        if email:
            logger_in_out.info(f'Выбранный email: {email}')
            meeting_link = get_meeting_link(request, email)
            logger_in_out.info(
                f'Полученная ссылка и отправленная ml ссылка: {meeting_link}')
            if meeting_link:
                amo_change_lead_status(
                    lead_id, '65061938')
                amo_change_custom_field(
                    lead_id, meeting_link, 1568953, 'Ссылка на встречу')
            amo_change_custom_field(lead_id, email, 1570465, 'Email брокера')
        else:
            meeting_link = None
        if meeting_link is None:
            logger_in_out.info('need authorization to google or email')
            raise HTTPException(
                status_code=500, detail="need authorization to google or email")
        if not meeting_link:
            amo_change_lead_status(
                lead_id, '66006762')
        return {"meeting_link": meeting_link}
    except Exception as e:
        logger_in_out.error('ERROR '+str(e), exc_info=True)


@app.post("/info_share_amo12new12")
async def share_info_with_amo(request: ShareInfoRequest, api_key: str = Header(...)):
    '''
    Эндпоинт изменения полей в амо
    '''
    try:
        if api_key != IN_API_KEY:
            logger_in_out.info('Api ключ не подошел')
            raise HTTPException(status_code=401, detail="Invalid API key")
        user_number = add_symbols_to_number(request.user_id)
        lead_id = DB.get_lead_id_by_user(user_number)
        request_data = request.json()
        logger_in_out.info(
            'PROCESS Обработка запроса поделитьcя информацией с амо')
        logger_in_out.info(
            f'Пришедший запрос с api: {request_data}')
    # Проверяем API ключ
        logger_in_out.info('Api ключ подошел')
        amo_change_custom_field(lead_id, request.value, fields_dictionary.get(
            request.field_name, 0), request.field_name)
        if request.field_name == 'Тип объекта' and not DB.was_set_name(user_number):
            lead_id = DB.get_lead_id_by_user(user_number)
            print(
                f'Пробуем изменить статус на статус обработки для сделки: {lead_id}')
            response_text = amo_change_lead_status(lead_id, '65061934')
            print(response_text)
            DB.add_new_set_name(user_number)
        return {"result": "good"}
    except Exception as e:
        logger_in_out.error('ERROR '+str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Exception")


# эндпоинт, обрабатывающий смену этапа в амо
@app.post("/json12222331jsdflfjblsa10")
async def handle_amo_stage_change(request: fapi_Request):
    '''
    Эндпоинт приема вебхука от амо о смене этапа
    '''
    headers = dict(request.headers)
    if 'amoCRM' in headers['user-agent']:
        try:
            body = await request.body()
            parsed_data = urllib.parse.parse_qsl(body.decode("utf-8"))
            lead_id = parsed_data[0][1]
            status_id = parsed_data[1][1]
            entity_id = get_entity_id(lead_id, logger_in_out)
            conversation_id = get_amo_conversation_id(entity_id, logger_in_out)
            logger_in_out.info(
                f'Для сделки {lead_id} изменен статус на {status_id}', exc_info=True)
            print(conversation_id)
            user_number = DB.get_user_id_by_conversation(conversation_id)
            print(user_number, lead_id)
            if user_number and lead_id:
                DB.add_lead_id(user_number, lead_id)
                only_number = user_number[user_number.index('+'):]
                amo_change_custom_field(
                    lead_id, only_number, 1570387, 'Номер телефона')
            if str(status_id) == '65061926':
                amo_change_lead_status(
                    lead_id, '65061930', access_token, domain_name)
                all_emails['email_list'] = get_brokers_emails()
        except Exception as e:
            logger_in_out.error(
                'ERROR in handle amo stage change: '+str(e), exc_info=True)


if __name__ == "__main__":
    run_server()
