import datetime
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
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.dispatcher import FSMContext

from bot.service import MarketClient, Market, get_manufacturers_names, get_products_names, get_modifications_names, \
    get_products_by_manufacturer, get_modifications_sw_by_product, get_manufacturers_names_wholesale, \
    get_products_names_wholesale, get_time
from bot.keyboard import ManufacturerKeyboard, ProductKeyboard, set_main_menu
from bot.states import RetailSaleState, WholeSaleState, MarketState
import aiogram.utils.markdown as fmt

logging.basicConfig(level=logging.INFO)

# manufacturers = get_manufacturers_names()
# manufacturers_wholesale = get_manufacturers_names_wholesale()
# products = get_products_names()
# products_wholesale = get_products_names_wholesale()
# modifications = get_modifications_names()
market_requests = Market()
retail_sale = RetailSaleState()
market_state = MarketState()


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


@DISPATCHER.message_handler(Command(['start']))
async def started(message: Message):
    start_message = Market.start_message(message)
    await message.answer(text=start_message)


@DISPATCHER.message_handler(Command(['market']), state='*')
async def market(message: Message, state: FSMContext = None):
    market_func = Market()
    user = MarketClient(message)
    if user.auth():
        if market_func.is_work_time(datetime.datetime.now().time()):
            if state:
                await state.reset_state(with_data=True)
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton(text='Производители'))
            keyboard.add(KeyboardButton(text='📑 Прайс'))
            await message.answer(text='Добро пожаловать.', reply_markup=keyboard)
        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(Command(['personal_area']), state='*')
async def personal_area(message: Message, state: FSMContext):
    if state:
        await state.finish()
    user = MarketClient(message)
    market_func = Market()
    if user.auth():
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Текущая корзина'))
        keyboard.add((KeyboardButton(text='Заказы')))
        keyboard.add((KeyboardButton(text='Помощь')))
        if not market_func.is_work_time(datetime.datetime.now().time()):
            keyboard.add(KeyboardButton(text='Скачать накладную'))
        await message.answer(text='Личный кабинет', reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(text=['Помощь'])
async def help_message(message: Message):
    text = Market.get_help()
    await message.answer(text=text)


@DISPATCHER.message_handler(text=['Скачать накладную'])
async def invoice(message: Message):
    user = MarketClient(message)
    is_authenticated = user.auth()
    if is_authenticated:
        file_path = user.create_invoice()
        await message.reply_document(open(file_path, 'rb'))
        os.remove(file_path)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(text=['Запрос на регистрацию'])
async def registration_request(message: Message):
    user = MarketClient(message)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add(KeyboardButton(text='Отправить контактные данные', request_contact=True))
    await message.answer(text='Для регистрации оставьте ваши контактные данные', reply_markup=keyboard)


@DISPATCHER.message_handler(content_types=ContentType.CONTACT)
async def registration(message: Message):
    user = MarketClient(message)
    if user.create_registration_request(message.contact.phone_number):
        await message.answer(text='Запрос на регистрацию отправлен')
    else:
        await message.answer(text='Ваш запрос в обработке')


@DISPATCHER.message_handler(text=['Производители', '0️⃣ Назад'], state='*')
async def market_entry(message: Message, state: FSMContext):
    user = MarketClient(message)
    is_authenticated = user.auth()
    market_func = Market()
    if is_authenticated:
        if market_func.is_work_time(datetime.datetime.now().time()):
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            manufacturers_names = market_requests.get_manufacturers_names()
            for name in manufacturers_names:
                keyboard.add(KeyboardButton(name))
            await message.answer('🇺🇸🇪🇺ВЫБЕРИТЕ ПРОИЗВОДИТЕЛЯ🇨🇳🇻🇳', reply_markup=keyboard)
            await state.set_state(market_state.waiting_select_manufacturer.state)

        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )

    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(state=[market_state.waiting_select_manufacturer.state])
