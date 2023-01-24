import logging
import json

from aiogram import types

from configuration.settings import get, post
from configuration.urls import URL, REGISTRATION_ENDPOINT
from configuration.payloads import get_user

logging.basicConfig(filename='logs.txt', level=logging.DEBUG)


async def registration(message: types.Message):
    user = get_user(message)
    request = post(URL, REGISTRATION_ENDPOINT, payload=user)
    response = json.loads(request.text)
    result = response.get('response_message')
    await message.answer(text=result)
