import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=255, null=True, verbose_name='Дополнительное имя')
    organization = models.CharField(max_length=255, null=True, verbose_name='Организация')
    banned = models.BooleanField(default=False, verbose_name='Заблокирован')
    client = models.BooleanField(default=False, verbose_name='Клиент') # видит весь прайс
    client_wholesale = models.BooleanField(default=False, verbose_name='Крупно-оптовый клиент') # только купный опт прайс
    client_small_wholesale = models.BooleanField(default=False, verbose_name='Мелко-оптовый клиент') # только мелкий опт прайс
    approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='profiles'
    )
    telegram_id = models.CharField(unique=True, max_length=500)
    telegram_username = models.CharField(max_length=255, null=True)
    telegram_phone_number = models.CharField(max_length=15, null=True)
    token = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Клиентские профили'

    def __str__(self):
        return f'id клиента:{self.telegram_id}'


class RegistrationRequest(models.Model):
    telegram_id = models.CharField(max_length=500)
    telegram_username = models.CharField(max_length=255, null=True)
    telegram_phone_number = models.CharField(max_length=15, null=True)
    allow = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4(), editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    client = models.BooleanField(default=False, verbose_name='Клиент')  # видит весь прайс
    client_wholesale = models.BooleanField(default=False,
                                           verbose_name='Крупно-оптовый клиент')  # только купный опт прайс
    client_small_wholesale = models.BooleanField(default=False,
                                                 verbose_name='Мелко-оптовый клиент')  # только мелкий опт прайс

    class Meta:
        verbose_name = 'Запрос на регистрацию'
        verbose_name_plural = 'Запросы на регистрацию'

    def __str__(self):
        return self.telegram_id