@DISPATCHER.message_handler(Text(equals='1️⃣ Назад'), state=market_state.waiting_select_modification.state)
async def select_product(message: Message, state: FSMContext):
    user = MarketClient(message)
    is_authenticated = user.auth()
    market_func = Market()
    if is_authenticated:
        if market_func.is_work_time(datetime.datetime.now().time()):
            if message.text == '1️⃣ Назад':
                data = await state.get_data()
                products_names = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                keyboard.add(KeyboardButton('0️⃣ Назад'))
                for name in products_names:
                    keyboard.add(KeyboardButton(name))
                await message.answer(text='⌚️📱ВЫБЕРИТЕ ПРОДУКТ💻🖥', reply_markup=keyboard)
                await state.set_state(market_state.waiting_select_product.state)

            else:
                async with state.proxy() as data:
                    data['manufacturer_name'] = message.text
                products_names = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                keyboard.add(KeyboardButton('0️⃣ Назад'))
                for name in products_names:
                    keyboard.add(KeyboardButton(name))
                await message.answer(text='⌚️📱ВЫБЕРИТЕ ПРОДУКТ💻🖥', reply_markup=keyboard)
                await state.set_state(market_state.waiting_select_product.state)

        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )

    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(state=market_state.waiting_select_product)
@DISPATCHER.message_handler(Text(equals='2️⃣ Назад'), state=[market_state.waiting_select_modification.state,
                                                             market_state.waiting_select_quantity.state])
async def select_modification(message: Message, state: FSMContext):
    user = MarketClient(message)
    is_authenticated = user.auth()
    market_func = Market()
    if is_authenticated:
        if market_func.is_work_time(datetime.datetime.now().time()):
            if message.text == '2️⃣ Назад':
                data = await state.get_data()
                modifications = market_requests.get_modifications_by_product(data['product_name'], message)
                modifications_names = [modification.specifications for modification in modifications]
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                keyboard.add(KeyboardButton('1️⃣ Назад'))
                keyboard.add(KeyboardButton('📑 Прайс'))
                for name in modifications_names:
                    keyboard.add(KeyboardButton(name))
                await message.answer(text='🔸🔸🔶Выберите модификацию🔶🔸🔸', reply_markup=keyboard)
                await state.set_state(market_state.waiting_select_modification.state)

            else:
                async with state.proxy() as data:
                    print(message.text)
                    data['product_name'] = message.text
                modifications = market_requests.get_modifications_by_product(data['product_name'], message)
                modifications_names = [modification.specifications for modification in modifications]
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                keyboard.add(KeyboardButton('1️⃣ Назад'))
                keyboard.add(KeyboardButton('📑 Прайс'))
                for name in modifications_names:
                    keyboard.add(KeyboardButton(name))
                await message.answer(text='🔸🔸🔶Выберите модификацию🔶🔸🔸', reply_markup=keyboard)
                await state.set_state(market_state.waiting_select_modification.state)
        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(Text(equals=['📑 Прайс']), state=[market_state.waiting_select_modification.state,
                                                             market_state.waiting_select_quantity.state])
async def product_price(message: Message, state: FSMContext):
    user = MarketClient(message)
    is_authenticated = user.auth()
    market_func = Market()
    if is_authenticated:
        if market_func.is_work_time(datetime.datetime.now().time()):
            data = await state.get_data()
            product_name = data['product_name']
            price_list = user.get_all_modification_prices_by_product_name(product_name)
            price_list.insert(0, "                    <b>Прайс</b>                    ")
            price = fmt.text(*[fmt.text(line) for line in price_list], sep="\n")
            if len(price) > 4096:
                for line in range(0, len(price), 4096):
                    await message.answer(price[line:line + 4096], parse_mode="HTML")
            else:
                await message.answer(price, parse_mode="HTML")
            await state.set_state(market_state.waiting_select_modification.state)
        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(state=market_state.waiting_select_modification.state)
async def quantity_waiting(message: Message, state: FSMContext):
    user = MarketClient(message)
    is_authenticated = user.auth()
    market_func = Market()
    if is_authenticated:
        if market_func.is_work_time(datetime.datetime.now().time()):
            async with state.proxy() as data:
                print(message.text)
                data['modification_name'] = message.text
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            keyboard.add(KeyboardButton('2️⃣ Назад'))
            await message.answer('Введите колличество', reply_markup=keyboard)
            await state.set_state(market_state.waiting_select_quantity.state)
        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(state=market_state.waiting_select_quantity.state)
