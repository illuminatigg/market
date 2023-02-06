from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class MarketState(StatesGroup):
    market_entry = State()
    waiting_select_manufacturer = State()
    waiting_select_product = State()
    waiting_select_modification = State()
    waiting_select_quantity = State()
    show_price = State()


class RetailSaleState(StatesGroup):
    """
    1. Выбор производителя
    2. Выбор продукта
    3. Выбор модификации
    4. Ожидание ввода колличества
    """
    waiting_manufacturer_name = State()
    waiting_product_name = State()
    waiting_modification_name = State()
    price = State()
    waiting_quantity = State()


class WholeSaleState(StatesGroup):
    """
    1. Выбор производителя
    2. Выбор продукта
    3. Выбор модификации
    4. Ожидание ввода колличества
    """
    waiting_manufacturer_name = State()
    waiting_product_name = State()
    waiting_modification_name = State()
    price = State()
    waiting_quantity = State()

"""

"""