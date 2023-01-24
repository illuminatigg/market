from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class MarketState(StatesGroup):
    entry_state = State()
    manufacturers_state = State()
    products_state = State()
    modifications_state = State()
    add_modification_state = State()


market_state = MarketState()


