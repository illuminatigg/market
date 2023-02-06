import os
from unicodedata import decimal

import django
import datetime

from aiogram.types import Message
import pandas as pd

from accounts.models import CustomUser, RegistrationRequest, Profile
from config.settings import MEDIA_ROOT
from market.models import Cart, Order, CartProduct, ProductModification, Product, Manufacturer, Schedule, StartMessage, \
    HelpRules


def get_time():
    return datetime.datetime.now().time()


now = get_time()


class OrderStructure:
    def __init__(self, identifier, created_at, status, total):
        self.identifier = identifier
        self.status = status
        self.created_at = created_at
        self.total = total


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

    def get_orders(self):
        orders_list = []
        orders = Order.objects.filter(owner=self.telegram_id,
                                      opened_at__lt=datetime.datetime.now().date()).prefetch_related('cart')
        if orders:
            for order in orders:
                orders_list.append(OrderStructure(
                    identifier=order.identifier,
                    created_at=order.created_at,
                    status=order.get_status_display(),
                    total=order.cart.total,
                )
                )
            return orders_list
        return orders_list

    def auth(self):
        try:
            user = CustomUser.objects.filter(username=self.telegram_id, approved=True)
            if user:
                return True
            return False
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
        product = ProductModification.objects.filter(
            specifications=modification_name
        ).prefetch_related(
            'wholesale_prices',
            'small_wholesale_prices'
        )
        return product[0]

    def add_product_to_cart(self, product: ProductModification, price: str, quantity: str, result):
        user = self.get_user()
        try:
            if user.client_small_wholesale:
                cart = self.get_or_create_cart()
                modification = product
                if modification.quantity < int(quantity):
                    return f'Остаток товара меньше, чем запрашиваемое колличество. Остаток {modification.specifications} остаток: {modification.quantity}'
                else:
                    modification.quantity -= int(quantity)
                    modification.product.save()
                    if modification.quantity == 0:
                        modification.available = False
                        modification.save()
                    else:
                        modification.save()
                    cart_product = CartProduct.objects.create(cart=cart, product=product, price=price,
                                                              quantity=int(quantity))
                    cart.total += cart_product.price * int(quantity)
                    cart.save()
                    return f'Вы заказали {quantity}  {modification.specifications} на сумму {result}'
            elif user.client_wholesale:
                cart = self.get_or_create_cart()
                modification = product
                print(modification)
                if modification.quantity < int(quantity):
                    return f'Остаток товара меньше, чем запрашиваемое колличество. Остаток {modification.specifications} остаток: {modification.quantity}'
                else:
                    modification.quantity -= int(quantity)
                    modification.product.save()
                    if modification.quantity == 0:
                        modification.available = False
                        modification.save()
                    else:
                        modification.save()
                    cart_product = CartProduct.objects.create(cart=cart, product=product, price=price,
                                                              quantity=int(quantity))
                    cart.total += cart_product.price * int(quantity)
                    cart.save()
                    return f'Вы заказали {quantity}  {modification.specifications} на сумму {result}'
            return f'Товар {product.specifications} добавлен в корзину'
        except Exception as ex:
            return f'Товар не был добавлен причниа: {ex}'

    def get_product_price(self, modification_name, quantity):
        product = ProductModification.objects.filter(
            specifications=modification_name
        ).prefetch_related(
            'wholesale_prices',
            'small_wholesale_prices'
        )
        user = self.get_user()
        if user.client_small_wholesale:
            result: int = 0
            for modification in product:
                for price in modification.small_wholesale_prices.all():
                    if quantity >= price.quantity_from and quantity <= price.quantity_to:
                        result = price.price
                    else:
                        continue
            if result == 0:
                print(result, 'for one sw', product[0].price_dollar)
                return product[0].price_dollar
            else:
                print(result, 'small wholesale')
                return result
        elif user.client_wholesale:
            result: int = 0
            for modification in product:
                for price in modification.wholesale_prices.all():
                    if quantity >= price.quantity_from and quantity <= price.quantity_to:
                        result = price.price
                    else:
                        continue
            if result == 0:
                print(result, 'for one ws' , product[0].price_rub)
                return product[0].price_rub
            else:
                print(result, 'wholesale', type(result))
                return result

    def get_all_modification_prices_by_product_name(self, product_name=None):
        user = self.get_user()
        if user.client_small_wholesale:
            if not product_name:
                modifications = ProductModification.objects.all(
                ).prefetch_related(
                    'small_wholesale_prices'
                )
                price = []
                for modification in modifications:
                    price.append('______________________________________')
                    price.append(
                        f'{modification.product.name} {modification.specifications} \nЦена за единицу: {modification.price_dollar} usd Остаток: {modification.quantity}'
                    )
                    for wholesale in modification.small_wholesale_prices.all():
                        price.append(
                            f'{wholesale.price} usd - от {wholesale.quantity_from} до {wholesale.quantity_to} единиц'
                        )
                return price
            else:
                modifications = ProductModification.objects.filter(
                    product__name=product_name
                ).prefetch_related(
                    'small_wholesale_prices'
                )
                price = []
                for modification in modifications:
                    price.append('______________________________________')
                    price.append(
                        f'{product_name} {modification.specifications} \nЦена за единицу: {modification.price_dollar} usd Остаток: {modification.quantity}'
                    )
                    for wholesale in modification.small_wholesale_prices.all():
                        price.append(
                            f'{wholesale.price} usd - от {wholesale.quantity_from} до {wholesale.quantity_to} единиц'
                        )
                return price
        elif user.client_wholesale:
            if not product_name:
                modifications = ProductModification.objects.all(
                ).prefetch_related(
                    'small_wholesale_prices'
                )
                price = []
                for modification in modifications:
                    price.append('______________________________________')
                    price.append(
                        f'{modification.product.name} {modification.specifications} \nЦена за единицу: {modification.price_rub} rub Остаток: {modification.quantity}'
                    )
                    for wholesale in modification.small_wholesale_prices.all():
                        price.append(
                            f'{wholesale.price} rub - от {wholesale.quantity_from} до {wholesale.quantity_to} единиц'
                        )
                return price
            else:
                modifications = ProductModification.objects.filter(
                    product__name=product_name
                ).prefetch_related(
                    'wholesale_prices'
                )
                price = []
                for modification in modifications:
                    price.append('______________________________________')
                    price.append(
                        f'{product_name} {modification.specifications} \nЦена за единицу: {modification.price_rub} rub Остаток: {modification.quantity}'
                    )
                    for wholesale in modification.wholesale_prices.all():
                        price.append(
                            f'{wholesale.price} rub - от {wholesale.quantity_from} до {wholesale.quantity_to} единиц'
                        )
                return price

    def get_product_wholesale_price(self, modification_name, quantity: int):
        user = self.get_user()
        if user.client_small_wholesale:
            products = ProductModification.objects.filter(specifications=modification_name,
                                                          available_for_small_wholesale=True).prefetch_related(
                'small_wholesale_prices')
            smallwholesale = []
            for modification in products:
                for small_wholesale in modification.small_wholesale_prices.filter(quantity=quantity):
                    smallwholesale.append(small_wholesale)
            if len(smallwholesale) >= 1:
                return smallwholesale[0].price
            else:
                return False
        elif user.client_wholesale:
            products = ProductModification.objects.filter(specifications=modification_name,
                                                          available_for_small_wholesale=True).prefetch_related(
                'small_wholesale_prices')
            wholesale = []
            for modification in products:
                for small_wholesale in modification.wholesale_prices.filter(quantity=quantity):
                    wholesale.append(small_wholesale)
            if len(wholesale) >= 1:
                return wholesale[0].price
            else:
                return False

    def show_cart(self):
        cart = self.get_or_create_cart()
        cart_products = cart.products.all()
        products = [f'<b>{product.product.specifications} колличество:</b> {product.quantity} <b>стоимость:</b> {product.price}' for
                    product in cart_products]
        total = cart.total
        products.append(f'<b>Сумма:</b> {total}')
        return products

    def show_order(self):
        cart = self.get_or_create_cart()
        return cart.order

    def validation(self, func):
        if self.auth():
            func()
        return 'Ваш аккаунт не зарегистрирован или заблокирован'

    def create_registration_request(self, phone_number):
        try:
            request, created = RegistrationRequest.objects.get_or_create(
                telegram_id=str(self.telegram_id),
                telegram_username=self.telegram_username,
            )
            if created:
                user = CustomUser.objects.create_user(
                    username=str(self.telegram_id),
                    password=str(self.telegram_id) + self.telegram_username
                )
                Profile.objects.create(
                    user=user,
                    telegram_id=str(self.telegram_id),
                    telegram_username=self.telegram_username,
                    telegram_phone_number=phone_number,
                    token=request.token
                )
                return True
            return False
        except Exception as ex:
            print(ex)
            return False

    def create_invoice(self):
        user = self.get_user()
        cart = self.get_or_create_cart()
        fields = {
            'Товар': [],
            'Колличество': [],
            'Стоимость': [],
            'Общая сумма': [],
            'Дата создания заказа': [],
            'Номер заказа': []
        }
        orders = Order.objects.filter(identifier=cart.order.identifier).prefetch_related('cart', 'cart__products', 'cart__products__product')
        file_name = f'накладная {datetime.date.today().strftime("%d-%m-%Y")}.xlsx'
        for order in orders:
            for index, prod in enumerate(order.cart.products.all()):
                fields['Товар'].append(prod.product.specifications)
                fields['Колличество'].append(prod.quantity)
                fields['Стоимость'].append(prod.price)
                fields['Общая сумма'].append(order.cart.total if index == 0 else ' ')
                fields['Дата создания заказа'].append(datetime.datetime.now() if index == 0 else ' ')
                fields['Номер заказа'].append(order.identifier if index == 0 else ' ')
        file_path = os.path.join(MEDIA_ROOT, file_name)
        dataframe = pd.DataFrame(fields)
        dataframe.to_excel(file_path, sheet_name=file_name, index=False)
        return file_path

