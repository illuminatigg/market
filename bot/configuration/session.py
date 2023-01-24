import datetime
from aiogram.types import Message
from users.models import User


class Session:
    created_date: datetime.date
    clients: dict = {}
    manufacturers_name: list[str] = []
    products_names: list[str] = []
    modifications_names: list[str] = []

    def __init__(self):
        self.created_date = datetime.datetime.now().date()

    def connect_client(self, client: User):
        self.clients[client.telegram_id] = client

    def get_client(self, message: Message):
        return self.clients[message.from_user.id]

    def update(self, client: User):
        self.clients[client.telegram_id] = client


def create_session(session: Session):
    new_session = session
    return new_session