async def add_product_to_cart(message: Message, state: FSMContext):
    user = MarketClient(message)
    is_authenticated = user.auth()
    market_func = Market()
    if is_authenticated:
        if market_func.is_work_time(datetime.datetime.now().time()):
            data = await state.get_data()
            quantity = int(message.text)
            modification = user.get_product_modification(data['modification_name'])
            modification_price = user.get_product_price(data['modification_name'], quantity)
            result = modification_price * quantity
            message_return = user.add_product_to_cart(modification, modification_price, quantity=message.text,
                                                      result=result)
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            keyboard.add(KeyboardButton('2️⃣ Назад'))
            await message.answer(text=message_return, reply_markup=keyboard)
            await state.set_state(market_state.waiting_select_modification.state)
        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


@DISPATCHER.message_handler(Text(equals=['📑 Прайс']))
async def price(message: Message, state: FSMContext):
    user = MarketClient(message)
    is_authenticated = user.auth()
    market_func = Market()
    if is_authenticated:
        if market_func.is_work_time(datetime.datetime.now().time()):
            price_list = user.get_all_modification_prices_by_product_name()
            price_list.insert(0, "                    <b>Прайс</b>                    ")
            price = fmt.text(*[fmt.text(line) for line in price_list], sep="\n\n")
            if len(price) > 4096:
                for line in range(0, len(price), 4096):
                    await message.answer(price[line:line + 4096], parse_mode="HTML")
            else:
                await message.answer(price, parse_mode="HTML")
        else:
            await message.answer(
                text=f'Магазин не доступен. Граффик работы с {market_func.show_schedule()[0]} до {market_func.show_schedule()[1]} МСК'
            )
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        keyboard.add(KeyboardButton(text='Запрос на регистрацию'))
        await message.answer(text='Для доступа к магазину запросите регистрацию аккаунта', reply_markup=keyboard)


# RETAIL________________________________________________________________________________________________________________
# @DISPATCHER.message_handler(text=['Производители', '0️⃣ Назад'], state='*')
# async def retail_sale_entry(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         if message.text == '0️⃣ Назад':
#             await state.reset_state(with_data=True)
#         manufacturers_names = market_requests.get_manufacturers_names()
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#         for name in manufacturers_names:
#             keyboard.add(KeyboardButton(text=name))
#         await message.answer(text='⌚️📱ВЫБЕРИТЕ ПРОИЗВОДИТЕЛЯ💻🖥', reply_markup=keyboard)
#         await state.set_state(retail_sale.waiting_manufacturer_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# @DISPATCHER.message_handler(text=manufacturers,
#                             state=[retail_sale.waiting_manufacturer_name.state, retail_sale.waiting_modification_name])
# async def show_products_for_retail(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         if message.text == '1️⃣ Назад':
#             data = await state.get_data()
#             products = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
#             keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#             keyboard.add(KeyboardButton(text='0️⃣ Назад'))
#             for product in products:
#                 keyboard.add(KeyboardButton(text=product))
#             await message.answer(text='Список товара', reply_markup=keyboard)
#             await state.set_state(retail_sale.waiting_product_name.state)
#
#         else:
#             async with state.proxy() as data:
#                 data['manufacturer_name'] = message.text
#             products = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
#             keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#             keyboard.add(KeyboardButton(text='0️⃣ Назад'))
#             for product in products:
#                 keyboard.add(KeyboardButton(text=product))
#             await message.answer(text='Список товара', reply_markup=keyboard)
#             await state.set_state(retail_sale.waiting_product_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# @DISPATCHER.message_handler(text=products, state=retail_sale.waiting_product_name)
# async def show_modifications_by_product(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         async with state.proxy() as data:
#             data['product_name'] = message.text
#         modifications = market_requests.get_modifications_by_product(data['product_name'], message)
#         modifications_names = [modification.specifications for modification in modifications]
#         if user.user_status() == 'sw':
#             price = [modification.specifications + ' - ' + str(modification.price_dollar) + ' usd' + ' остаток: ' + str(
#                 modification.quantity) for modification in
#                      modifications]
#         else:
#             price = [modification.specifications + ' - ' + str(modification.price_rub) + ' rur' + ' остаток: ' + str(
#                 modification.quantity) for modification in
#                      modifications]
#         async with state.proxy() as data:
#             data['price'] = price
#             print(data['price'])
#         if modifications_names:
#             keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#             keyboard.add(KeyboardButton(text='1️⃣ Назад'))
#             keyboard.add(KeyboardButton(text='📄 Прайс'))
#             for modification in modifications_names:
#                 keyboard.add(KeyboardButton(text=modification))
#             await message.answer(text='Список модификаций', reply_markup=keyboard)
#             await state.set_state(retail_sale.waiting_modification_name.state)
#         else:
#             keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#             keyboard.add(KeyboardButton(text='1️⃣ Назад'))
#             await message.answer(text='Нет доступных модификаций', reply_markup=keyboard)
#             await state.set_state(retail_sale.waiting_modification_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# @DISPATCHER.message_handler(text=modifications, state=[retail_sale.waiting_modification_name])
# async def retail_modification_quantity(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         cart = user.get_or_create_cart()
#         print(cart.id)
#         async with state.proxy() as data:
#             data['modification_name'] = message.text
#             data['cart_id'] = cart.id
#         await message.answer(f'Введите колличество чтобы добавить товар {message.text} в корзину',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.set_state(retail_sale.waiting_quantity.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#

