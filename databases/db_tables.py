from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer


Base = declarative_base()


class UsersBackend(Base):
    __tablename__ = 'users_backend'
    user_id = Column(String, primary_key=True)

class FirstHistory(Base):
    __tablename__ = 'first_history'
    id = Column(Integer, primary_key=True)
    client_id = Column(String)
    client_name = Column(String, default='')
    client_message = Column(String, default='')
    ml_message = Column(String, default='')
    client_info = Column(String, default='')


class UsersWithClear(Base):
    __tablename__ = 'users_with_clear'
    user_id = Column(String, primary_key=True)
    new_user_id = Column(String)


class UsersConversationLead(Base):
    __tablename__ = 'users_conversation_lead'
    user_id = Column(String, primary_key=True)
    conversation_id = Column(String, default='')
    lead_id = Column(String, default='')

class WasSetName(Base):
    __tablename__ = 'was_set_name'
    user_id = Column(String, primary_key=True)
