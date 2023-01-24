import datetime
from datetime import timedelta

from aiogram import types


from configuration.settings import get
from configuration.session import Session
from configuration.buttons import market_keyboard
from configuration.urls import *
from users.models import User, client_auth


date = datetime.datetime.now().date()
yesterday_date = date - timedelta(days=1)

session = Session()


def get_data(payload, url, endpoint):
    response = get(url=url, endpoint=endpoint, payload=payload).json()
    return response


async def delete_old_keyboard(object):
    await object.answer(text=object.text, reply_markup=types.ReplyKeyboardRemove())


async def market_entry(message: types.Message):
    await delete_old_keyboard(message)
    user = User(message)
    session.connect_client(user)
    response = client_auth(user=user.auth_data())
    if response is True:
        keyboard = market_keyboard.return_keyboard()
        await message.answer(text='Выберите из списка', reply_markup=keyboard)
    else:
        await message.answer(text=response)


async def show_manufacturers(message: types.Message):
    user = session.get_client(message)
    response = get_data(url=URL, endpoint=MANUFACTURERS_ENDPOINT, payload=user.auth_data())
    for manufacturer in response:
        if manufacturer['name'] not in session.manufacturers_name:
            session.manufacturers_name.append(manufacturer['name'])
    user.create_manufacturer_keyboard(session.manufacturers_name)
    session.update(user)
    await message.answer(text='Все производители', reply_markup=user.manufacturer_keyboard)


async def show_products_by_manufacturer(message: types.Message):
    user = session.get_client(message)
    manufacturer_name = message.text
    data = {'manufacturer': manufacturer_name}
    data.update(user.auth_data())
    response = get_data(url=URL, endpoint=PRODUCT_BY_MANUFACTURER_ENDPOINT, payload=data)
    for product in response:
        if product['name'] not in session.products_names:
            session.products_names.append(product['name'])
    user.create_product_keyboard(products_names=session.products_names)
    session.update(user)
    await message.answer(text=f'Продукты от производителя: {manufacturer_name}')

