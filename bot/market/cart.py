from aiogram import types

from configuration.settings import post, put
from configuration.urls import URL, CREATE_CART, UPDATE_CART
from configuration.payloads import get_user


class User:
    telegram_id: int
    telegram_username: str

    def __init__(self, message: types.Message):
        self.telegram_id = message.from_user.id
        self.telegram_username = message.from_user.username




class Manufacturers:
    all: dict = {}

    def add(self, manufacturers: dict):
        for manufacturer in manufacturers:
            self.all.update(
                {
                    manufacturer['name']: Manufacturer(
                        id=manufacturer['id'],
                        name=manufacturer['name']
                    )
                }
            )

    def show_all(self):
        return self.all.keys()


class Manufacturer:

    def __init__(self, id: int, name: str):
        self.id: int = id
        self.name: str = name

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name


class ProductModification:

    def __init__(self, id: int, specifications: str, price: float, quantity: int):
        self.id: int = id
        self.specifications: str = specifications
        self.price: float = price
        self.quantity: int = quantity


class Product:
    modifications: dict = {}
    modifications_names: list[str] = []

    def __init__(self, product_id: int = None, product_name: str = None, quantity: int = None, price: float = None):
        self.id: int = product_id
        self.name: str = product_name
        self.quantity: int = quantity

    def add_modification(self, id: int, product_modification: ProductModification) -> None:
        self.modifications.update({id: product_modification})

    def show_modifications_name(self) -> list[str]:
        for modification in self.modifications:
            self.modifications_names.append(modification.specifications)
        return self.modifications_names


class Products:
    all: dict = {}

    def add(self, name, product: Product):
        self.all.update({name: product})

    def show_all(self):
        return self.all.keys()


class Cart:
    cart_id: int
    products: list[ProductModification]
    total: float

    def __init__(self, owner: dict):
        self.owner: dict = owner

    def add_product(self, product: ProductModification):
        self.products.append(product)
        self.total += product.price

    def create(self) -> None:
        response = post(url=URL, endpoint=CREATE_CART, payload=self.owner).json()
        self.cart_id = response['id']

    def update(self):
        payload = {'cart_id': self.cart_id, 'proucts': []}
        for product in self.products:
            payload['proucts'].append(
                {
                    'id': product.id,
                    'name': product.name,
                    'quantity': product.quantity
                }
            )
        response = put(
            url=URL,
            endpoint=UPDATE_CART + f'{self.cart_id}/',
            payload=payload

        )
        return response

    def by_owner(self):
        return self.owner['telegram_id']
