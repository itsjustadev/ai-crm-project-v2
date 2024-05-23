from datetime import datetime, timedelta
from sys import exc_info
from sqlalchemy import create_engine, Column, String, Text, Integer, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import DateTime
import os
from dotenv import load_dotenv
from databases.db_tables import *

load_dotenv()
username = str(os.getenv('USERNAME'))
password = str(os.getenv('PASSWORD'))
host = str(os.getenv('HOST'))
port = str(os.getenv('PORT'))
database = str(os.getenv('DATABASE'))
connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def add_in_first_history(client_id: str, client_name: str, client_message: str, ml_message: str, client_info: str) -> bool:
    session = Session()
    try:
        new_addition = FirstHistory(
            client_id=client_id, client_name=client_name, client_message=client_message, ml_message=ml_message,  client_info=client_info)
        session.merge(new_addition)
        session.commit()
        return True
    except Exception as e:
        print(
            'Ошибка в функции add_in_first_history, записать данные не удалось /n' + str(e))
        return False
    finally:
        session.close()


def get_first_history(client_id):
    session = Session()
    try:
        # Извлекаем все записи для данного client_id
        results = session.query(FirstHistory).filter(
            FirstHistory.client_id == client_id).all()
        history_dict = {}
        if results:
            history_dict['client_id'] = client_id
            for result in results:
                if result.client_message:  # Проверяем, что поля не пустые
                    history_dict['incoming'] = result.client_message
                if result.ml_message:
                    history_dict['outgoing'] = result.ml_message
                session.delete(result)
            session.commit()
        return history_dict
    except Exception as e:
        print(
            'Ошибка в функции get_first_history /n' + str(e))
        return None
    finally:
        session.close()


def get_special_user_id(user_id):
    session = Session()
    try:
        user = session.query(UsersWithClear).get(user_id)
        return user.new_user_id if user else None
    except Exception as e:
        print(
            'Ошибка в функции get_special_user_id /n' + str(e))
        return None
    finally:
        session.close()


def check_user_already_exists(user_id):
    session = Session()
    try:
        user = session.query(UsersBackend).get(user_id)
        return True if user else False
    except Exception as e:
        print(
            'Ошибка в функции check_user_already_exists /n' + str(e))
        return False
    finally:
        session.close()


def add_new_user(user_id):
    session = Session()
    try:
        new_user = UsersBackend(user_id=user_id)
        session.merge(new_user)
        session.commit()
    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(
            'Ошибка в функции add_new_user /n' + str(e))
    finally:
        session.close()

def add_special_user_id(user_id, new_user_id):
    session = Session()
    try:
        new_user = UsersWithClear(user_id=user_id, new_user_id=new_user_id)
        session.merge(new_user)
        session.commit()
    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(
            'Ошибка в функции add_special_user_id /n' + str(e))
    finally:
        session.close()

def add_conversation_id(user_id, conversation_id):
    session = Session()
    try:
        new_user = UsersConversationLead(
            user_id=user_id, conversation_id=conversation_id)
        session.merge(new_user)
        session.commit()
    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(
            'Ошибка в функции add_conversation_id /n' + str(e))
    finally:
        session.close()


def add_lead_id(user_id, lead_id):
    session = Session()
    try:
        user = session.query(UsersConversationLead).get(user_id)
        if user:
            user.lead_id = lead_id
            session.commit()
        else:
            print("User not found to add lead_id")
    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(
            'Ошибка в функции add_lead_id /n' + str(e))
    finally:
        session.close()


def get_lead_id_by_user(user_id):
    session = Session()
    try:
        user = session.query(UsersConversationLead).get(user_id)
        if user:
            return user.lead_id
        else:
            print("User not found to get lead_id_by_user")
    except Exception as e:
        print(
            'Ошибка в функции get_lead_id_by_user /n' + str(e))
    finally:
        session.close()


def get_user_id_by_conversation(conversation_id):
    session = Session()
    try:
        user = session.query(UsersConversationLead).filter(
            UsersConversationLead.conversation_id == conversation_id).first()
        return user.user_id if user else None
    except Exception as e:
        print(
            'Ошибка в функции get_user_id_by_conversation /n' + str(e))
        return None
    finally:
        session.close()

def add_new_set_name(user_id):
    session = Session()
    try:
        new_user = WasSetName(user_id=user_id)
        session.merge(new_user)
        session.commit()
    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(
            'Ошибка в функции add_new_set_name/n' + str(e))
    finally:
        session.close()


def was_set_name(user_id):
    session = Session()
    try:
        user = session.query(WasSetName).get(user_id)
        return True if user else False
    except Exception as e:
        print(
            'Ошибка в функции was_set_name /n' + str(e))
        return False
    finally:
        session.close()

def delete_command_set_name(user_id):
    session = Session()
    try:
        user = session.query(WasSetName).get(user_id)
        if user:
            session.delete(user)
            session.commit()
            return True
    except Exception as e:
        print(
            'Ошибка в функции delete_command_set_name /n' + str(e))
        return False
    finally:
        session.close()

# def check_user_has_clear_command(user_id):
#     session = Session()
#     try:
#         existing_user = session.query(
#             UsersWithClear).get(user_id)
#         return existing_user is not None
#     except Exception as e:
#         print(
#             'Ошибка в функции check_user_has_clear_command /n' + str(e))
#         return None
#     finally:
#         session.close()

