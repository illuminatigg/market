from uuid import uuid4

from django.db import models
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from config.labels import FLAGS


# Create your models here.


ORDER_STATUS = (
    ('opened', 'Открыт'),
    ('created', 'Создан'),
    ('in_processing', 'В обработке'),
    ('delivered', 'Доставлен')
)


class Schedule(models.Model):
    start_time = models.TimeField(verbose_name='Начало работы')
    end_time = models.TimeField(verbose_name='Конец работы')

    class Meta:
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'

    # def save(self, *args, **kwargs):
    #     try:
    #         schedule, created = CrontabSchedule.objects.get_or_create(
    #             hour=str(self.end_time.hour),
    #             minute=str(self.end_time.minute),
    #             day_of_week='*',
    #             day_of_month='*',
    #             month_of_year='*',
    #             timezone='Europe/Moscow'
    #         )
    #         PeriodicTask.objects.create(
    #             crontab=schedule,
    #             name='Send end time report',
    #             task='market.tasks.send_report'
    #         )
    #         super().save(*args, **kwargs)
    #     except Exception as ex:
    #         super().save(*args, **kwargs)

    def __str__(self):
        return f'Бот работает с: {self.start_time} до: {self.end_time}'


class StoreHouse(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return f'Склад: {self.name}'


class Manufacturer(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name='Название')
    available = models.BooleanField(default=True, verbose_name='Доступен')

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name='Название')
    available = models.BooleanField(default=True, verbose_name='Доступен')

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=500, null=True, db_index=True, verbose_name='Наименование')
    quantity = models.IntegerField(default=0, verbose_name='Остаток')
    start_quantity = models.IntegerField(default=0, verbose_name='Изначальное колличество')
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        verbose_name='Производитель'
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        verbose_name='Категория'
    )
    store_house = models.ForeignKey(
        StoreHouse,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        verbose_name='Склад'
    )
    available = models.BooleanField(default=True, verbose_name='Доступен')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            self.start_quantity = self.quantity
            super().save(*args, **kwargs)
        except Exception as ex:
            super().save(*args, **kwargs)


class ProductModification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='modifications',
        null=True,
        verbose_name='Товар'
    )
    specifications = models.CharField(max_length=500, null=True, verbose_name='Характеристики')
    price_rub = models.DecimalField(max_digits=20, decimal_places=2, null=True, verbose_name='Стоимость за штутку')
    price_dollar = models.DecimalField(max_digits=20, decimal_places=2, null=True, verbose_name='Стоимость за штутку')
    quantity = models.PositiveBigIntegerField(default=0, verbose_name='Остаток')
    start_quantity = models.IntegerField(default=0, verbose_name='Изначальное колличество')
    available = models.BooleanField(default=True, verbose_name='Доступен')
    available_for_wholesale = models.BooleanField(default=True, verbose_name='Доступен для опта')
    available_for_small_wholesale = models.BooleanField(default=True, verbose_name='Доступен для мелкого опта')

    class Meta:
        verbose_name = 'Модификация'
        verbose_name_plural = 'Модификации'

    def __str__(self):
        return self.specifications

    def save(self, *args, **kwargs):
        try:
            country = self.specifications
            country = country.replace(country[-2:], FLAGS[country[-2:].upper()])
            self.specifications = country
            self.start_quantity = self.quantity
            super().save(*args, **kwargs)
        except Exception as ex:
            super().save(*args, **kwargs)


class WholesalePrice(models.Model):
    modification = models.ForeignKey(
        ProductModification,
        on_delete=models.CASCADE,
        related_name='wholesale_prices',
        verbose_name='Модификация'
    )
    quantity_from = models.IntegerField()
    quantity_to = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        verbose_name = 'Оптовая цена'
        verbose_name_plural = 'Оптовые цены'

    def __str__(self):
        return f'Цена за колличество от {self.quantity_from} до {self.quantity_to}'


class SmallWholesalePrice(models.Model):
    modification = models.ForeignKey(
        ProductModification,
        on_delete=models.CASCADE,
        related_name='small_wholesale_prices',
        verbose_name='Модификация'
    )
    quantity_from = models.IntegerField()
    quantity_to = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        verbose_name = 'Мелко-оптовая цена'
        verbose_name_plural = 'Мелко-оптовые цены'

    def __str__(self):
        return f'Цена за колличество от {self.quantity_from} до {self.quantity_to}'


class Order(models.Model):
    identifier = models.UUIDField(default=uuid4, editable=False, verbose_name='Уникальный идентификатор заказа')
    owner = models.CharField(max_length=255, null=True, db_index=True, verbose_name='Клиент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    status = models.CharField(max_length=50, choices=ORDER_STATUS, default='opened')
    delivered_at = models.DateTimeField(null=True)
    opened_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ №{self.id}, от {self.created_at}, статуc - {self.status}, клиент - {self.owner}'


class Cart(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='cart',
        null=True,
        verbose_name='Заказ'
    )
    owner = models.CharField(max_length=255, null=True)
    total = models.DecimalField(max_digits=30, decimal_places=2, null=True, verbose_name='Сумма', default=0.00)
    done = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина {self.owner} за {self.created_at}'


class CartProduct(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        ProductModification,
        on_delete=models.CASCADE,
        related_name='cartproduct'
    )
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, verbose_name='Стоимость', default=0.00)
    quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Товар для корзины'
        verbose_name_plural = 'Товары для корзины'

    def __str__(self):
        return self.product.specifications


class StartMessage(models.Model):
    text = models.TextField()

    class Meta:
        verbose_name = 'Приветственное сообщение'
        verbose_name_plural = 'Приветственные сообщения'


class EndMessage(models.Model):
    text = models.TextField()

    class Meta:
        verbose_name = 'Сообщение по окончанию работы'
        verbose_name_plural = 'Сообщения по окончанию работы'


class HelpRules(models.Model):
    text = models.TextField()

    class Meta:
        verbose_name = 'Правила'
        verbose_name_plural = 'Правила'


class ProductsUploadFile(models.Model):
    file = models.FileField(max_length=500, upload_to='files/')
    uploaded = models.DateTimeField(auto_now_add=True)


class ReportFile(models.Model):
    file = models.FileField(max_length=500, upload_to='reports/')
    created_at = models.DateTimeField(auto_now_add=True)