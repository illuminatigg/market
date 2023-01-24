from django.core.management.base import BaseCommand, CommandError
from market.models import *
from accounts.models import CustomUser
from random import randint


class Command(BaseCommand):
    manufacturers = ['Apple', 'Samsung', 'Xiaomi']
    product_apple = ['iphone 11',
                     'iphone 12',
                     'iphone 13',
                     'iphone 14',
                     'iphone 11 pro',
                     'iphone 12 pro',
                     'iphone 13 pro',
                     'iphone 14 pro',
                     'iphone 11 pro max',
                     'iphone 12 pro max',
                     'iphone 13 pro max',
                     'iphone 14 pro max'
                     ]
    product_samsung = ['s20', 's21', 's22', 's20 ultra', 's21 ultra', 's22 ultra']
    product_xiaomi = ['mi 12', 'mi 12pro', 'mi 13', 'mi 13pro', 'mi 12ultra', 'mi 13ultra']

    ssd = [64, 128, 256, 512, 1024]
    ram = [4, 8, 16, 32]
    version = ['EU', 'US', 'CN', 'RU']
    colors = ['black', 'white', 'lgbt', 'blue', 'red']

    def apple_create(self, store_house):
        apple = Manufacturer.objects.create(name=self.manufacturers[0])
        products = [
            Product.objects.create(
                name=name,
                quantity=randint(10, 200),
                manufacturer=apple,
                store_house=store_house
            ) for name in self.product_apple
        ]
        modifications = [ProductModification.objects.create(
            product=product,
            specifications=f'{product} {self.ram[randint(0, len(self.ram) - 1)]}/{self.ssd[randint(0, len(self.ssd) - 1)]}/{self.colors[randint(0, len(self.colors) - 1)]}/{self.version[randint(0, len(self.version) - 1)]}',
            price_rub=randint(20000, 100000),
            price_dollar=randint(20000, 100000),
            quantity=randint(10, 50)
        ) for product in products
        ]

    def samsung_create(self, store_house):
        samsung = Manufacturer.objects.create(name=self.manufacturers[1])
        products = [
            Product.objects.create(
                name=name,
                quantity=randint(10, 200),
                manufacturer=samsung,
                store_house=store_house
            ) for name in self.product_samsung
        ]
        modifications = [ProductModification.objects.create(
            product=product,
            specifications=f'{product} {self.ram[randint(0, len(self.ram) - 1)]}/{self.ssd[randint(0, len(self.ssd) - 1)]}/{self.colors[randint(0, len(self.colors) - 1)]}/{self.version[randint(0, len(self.version) - 1)]}',
            price_rub=randint(20000, 100000),
            price_dollar=randint(20000, 100000),
            quantity=randint(10, 50)
        ) for product in products
        ]

    def xiaomi_create(self, store_house):
        mi = Manufacturer.objects.create(name=self.manufacturers[2])
        products = [
            Product.objects.create(
                name=name,
                quantity=randint(10, 200),
                manufacturer=mi,
                store_house=store_house
            ) for name in self.product_xiaomi
        ]
        modifications = [ProductModification.objects.create(
            product=product,
            specifications=f'{product} {self.ram[randint(0, len(self.ram) - 1)]}/{self.ssd[randint(0, len(self.ssd) - 1)]}/{self.colors[randint(0, len(self.colors) - 1)]}/{self.version[randint(0, len(self.version) - 1)]}',
            price_rub=randint(20000, 100000),
            price_dollar=randint(20000, 100000),
            quantity=randint(10, 50)
        ) for product in products
        ]

    def handle(self, *args, **options):
        try:
            CustomUser.objects.create_superuser(username='fedser', password='pft,jxrf3000')
            CustomUser.objects.create_superuser(username='rusjmg', password='Xam4ik123')
        except Exception as ex:
            print(f'also users created {ex}')
        ProductCategory.objects.all().delete()
        Manufacturer.objects.all().delete()
        StoreHouse.objects.all().delete()
        created_store_house = StoreHouse.objects.create(name='Тестовый')
        self.apple_create(store_house=created_store_house)
        self.samsung_create(store_house=created_store_house)
        self.xiaomi_create(store_house=created_store_house)
