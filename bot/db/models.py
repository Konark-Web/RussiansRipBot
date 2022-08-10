from sqlalchemy import Column, BigInteger, Boolean

from bot.db.base import Base


class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    status = Column(Boolean, default=True)
    schedule_status = Column(Boolean, default=True)


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    schedule_status = Column(Boolean, default=False)
