from uuid import uuid4

from django.db import models


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
    quantity = models.PositiveBigIntegerField(default=0, verbose_name='Остаток')
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


class ProductModification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='modifications',
        null=True,
        verbose_name='Товар'
    )
    specifications = models.CharField(max_length=500, null=True, verbose_name='Характеристики')
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, verbose_name='Стоимость')
    quantity = models.PositiveBigIntegerField(default=0, verbose_name='Остаток')
    available = models.BooleanField(default=True, verbose_name='Доступен')

    class Meta:
        verbose_name = 'Модификация'
        verbose_name_plural = 'Модификации'

    def __str__(self):
        return self.specifications


class WholesalePrice(models.Model):
    modification = models.ForeignKey(
        ProductModification,
        on_delete=models.CASCADE,
        related_name='wholesale_price',
        verbose_name='Модификация'
    )
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        verbose_name = 'Оптовая цена'
        verbose_name_plural = 'Оптовые цены'

    def __str__(self):
        return f'Цена за: {self.quantity}'


class Order(models.Model):
    identifier = models.UUIDField(default=uuid4, editable=False, verbose_name='Уникальный идентификатор заказа')
    owner = models.CharField(max_length=255, null=True, db_index=True, verbose_name='Клиент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    status = models.CharField(max_length=50, choices=ORDER_STATUS, default='opened')
    delivered_at = models.DateTimeField(null=True)

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
    total = models.DecimalField(max_digits=30, decimal_places=2, null=True, verbose_name='Сумма')
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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
    )
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Товар для корзины'
        verbose_name_plural = 'Товары для корзины'

    def __str__(self):
        return self.cart


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

