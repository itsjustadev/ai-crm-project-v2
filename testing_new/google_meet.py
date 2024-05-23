import pytz
import datetime
from datetime import date, timedelta
from testing_new.connection_to_google import CALENDAR_ID, timezone, get_service


def get_occupied_hours(start_time, end_time):

    # Преобразуем строки в объекты datetime для удобства вычислений
    start_dt = datetime.datetime.strptime(start_time, '%H:%M')
    end_dt = datetime.datetime.strptime(end_time, '%H:%M')

    # Проверяем, что конечное время после начального, иначе возвращаем пустой список
    if end_dt <= start_dt:
        return []

    # Инициализируем список занятых часов
    occupied_hours = []

    # Начинаем с часа следующего за начальным временем
    current_hour = start_dt + timedelta(hours=1)
    occupied_hours.append(start_dt.strftime('%H'))

    # Добавляем часы в список, пока не достигнем часа, предшествующего конечному времени
    while current_hour < end_dt:
        occupied_hours.append(current_hour.strftime('%H'))
        current_hour += timedelta(hours=1)
    return occupied_hours


# Пример использования функции
#start_time = "06:30"
#end_time = "13:45"
#occupied_hours = get_occupied_hours(start_time, end_time)
#print("Занятые часы:", occupied_hours)


def get_offset_timedelta(timezone):
    current_timezone = pytz.timezone(timezone)
    current_time = datetime.datetime.now(current_timezone)
    offset_timedelta = current_time.utcoffset()
    return offset_timedelta


def get_time_offset(timezone):
    formatted_offset = ''
    offset_timedelta = get_offset_timedelta(timezone)
    if offset_timedelta:
        # Преобразуем смещение в часы и минуты
        offset_hours = offset_timedelta.seconds // 3600
        # Форматируем строку смещения
        formatted_offset = f"+{offset_hours:02d}:00"
    return formatted_offset


def get_hours_delta(timezone):
    offset_hours = 0
    offset_timedelta = get_offset_timedelta(timezone)
    if offset_timedelta:
        offset_hours = offset_timedelta.seconds // 3600
    return offset_hours


today_date = date.today()
time_offset = get_time_offset(timezone)
formatted_date = today_date.strftime('%Y-%m-%d')


def get_busy_hours():
    try:
        today = datetime.date.today()
        start_time = datetime.datetime(
            today.year, today.month, today.day, 10, 0, tzinfo=datetime.timezone(timedelta(hours=get_hours_delta(timezone))))
        end_time = datetime.datetime(today.year, today.month, today.day,
                                     20, 0, tzinfo=datetime.timezone(timedelta(hours=get_hours_delta(timezone))))

        # Формирование запроса на получение информации о занятости
        freebusy_query = {
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "items": [{"id": "bokoter@gmail.com"}]
        }

        # Отправка запроса
        freebusy_result = service.freebusy().query(  # type: ignore
            body=freebusy_query).execute()
        print(freebusy_result)
        # event_result = service.events().list(  # type: ignore
        #     calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
        # print(event_result.get('items'), [])
    except Exception as e:
        print(str(e))


def set_google_meeting(start_time, end_time, event_name, participant_email: str):
    try:
        service = get_service()
        event = {
            'summary': event_name,
            'location': 'somewhere_online',
            'description': 'meeting',
            'colorId': 6,
            'start': {
                # formatted_date+f'T{start_hour}:00:00'+time_offset,
                'dateTime': start_time,
                'timeZone': timezone
            },
            'end': {
                # formatted_date+f'T{end_hour}:00:00'+time_offset,
                'dateTime': end_time,
                'timeZone': timezone
            },
            'attendees': [
                {'email': participant_email}
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': 'some-random-string',
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        event = service.events().insert(calendarId=CALENDAR_ID,  # type: ignore
                                        body=event, sendNotifications=True, conferenceDataVersion=1).execute()
        return event.get('hangoutLink', '')
    except Exception as e:
        print(str(e))


# if __name__ == "__main__":
#     set_google_meeting('2024-04-08T20:00:00+03:00',
#                        '2024-04-08T21:00:00+03:00', 'test_meeting', email_list.get('ru', ''))
