from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import os
import pytz
from datetime import timedelta
from testing_new.connection_to_google import CALENDAR_ID, get_service, timezone


SLOTS_START_HOUR = 10
SLOTS_END_HOUR = 23

def check_date_not_previous(date_string):
    try:
        date_string_clean = date_string.split('+')[0]
        date_incoming = datetime.datetime.strptime(
            date_string_clean, '%Y-%m-%dT%H:%M:%S').date()
        date_today = datetime.datetime.now().date()
        if date_incoming >= date_today:
            result = True
        else:
            result = False
        return result
    except Exception as e:
        print(str(e))
        result = False

def get_offset_timedelta(timezone):
    current_timezone = pytz.timezone(timezone)
    current_time = datetime.datetime.now(current_timezone)
    offset_timedelta = current_time.utcoffset()
    return offset_timedelta


def get_hours_delta(timezone):
    offset_hours = 0
    offset_timedelta = get_offset_timedelta(timezone)
    if offset_timedelta:
        offset_hours = offset_timedelta.seconds // 3600
    return offset_hours


def get_busy_times_with_participant(participant_email, hour_start=SLOTS_START_HOUR, hour_end=SLOTS_END_HOUR, timezone=timezone):
    try:
        service = get_service()
        now = datetime.datetime.utcnow()
        if now.hour >= 20:
            day = now.day + 1
        else:
            day = now.day
        hours_delta = get_hours_delta(timezone)
        today_start = datetime.datetime(
            now.year, now.month, day, hour_start - hours_delta).isoformat() + 'Z'
        print(today_start)
        today_end = datetime.datetime(
            now.year, now.month, day, hour_end - hours_delta).isoformat() + 'Z'
        print(today_end)

        events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=today_start, timeMax=today_end,  # type: ignore
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        busy_times = []
        for event in events:
            # Проверяем наличие участников в событии
            if 'attendees' in event:
                # Проверяем, есть ли среди участников нужный email
                for attendee in event['attendees']:
                    if attendee['email'] == participant_email:
                        start = event['start'].get(
                            'dateTime', event['start'].get('date'))
                        end = event['end'].get(
                            'dateTime', event['end'].get('date'))
                        busy_times.append({'start': start, 'end': end})
                        break  # Прерываем цикл, т.к. нужный участник найден
        return busy_times
    except Exception as e:
        print(str(e))


def parse_time(time_str):
    return datetime.datetime.fromisoformat(time_str)


def format_time(dt):
    iso_formatted = dt.strftime('%Y-%m-%dT%H:%M:%S')
    offset = dt.strftime('%z')
    formatted_offset = offset[:3] + ':' + \
        offset[3:]  # Добавляем ':' в часовой пояс
    return iso_formatted + formatted_offset


def round_start_time(dt):
    """Округляет время начала в большую сторону до следующего часа."""
    if dt.minute == 0 and dt.second == 0:
        return dt
    else:
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def round_end_time(dt):
    """Округляет время окончания в меньшую сторону, только если минуты и секунды не 00:00."""
    if dt.minute == 0 and dt.second == 0:
        return dt
    else:
        return dt.replace(minute=0, second=0, microsecond=0)


def round_time(dt):
    # Округляем минуты в соответствии с заданными условиями
    if dt.minute < 15:
        return dt.replace(minute=0, second=0, microsecond=0)
    elif 15 <= dt.minute < 45:
        return dt.replace(minute=30, second=0, microsecond=0)
    else:
        # Если минуты больше 45, добавляем час и обнуляем минуты
        return (dt + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)


def find_free_slots(events, start_hour=SLOTS_START_HOUR, end_hour=SLOTS_END_HOUR, timezone=timezone):
    free_slots = []
    if not events:
        # Создаем слот со стартом в 10 утра и концом в 19 вечера
        day_start = round_start_time(get_current_time_with_timezone(timezone).replace(
            hour=start_hour, minute=0, second=0, microsecond=0))
        day_end = round_end_time(get_current_time_with_timezone(timezone).replace(
            hour=end_hour, minute=0, second=0, microsecond=0))
        free_slots = [{'start': format_time(
            day_start), 'end': format_time(day_end)}]
    elif events:
        events = sorted(events, key=lambda x: parse_time(x['start']))
    # Определяем начало и конец дня на основе первого события
        day_start = parse_time(events[0]['start']).replace(
            hour=start_hour, minute=0, second=0, microsecond=0)
        day_end = parse_time(events[0]['start']).replace(
            hour=end_hour, minute=0, second=0, microsecond=0)

        free_slots = []
        last_end_time = day_start
        for event in events:
            event_start = parse_time(event['start'])
            event_end = parse_time(event['end'])

            if event_start > last_end_time:
                start_rounded = round_start_time(last_end_time)
                end_rounded = round_end_time(event_start)
                if start_rounded < end_rounded:  # Проверяем, чтобы начало слота было до его окончания после округления
                    free_slots.append({'start': format_time(
                        start_rounded), 'end': format_time(end_rounded)})

            last_end_time = max(last_end_time, event_end)

        if last_end_time < day_end:
            start_rounded = round_start_time(last_end_time)
            end_rounded = round_end_time(day_end)
    # Та же проверка для последнего слота дня
            if start_rounded < end_rounded and (end_rounded - start_rounded) >= timedelta(hours=1):
                free_slots.append({'start': format_time(
                    start_rounded), 'end': format_time(day_end)})
    return free_slots


def get_current_time_with_timezone(timezone):
    """Возвращает текущее время с учетом разницы часового пояса."""
    current_timezone = pytz.timezone(timezone)
    current_time = datetime.datetime.now(current_timezone)
    return current_time


def get_suitable_slots(free_slots, timezone=timezone):
    scheduled_slots = []
    current_time = get_current_time_with_timezone(timezone)
    for slot in free_slots:
        original_start = parse_time(slot['start'])
        original_end = parse_time(slot['end'])
# Если длительность промежутка ровно один час, добавляем его без изменений
        if original_end - original_start == timedelta(hours=1):
            scheduled_slots.append({'start': format_time(
                original_start), 'end': format_time(original_end)})
            continue  # Переходим к следующему промежутку
# Для остальных промежутков прибавляем 30 минут к начальному времени
        start = original_start + timedelta(minutes=30)
        end = original_end
        while start + timedelta(hours=1) <= end:
            scheduled_slot_start = start
            scheduled_slot_end = start + timedelta(hours=1)
# Добавляем выбранный слот в список
            if scheduled_slot_start >= current_time:
                scheduled_slots.append({'start': format_time(
                    scheduled_slot_start), 'end': format_time(scheduled_slot_end)})
# Пытаемся прибавить час для следующего слота
            start += timedelta(hours=1)
    return scheduled_slots[:3]


# Использование функции для получения событий с участием example@gmail.com
# participant_email = 'itsjustfortwits@gmail.com'
# busy_times = get_busy_times_with_participant(
#     participant_email, 'Europe/Moscow')
# if busy_times is None:
#     print('need authentication')
# else:
#     free_slots = find_free_slots(busy_times, 'Europe/Moscow')
#     print(free_slots)
#     print(get_suitable_slots(free_slots, 'Europe/Moscow'))
