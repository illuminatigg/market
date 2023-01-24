from aiogram.types import Message


def get_user(object) -> dict:
    user = {
        'telegram_id': object.from_user.id,
        'telegram_username': object.from_user.username,
        'telegram_phone_number': 'false'
    }
    return user


def payload(data: dict):
    payload_data = {}
    payload_data.update(data)
    return payload_data
