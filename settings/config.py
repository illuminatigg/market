import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv


load_dotenv('.env')

API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)

