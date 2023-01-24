from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Message

from configuration.settings import get
from configuration.urls import URL, CLIENT_AUTH_ENDPOINT


# from market.models import Cart


class User:
    telegram_id: int
    telegram_username: str
    manufacturer_keyboard: ReplyKeyboardMarkup
    product_keyboard: ReplyKeyboardMarkup
    modification_keyboard: ReplyKeyboardMarkup

    def __init__(self, message: Message):
        self.telegram_id = message.from_user.id
        self.telegram_username = message.from_user.username

    def create_manufacturer_keyboard(self, manufacturers_names: list[str]):
        self.manufacturer_keyboard = ReplyKeyboardMarkup()
        for name in manufacturers_names:
            self.manufacturer_keyboard.add(KeyboardButton(name))

    def create_product_keyboard(self, products_names: list[str]):
        self.product_keyboard = ReplyKeyboardMarkup()
        self.product_keyboard.add(KeyboardButton('Назад к производителям'))
        for name in products_names:
            self.product_keyboard.add(KeyboardButton(name))

    def create_modification_keyboard(self, modifications_names: list[str]):
        self.modification_keyboard = ReplyKeyboardMarkup()
        self.modification_keyboard.add(KeyboardButton('Назад к продукту'))
        for name in modifications_names:
            self.modification_keyboard.add(KeyboardButton(name))

    def auth_data(self) -> dict:
        data = {'telegram_id': self.telegram_id}
        return data


def client_auth(user):
    response = get(url=URL, endpoint=CLIENT_AUTH_ENDPOINT, payload=user).json()
    if response['message'] == 'ok':
        return True
    else:
        return response['message']