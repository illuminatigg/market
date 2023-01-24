import django
import datetime

from aiogram.types import Message

from accounts.models import CustomUser, RegistrationRequest
from market.models import Cart, Order, CartProduct, ProductModification, Product, Manufacturer


class MarketClient:
    id: int

    def __init__(self, message: Message):
        self.telegram_id: int = message.from_user.id
        self.telegram_username: str = message.from_user.username
        self.user: CustomUser

    def user_status(self):
        user = self.get_user()
        if user.client_small_wholesale:
            return 'sw'
        elif user.client_wholesale:
            return 'w'

    def get_user(self):
        user = CustomUser.objects.get(username=self.telegram_id)
        return user

    def auth(self):
        try:
            user = CustomUser.objects.filter(username=self.telegram_id, approved=True)
            return True
        except Exception as ex:
            print(ex)
            return False

    def get_or_create_cart(self):
        date_today = datetime.datetime.now().date()
        cart, created = Cart.objects.get_or_create(owner=self.telegram_id, created_at=date_today)
        if created:
            order = Order.objects.create(owner=self.telegram_id)
            cart.order = order
            cart.save()
            return cart
        return cart

    @staticmethod
    def get_product_modification(modification_name):
        product = ProductModification.objects.get(specifications=modification_name)
        return product

    def add_product_to_cart(self, product: ProductModification, price: str, quantity: int):
        try:
            user = self.get_user()
            cart = self.get_or_create_cart()
            modification = product
            modification.quantity -= quantity
            modification.product.quantity -= quantity
            modification.product.save()
            modification.save()
            if user.client_small_wholesale:
                cart_product = CartProduct.objects.create(cart=cart, product=product, price=price, quantity=quantity)
                cart.total += cart_product.price
                cart.save()
            elif user.client_wholesale:
                cart_product = CartProduct.objects.create(cart=cart, product=product, price=price, quantity=quantity)
                cart.total += cart_product.price
                cart.save()
            return f'Товар {product.specifications} добавлен в корзину'
        except Exception as ex:
            return f'Товар не был добавлен причниа: {ex}'

    def get_product_price(self, modification_name):
        product = self.get_product_modification(modification_name)
        user = self.get_user()
        if user.client_small_wholesale:
            return product.price_dollar
        elif user.client_wholesale:
            return product.price_rub

    def show_cart(self):
        cart = self.get_or_create_cart()
        return cart.products.all()

    def show_order(self):
        cart = self.get_or_create_cart()
        return cart.order

    def validation(self, func):
        if self.auth():
            func()
        return 'Ваш аккаунт не зарегистрирован или заблокирован'

    def create_registration_request(self):
        try:
            request, created = RegistrationRequest.objects.get_or_create(
                telegram_id=self.telegram_id,
                telegram_username=self.telegram_username,
            )
            if created:
                user = CustomUser.objects.create_user(
                    username=str(self.telegram_id),
                    password=str(self.telegram_id) + self.telegram_username
                )
                return True
            return False
        except Exception as ex:
            print(ex)
            return False


class Market:

    @staticmethod
    def get_price(user: MarketClient):
        client = user.get_user()
        if client.client_wholesale:
            products = ProductModification.objects.filter(
                available_for_wholesale=True
            ).prefetch_related(
                'wholesale_prices'
            )
            return products
        elif client.client_small_wholesale:
            products = ProductModification.objects.filter(
                available_for_small_wholesale=True
            ).prefetch_related(
                'small_wholesale_prices'
            )
            return products

    @staticmethod
    def get_manufacturers_names():
        manufacturers_names = Manufacturer.objects.all().values_list('name')
        result = [name[0] for name in manufacturers_names]
        return result

    @staticmethod
    def get_products_names():
        products_names = Product.objects.all().values_list('name')
        return set([name[0] for name in products_names])

    @staticmethod
    def get_modifications_names():
        modifications_names = ProductModification.objects.all().values_list('specifications')
        return set([name[0] for name in modifications_names])

    @staticmethod
    def get_manufacturers():
        manufacturers = Manufacturer.objects.all()
        return manufacturers

    @staticmethod
    def get_products_by_manufacturer(manufacturer_name):
        products = Product.objects.filter(manufacturer__name=manufacturer_name, available=True).values_list('name')
        return set([name[0] for name in products])

    @staticmethod
    def get_modifications_by_product(product_name, message: Message):
        user = MarketClient(message)
        client = user.get_user()
        if client.client_small_wholesale:
            modifications = ProductModification.objects.filter(
                product__name=product_name,
                available=True,
                available_for_small_wholesale=True
            )
            return modifications

        elif client.client_wholesale:
            modifications = ProductModification.objects.filter(
                product__name=product_name,
                available=True,
                available_for_wholesale=True
            )
            return modifications

    @staticmethod
    def get_modifications_sw_by_product(product_name):
        modifications = ProductModification.objects.filter(
            product__name=product_name,
            available=True,
            available_for_small_wholesale=True
        ).values_list('specifications')
        result = [name[0] for name in modifications]
        return result

    @staticmethod
    def get_products_by_modification(modification_name):
        modifications = Product.objects.filter(modifications__specifications=modification_name).values_list('name')
        return set([name[0] for name in modifications])


def get_manufacturers_names():
    manufacturers_names = Manufacturer.objects.all().values_list('name')
    result = [name[0] for name in manufacturers_names]
    result.insert(0, '1️⃣ Назад')
    return result


def get_products_names():
    products_names = Product.objects.all().values_list('name')
    result = [name[0] for name in products_names]
    result.insert(0, '1️⃣ Назад')
    return result


def get_modifications_names():
    modifications_names = ProductModification.objects.all().values_list('specifications')
    list(modifications_names).insert(0, '2️⃣ Назад')
    return set([name[0] for name in modifications_names])


def get_products_by_manufacturer(manufacturer_name):
    products = Product.objects.filter(manufacturer__name=manufacturer_name, available=True).values_list('name')
    result = [name[0] for name in products]
    result.insert(0, '1️⃣ Назад')
    return result


def get_modifications_sw_by_product(product_name):
    modifications = ProductModification.objects.filter(
        product__name=product_name, available_for_small_wholesale=True
    ).values_list('specifications')
    result = [name[0] for name in modifications]
    return result


def get_product_by_name(name):
    products_names = Product.objects.get().values_list('name')
    result = [name[0] for name in products_names]
    result.insert(0, '1️⃣ Назад')
    return result
