from django.contrib import admin

from .models import CustomUser, Profile, RegistrationRequest
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'client', 'nickname']
    list_editable = ['nickname']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id', 'telegram_username', 'telegram_phone_number']


@admin.register(RegistrationRequest)
class RegistrationRequest(admin.ModelAdmin):
    list_display = ['telegram_id', 'telegram_username', 'telegram_phone_number', 'allow']
    list_editable = ['allow']
