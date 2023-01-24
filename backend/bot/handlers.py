import django
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
# ______________________________________________________________________________________________________________________
import logging

from aiogram.dispatcher.filters import Command, Text
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config.settings import DISPATCHER
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext

from bot.service import MarketClient, Market, get_manufacturers_names, get_products_names, get_modifications_names, \
    get_products_by_manufacturer, get_modifications_sw_by_product
from bot.keyboard import ManufacturerKeyboard, ProductKeyboard, set_main_menu
from bot.states import RetailSaleState
import aiogram.utils.markdown as fmt

logging.basicConfig(level=logging.INFO)

manufacturers = get_manufacturers_names()
products = get_products_names()
modifications = get_modifications_names()
market_requests = Market()
retail_sale = RetailSaleState()


async def delete_old_keyboard(object):
    await object.answer(text=object.text, reply_markup=ReplyKeyboardRemove())


def user_is_client(func):
    async def wrapper(message: Message, *args, **kwargs):
        user = MarketClient(message)
        if user.auth():
            await func(message)
        else:
            await message.answer(text='Регистрация не пройдена или не подтверждена, обратитесь к оператору')
    return wrapper


@DISPATCHER.message_handler(text=['Запрос на регистрацию'])
async def registration_request(message: Message):
    user = MarketClient(message)
    if user.create_registration_request():
        await message.answer(text='Запрос на регистрацию отправлен')
    else:
        await message.answer(text='Ваш запрос в обработке')


@DISPATCHER.message_handler(Command(['market']), state='*')
@user_is_client
async def market(message: Message, state: FSMContext=None):
    if state:
        await state.reset_state(with_data=True)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text='Розничная продажа'))
    keyboard.add(KeyboardButton(text='Оптовая продажа'))
    await message.answer(text='™️', reply_markup=keyboard)


@DISPATCHER.message_handler(text=['Розничная продажа', '0️⃣ Назад'], state='*')
# @user_is_client
async def retail_sale_entry(message: Message, state: FSMContext):
    if message.text == '0️⃣ Назад':
        await state.reset_state(with_data=True)
    manufacturers_names = market_requests.get_manufacturers_names()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in manufacturers_names:
        keyboard.add(KeyboardButton(text=name))
    await message.answer(text='Список производителей 📄', reply_markup=keyboard)
    await state.set_state(retail_sale.waiting_manufacturer_name.state)


@DISPATCHER.message_handler(text=manufacturers, state=[retail_sale.waiting_manufacturer_name.state, retail_sale.waiting_modification_name])
async def show_products_for_retail(message: Message, state: FSMContext):
    if message.text == '1️⃣ Назад':
        data = await state.get_data()
        products = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='0️⃣ Назад'))
        for product in products:
            keyboard.add(KeyboardButton(text=product))
        await message.answer(text='Список товара', reply_markup=keyboard)
        await state.set_state(retail_sale.waiting_product_name)

    else:
        async with state.proxy() as data:
            data['manufacturer_name'] = message.text
        products = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='0️⃣ Назад'))
        for product in products:
            keyboard.add(KeyboardButton(text=product))
        await message.answer(text='Список товара', reply_markup=keyboard)
        await state.set_state(retail_sale.waiting_product_name)


@DISPATCHER.message_handler(text=products, state=retail_sale.waiting_product_name)
async def show_modifications_by_product(message: Message, state: FSMContext):
    user = MarketClient(message)
    async with state.proxy() as data:
        data['product_name'] = message.text
    modifications = market_requests.get_modifications_by_product(data['product_name'], message)
    modifications_names = [modification.specifications for modification in modifications]
    if user.user_status() == 'sw':
        price = [modification.specifications + ' - ' + str(modification.price_dollar) + ' usd' for modification in modifications]
    else:
        price = [modification.specifications + ' - ' + str(modification.price_rub) + ' rur' for modification in modifications]
    async with state.proxy() as data:
        data['price'] = price
        print(data['price'])
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(KeyboardButton(text='1️⃣ Назад'))
    keyboard.add(KeyboardButton(text='📄 Прайс'))
    for modification in modifications_names:
        keyboard.add(KeyboardButton(text=modification))
    await message.answer(text='Список модификаций', reply_markup=keyboard)
    await state.set_state(retail_sale.waiting_modification_name)


@DISPATCHER.message_handler(text=modifications, state=[retail_sale.waiting_modification_name])
async def retail_modification_quantity(message: Message, state: FSMContext):
    client = MarketClient(message)
    cart = client.get_or_create_cart()
    print(cart.id)
    async with state.proxy() as data:
        data['modification_name'] = message.text
        data['cart_id'] = cart.id
    await message.answer(f'Введите колличество чтобы добавить товар {message.text} в корзину', reply_markup=ReplyKeyboardRemove())
    await state.set_state(retail_sale.waiting_quantity)