#
# @DISPATCHER.message_handler(text='📄 Прайс', state=retail_sale.waiting_modification_name)
# async def retail_price(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         data = await state.get_data()
#         price = fmt.text(*[fmt.text(line) for line in data['price']], sep="\n")
#         await message.answer(price)
#         await state.set_state(retail_sale.waiting_modification_name)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# # ______________________________________________________________________________________________________________________
#
#
# # WHOLESALE_____________________________________________________________________________________________________________
# whole_sale_state = WholeSaleState()
#
#
# @DISPATCHER.message_handler(text=['Оптовая продажа', '2️⃣ Назад'], state='*')
# # @user_is_client
# async def whole_sale_entry(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         if message.text == '2️⃣ Назад':
#             await state.reset_state(with_data=True)
#         manufacturers_names = market_requests.get_manufacturers_names()
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#         for name in manufacturers_names:
#             keyboard.add(KeyboardButton(text=name))
#         await message.answer(text='Список производителей 📄 Опт', reply_markup=keyboard)
#         await state.set_state(whole_sale_state.waiting_manufacturer_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# @DISPATCHER.message_handler(text=manufacturers_wholesale,
#                             state=[
#                                 whole_sale_state.waiting_manufacturer_name.state,
#                                 whole_sale_state.waiting_modification_name.state
#                             ]
#                             )
# async def show_products_for_wholesale(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         if message.text == '3️⃣ Назад':
#             data = await state.get_data()
#             products = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
#             keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#             keyboard.add(KeyboardButton(text='2️⃣ Назад'))
#             for product in products:
#                 keyboard.add(KeyboardButton(text=product))
#             await message.answer(text='Список товара Опт', reply_markup=keyboard)
#             await state.set_state(whole_sale_state.waiting_product_name.state)
#
#         else:
#             async with state.proxy() as data:
#                 data['manufacturer_name'] = message.text
#             products = market_requests.get_products_by_manufacturer(data['manufacturer_name'])
#             keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#             keyboard.add(KeyboardButton(text='2️⃣ Назад'))
#             for product in products:
#                 keyboard.add(KeyboardButton(text=product))
#             await message.answer(text='Список товара Опт', reply_markup=keyboard)
#             await state.set_state(whole_sale_state.waiting_product_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# def wholesale_price_structure():
#     pass
#
#
# @DISPATCHER.message_handler(text=products_wholesale, state=whole_sale_state.waiting_product_name.state)
# async def show_modifications_by_product_wholesale(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         async with state.proxy() as data:
#             data['product_name'] = message.text
#         modifications = market_requests.get_modifications_wholesales_by_product(data['product_name'], message=message)
#         modifications_names = [modification.specifications for modification in modifications]
#         if user.user_status() == 'sw':
#             price = market_requests.wholesale_price_structure(modifications, 'usd', user.user_status())
#         else:
#             price = market_requests.wholesale_price_structure(modifications, 'rur', user.user_status())
#         async with state.proxy() as data:
#             data['price'] = price
#             print(data['price'])
#         keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#         keyboard.add(KeyboardButton(text='3️⃣ Назад'))
#         keyboard.add(KeyboardButton(text='📑 Прайс'))
#         for modification in modifications_names:
#             keyboard.add(KeyboardButton(text=modification))
#         await message.answer(text='Список модификаций опт', reply_markup=keyboard)
#         await state.set_state(whole_sale_state.waiting_modification_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# @DISPATCHER.message_handler(text=modifications, state=[whole_sale_state.waiting_modification_name.state])
# async def wholesale_modification_quantity(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         cart = user.get_or_create_cart()
#         print(cart.id)
#         async with state.proxy() as data:
#             data['modification_name'] = message.text
#             data['cart_id'] = cart.id
#         await message.answer(f'Введите колличество чтобы добавить товар {message.text} в корзину',
#                              reply_markup=ReplyKeyboardRemove())
#         await state.set_state(whole_sale_state.waiting_modification_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# @DISPATCHER.message_handler(lambda message: message.text.isdigit(),
#                             state=[whole_sale_state.waiting_modification_name.state])
# async def wholesale_quantity(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         data = await state.get_data()
#         product = user.get_product_modification(data['modification_name'])
#         price = user.get_product_wholesale_price(data['modification_name'], quantity=int(message.text))
#         if price:
#             message_return = user.add_product_to_cart(product, price, quantity=int(message.text), result=price)
#             await message.answer(text=message_return,
#                                  reply_markup=ReplyKeyboardRemove())
#         else:
#             await message.answer(text='Неверное колличество')
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#
#
# @DISPATCHER.message_handler(text='📑 Прайс', state=whole_sale_state.waiting_modification_name.state)
# async def wholesale_price(message: Message, state: FSMContext):
#     user = MarketClient(message)
#     is_authenticated = user.auth()
#     if is_authenticated:
#         data = await state.get_data()
#         price = fmt.text(*[fmt.text(line) for line in data['price']], sep="\n")
#         await message.answer(price)
#         await state.set_state(whole_sale_state.waiting_modification_name.state)
#     else:
#         await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')
#

