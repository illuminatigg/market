from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, BotCommand
from aiogram import Dispatcher
from config.settings import DISPATCHER


async def set_main_menu(dispatcher: Dispatcher):
    commands: list[BotCommand] = [
        BotCommand(command='market', description='Маркет'),
        BotCommand(command='personal_area', description='Личный кабинет'),
    ]
    await dispatcher.bot.set_my_commands(commands)


class MarketKeyboard:
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)

    def set_buttons(self, buttons_names: list[str]) -> None:
        for button in buttons_names:
            self.keyboard.add(KeyboardButton(text=button))

    def return_keyboard(self):
        return self.keyboard


class ManufacturerKeyboard(MarketKeyboard):
    pass


class ProductKeyboard(MarketKeyboard):
    pass


class ModificationKeyboard(MarketKeyboard):
    pass

