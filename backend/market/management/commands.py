from django.core.management.base import BaseCommand, CommandError
from market.models import *
import random


class DbDataCreate(BaseCommand):
    categories = ['Ноутбуки', 'Смартфоны']
    manufacturers = ['Apple', 'Samsung', 'mi', 'Acer', 'Asus', 'Lenovo', 'Nokia', 'Dell']
    products = [
        'iphone 11',
        'iphone 12',
        'iphone 13',
        'iphone 14',
        'zenphone',
        'gt',
        'lte',
        'nexus'
        'rog',
        'g',
        's22',
        's21',
        's20',
        'xt',
        'rtx',
        'gnga'
    ]
    ssd = [64, 128, 256, 512, 1024]
    ram = [4, 8, 16, 32]
    version = ['EU', 'US', 'CN', 'RU']
    colors = ['black', 'white', 'lgbt', 'blue', 'red']

    def handle(self, *args, **options):
        store_house = StoreHouse.objects.create(name='Тестовый')
        created_manufacturers = []
        created_products = []
        created_categories = []
        for manufacturer in self.manufacturers:
            created_manufacturers.append(Manufacturer.objects.create(name=manufacturer))

        for cat in self.categories:
            created_categories.append(ProductCategory.objects.create(name=cat))

        for product in self.products:
            created_products.append(
                Product.objects.create(
                    name=product,
                    quantity=random.randint(50, 500),
                    manufacturer=created_manufacturers[random.randint(0, len(self.manufacturers) - 1)],
                    category=created_categories[random.randint(0, 1)],
                    store_house=store_house
                )
            )
        for modification in range(0, 500):
            ProductModification.objects.create(
                product=created_products[random.randint(0, len(created_products) -1 )],
                specifications=f'{self.ssd[random.randint(0, len(self.ssd) - 1)]}/{self.ram[random.randint(0, len(self.ram) - 1)]}/{self.colors[random.randint(0, len(self.colors) - 1)]}/{self.version[random.randint(0, len(self.version) - 1)]}',
                price=random.randint(10000, 90000),
                quantity=random.randint(50, 500),
            )