class Market:

    @staticmethod
    def get_help():
        message = HelpRules.objects.last()
        return f'{message.text}'

    @staticmethod
    def is_work_time(time):
        schedule = Schedule.objects.first()
        start_time = schedule.start_time
        end_time = schedule.end_time
        if start_time < time <= end_time:
            return True
        else:
            return False

    @staticmethod
    def show_schedule():
        schedule = Schedule.objects.first()
        return schedule.start_time, schedule.end_time

    @staticmethod
    def start_message(message: Message):
        text = StartMessage.objects.first()
        start_message = f'Приветствую {message.from_user.username}. {text.text if text else ""}'
        return start_message

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
        manufacturers_names = Manufacturer.objects.filter(available=True).values_list('name')
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
        products = Product.objects.filter(manufacturer__name=manufacturer_name, available=True, ).values_list('name')
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
    def get_modifications_wholesales_by_product(product_name, message: Message):
        user = MarketClient(message)
        client = user.get_user()
        if client.client_small_wholesale:
            modifications = ProductModification.objects.filter(
                product__name=product_name,
                available=True,
                available_for_small_wholesale=True
            ).prefetch_related('small_wholesale_prices')
            return modifications

        elif client.client_wholesale:
            modifications = ProductModification.objects.filter(
                product__name=product_name,
                available=True,
                available_for_wholesale=True
            ).prefetch_related('wholesale_prices')
            return modifications

    @staticmethod
    def wholesale_price_structure(modifications, nominal: str, user_status: str):
        price = []
        if user_status == 'sw':
            for modification in modifications:
                for wholesale in modification.small_wholesale_prices.all():
                    product = modification.specifications + ' за ' + str(wholesale.quantity) + ' единиц ' + str(
                        wholesale.price) + ' ' + nominal
                    price.append(product)
            return price
        else:
            for modification in modifications:
                for wholesale in modification.wholesale_prices.all():
                    product = modification.specifications + ' за ' + str(wholesale.quantity) + ' единиц ' + str(
                        wholesale.price) + ' ' + nominal
                    price.append(product)
            return price

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


def get_manufacturers_names_wholesale():
    manufacturers_names = Manufacturer.objects.all().values_list('name')
    result = [name[0] for name in manufacturers_names]
    result.insert(0, '3️⃣ Назад')
    return result


def get_products_names():
    products_names = Product.objects.all().values_list('name')
    result = [name[0] for name in products_names]
    result.insert(0, '1️⃣ Назад')
    return result


def get_products_names_wholesale():
    products_names = Product.objects.all().values_list('name')
    result = [name[0] for name in products_names]
    result.insert(0, '3️⃣ Назад')
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
