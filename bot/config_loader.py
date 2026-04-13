from dataclasses import dataclass
from os import getenv


@dataclass
class Bot:
    token: str


@dataclass
class DB:
    host: str
    db_name: str
    user: str
    password: str


@dataclass
class Config:
    bot: Bot
    db: DB
    admin_telegram_user_id: int


def load_config():
    admin_raw = getenv("ADMIN_TELEGRAM_USER_ID") or getenv("ADMIN_USER_ID")
    if not admin_raw:
        raise ValueError("ADMIN_TELEGRAM_USER_ID must be set in .env")

    return Config(
        bot=Bot(token=getenv("BOT_TOKEN")),
        db=DB(
            host=getenv("DB_HOST"),
            db_name=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASS"),
        ),
        admin_telegram_user_id=int(admin_raw),
    )
