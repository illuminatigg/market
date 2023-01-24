from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram import Dispatcher
from abc import ABC, abstractmethod

from configuration.settings import dispatcher, bot


class Menu:
    commands: list[BotCommand] = [
        BotCommand(command='/market', description='К покупкам'),
        BotCommand(command='/registration', description='Запрос на регистрацию'),
        BotCommand(command='/schedule', description='Рабочий график'),
        BotCommand(command='/help', description='Помощь')
    ]

    async def run(self, dispatcher: Dispatcher):
        await dispatcher.bot.set_my_commands(self.commands)


class Keyboard(ABC):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    @abstractmethod
    def return_keyboard(self) -> ReplyKeyboardMarkup:
        pass


class MarketKeyboard(Keyboard):
    manufacturers_button: KeyboardButton = KeyboardButton(text='Выбрать производителя')
    cart_button: KeyboardButton = KeyboardButton(text='Моя корзина')

    def __init__(self):
        self.keyboard.add(self.manufacturers_button).add(self.cart_button)

    def return_keyboard(self) -> ReplyKeyboardMarkup:
        return self.keyboard


menu = Menu()
market_keyboard = MarketKeyboard()


class ManufacturersKeyboard(Keyboard):

    def set_buttons(self, buttons: list[str]) -> None:
        for button in buttons:
            self.keyboard.add(KeyboardButton(text=button))

    def return_keyboard(self) -> ReplyKeyboardMarkup:
        return self.keyboard


manufacturer_keyboard = ManufacturersKeyboard()


def create_manufacturer_keyboard(buttons: list[str]):
    keyboard = ReplyKeyboardMarkup()
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    return keyboard


def create_products_keyboard(buttons: list[str] = None):
    keyboard = ReplyKeyboardMarkup()
    keyboard.add(KeyboardButton(text='Назад к производителям'))
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    return keyboard


def create_modifications_keyboard(buttons: list[str]):
    keyboard = ReplyKeyboardMarkup()
    keyboard.add(KeyboardButton(text='Назад к продукту'))
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    return keyboard