# ______________________________________________________________________________________________________________________
@DISPATCHER.message_handler(text=['Корзина', 'Текущая корзина'], state='*')
async def show_cart(message: Message):
    user = MarketClient(message)
    is_authenticated = user.auth()
    if is_authenticated:
        cart_products = user.show_cart()
        products = fmt.text(*cart_products, sep="\n\n")
        if products == 'Сумма: 0.00':
            await message.answer(text='Корзина пуста')
        else:
            await message.answer(products, parse_mode="HTML")
    else:
        await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')


@DISPATCHER.message_handler(text=['Заказы'], state='*')
async def client_orders(message: Message):
    user = MarketClient(message)
    is_authenticated = user.auth()
    if is_authenticated:
        orders = []
        for order in user.get_orders():
            orders.append(
                f'<b>ЗАКАЗ:</b> {order.identifier}\n<b>СУММА:</b> {order.total}\n<b>СОЗДАН:</b> {order.created_at.strftime("%m/%d/%Y, %H:%M:%S")}\n<b>СТАТУС:</b> {order.status}\n\n')
        if len(orders) >= 1:
            orders = fmt.text(*[fmt.text(line) for line in orders], sep="\n")
            await message.answer(text=orders, parse_mode="HTML")
        else:
            await message.answer(text='Вы еще ничего не заказывали')
    else:
        await message.answer(text='Ваш доступ ограничен или вы еще не прошли регистрацию')


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

def run():
    executor.start_polling(DISPATCHER, skip_updates=True, on_startup=set_main_menu)

# run()
#
#
# if __name__ == '__main__':
#     executor.start_polling(DISPATCHER, skip_updates=True, on_startup=set_main_menu)