@DISPATCHER.message_handler(lambda message: message.text.isdigit(), state=[retail_sale.waiting_quantity])
async def retail_quantity(message: Message, state: FSMContext):
    client = MarketClient(message)
    data = await state.get_data()
    product = client.get_product_modification(data['modification_name'])
    price = client.get_product_price(data['modification_name'])
    client.add_product_to_cart(product, price, quantity=int(message.text))
    await message.answer(text=f'Вы заказали {message.text}  штук {data["modification_name"]}', reply_markup=ReplyKeyboardRemove())


@DISPATCHER.message_handler(text='📄 Прайс', state=retail_sale.waiting_modification_name)
async def retail_price(message: Message, state: FSMContext):
    data = await state.get_data()
    price = fmt.text(*data['price'])
    await message.answer(price)
    await state.set_state()


@DISPATCHER.message_handler(text='Корзина', state='*')
async def show_cart(message: Message):
    user = MarketClient(message)
    cart = user.show_cart()
    products = fmt.text(*[product.product.specifications for product in cart])
    await message.answer(products)



# @DISPATCHER.message_handler(text=manufacturers, state='*')
# async def product_by_manufacturer(message: Message, state: FSMContext):
#     await state.set_state(MarketState.waiting_select_product.state)
#     async with state.proxy() as data:
#         data['select_manufacturer'] = message.text
#     products_names = get_products_by_manufacturer(message.text)
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(KeyboardButton(text='0️⃣ Назад'))
#     for name in products_names:
#         keyboard.add(KeyboardButton(text=name))
#     await message.answer(text='Список продуктов', reply_markup=keyboard)
#
#
# @DISPATCHER.message_handler(text=products, state='*')
# async def modifications_by_product(message: Message, state: FSMContext):
#     await state.update_data(product=str(message.text))
#     modifications_names = get_modifications_by_product(message.text)
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add()
#     keyboard.add(KeyboardButton(text='0️⃣ Назад'))
#     keyboard.add(KeyboardButton(text='🗒 Прайс'))
#     for name in modifications_names:
#         keyboard.add(KeyboardButton(text=name))
#     await message.answer(text='Список модификаций', reply_markup=keyboard)
#
#
# @DISPATCHER.message_handler(text='🗒 Прайс', state='*')
# async def show_price(message: Message, state: FSMContext):
#     data = await state.get_data()


# @DISPATCHER.message_handler(text=manufacturers)
# async def manufacturers
# async def client_registration(message: Message):
#     await delete_old_keyboard(message)
#     user = MarketClient(message)
#     if user.create_registration_request():
#         await message.answer(text='Запрос создан, в ближайшее время вам откроют доступ')
#     elif user.auth():
#         await message.answer(text='Вы уже зарегистрированны')
#     else:
#         await message.answer(text='Запрос все еще в обработке')
#
#
# async def market_entry(message: Message):
#     user = MarketClient(message)
#     if user.auth():
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#         buttons = ['Производители', 'Товары', 'Корзина']
#         for button in buttons:
#             keyboard.add(KeyboardButton(text=button))
#         await message.answer(text='Выберите из списка', reply_markup=keyboard)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# async def show_manufacturers(message: Message):
#     global manufacturers
#     manufacturers = market.get_manufacturers_names()
#     user = MarketClient(message)
#     if user.auth():
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#         for name in manufacturers:
#             keyboard.add(KeyboardButton(text=name))
#         await message.answer(text='Список производителей', reply_markup=keyboard)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# async def show_products_by_manufacturer(message: Message):
#     await delete_old_keyboard(message)
#     global products
#     products = market.get_products_names()
#     user = MarketClient(message)
#     if user.auth():
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(KeyboardButton(text='Назад к производителям'))
#         products_by_manufacturer = market.get_products_by_manufacturer(message.text)
#         for name in products_by_manufacturer:
#             keyboard.add(KeyboardButton(text=name))
#         await message.answer(text=f'Все продукты от производителя: {message.text}', reply_markup=keyboard)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# async def show_product_modifications(message: Message):
#     await delete_old_keyboard(message)
#     global modifications
#     modifications = market.get_modifications_names()
#     user = MarketClient(message)
#     if user.auth():
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(KeyboardButton(text='Назад к товарам'))
#         modifications = market.get_modifications_by_product(message.text)
#         for modification in modifications:
#             keyboard.add(KeyboardButton(text=modification))
#         await message.answer(text=f'Все продукты: {message.text}', reply_markup=keyboard)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# async def get_back(message: Message):
#     if message.text == 'Назад к товарам':
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(KeyboardButton(text='Назад к товарам'))
#         products_by_modification = market.get_products_by_modification(message.text)
#         keyq = message.reply_markup
#         print(keyq)
#         print(products_by_modification)
#         for product in products_by_modification:
#             keyboard.add(KeyboardButton(text=product))
#         await message.answer(text='Производители', reply_markup=keyboard)
#
#
# async def test(message: Message):
#     user = MarketClient(message)
#     if user.auth():
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#
#         await message.answer(text='')
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')


# _____________________RUN________________________________________________________________
if __name__ == '__main__':
    executor.start_polling(DISPATCHER, skip_updates=True, on_startup=set_main_menu)
