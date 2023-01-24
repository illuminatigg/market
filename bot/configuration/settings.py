import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

import requests
from pydantic import BaseSettings, SecretStr
from aiogram import Bot, Dispatcher

load_dotenv('../../settings/.env')

DEBUG = True

logging.basicConfig(level=logging.INFO)


# storage: MemoryStorage = MemoryStorage()


# bot settings
# ______________________________________________________________________
class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


# config = Settings()

bot = Bot(token='5660333027:AAHfgCeu8gxixfpmIu-fBbgyVvwiCJzc0aE')

dispatcher = Dispatcher(bot)

# db settings
# ______________________________________________________________________
DATABASE = {
    'USER': ['postgres' if DEBUG else os.getenv('POSTGRES_NAME')],
    'PASSWORD': ['postgres' if DEBUG else os.getenv('POSTGRES_PASSWORD')],
    'HOST': ['localhost' if DEBUG else os.getenv('DATABASE_HOST')],
    'DB': ['market' if DEBUG else os.getenv('POSTGRES_NAME')]
}

engine = create_engine(
    f"postgresql+psycopg2://{DATABASE['USER']}:{DATABASE['PASSWORD']}@{DATABASE['HOST']}/{DATABASE['DB']}",
    echo=True,
    pool_size=6,
    max_overflow=10
)

