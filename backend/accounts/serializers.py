import asyncio

from rest_framework import serializers
from .models import CustomUser, Profile, RegistrationRequest
from config.settings import BOT


async def send_approve_message(customer):
    if customer.approved:
        await BOT.send_message(customer.username,
                               'Доброго времени суток. Ваша регистрация подтверждена, доступ к магазину открыт.')
    else:
        await BOT.send_message(customer.username, 'Ваш запрос на регистрацию не подтвержден. Обратитесь к оператору')


class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def create(self, validated_data):
        employee = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_staff=True,
        )
        return employee


class ClientTgProfileSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(read_only=True)
    telegram_username = serializers.CharField(read_only=True)
    telegram_phone_number = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ['telegram_id', 'telegram_username', 'telegram_phone_number']


class ClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, required=True)
    nickname = serializers.CharField(max_length=255, required=False)
    organization = serializers.CharField(read_only=True)
    client_wholesale = serializers.BooleanField(required=False)
    client_small_wholesale = serializers.BooleanField(required=False)
    banned = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    profiles = ClientTgProfileSerializer(many=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'nickname', 'organization', 'banned', 'is_active', 'profiles', 'client_wholesale', 'client_small_wholesale']


class ClientRegistrationRequestSerializer(serializers.ModelSerializer):
    telegram_id = serializers.CharField(max_length=500)
    telegram_username = serializers.CharField(required=False, allow_null=True, max_length=255)
    telegram_phone_number = serializers.CharField(required=False, allow_null=True, max_length=15)

    class Meta:
        model = RegistrationRequest
        fields = ['telegram_id', 'telegram_username', 'telegram_phone_number']

    def create(self, validated_data):
        new_request = RegistrationRequest.objects.create(
            telegram_id=validated_data['telegram_id'],
            telegram_username=validated_data['telegram_username'],
            telegram_phone_number=validated_data['telegram_phone_number'],
        )
        customer = CustomUser.objects.create_user(
            username=validated_data['telegram_id'],
            password=validated_data['telegram_id'] + validated_data['telegram_username'],
            is_active=False,
            client=True
        )
        Profile.objects.create(
            user=customer,
            telegram_id=validated_data['telegram_id'],
            telegram_username=validated_data['telegram_username'],
            telegram_phone_number=validated_data['telegram_phone_number'],
            token=new_request.token
        )
        return new_request


class ApproveRegistrationRequestsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, required=False)
    telegram_id = serializers.CharField(read_only=True, required=False)
    telegram_username = serializers.CharField(read_only=True, required=False)
    telegram_phone_number = serializers.CharField(read_only=True, required=False, allow_null=True)
    allow = serializers.BooleanField(required=False)
    client = serializers.BooleanField(required=False)
    client_wholesale = serializers.BooleanField(required=False)
    client_small_wholesale = serializers.BooleanField(required=False)

    class Meta:
        model = RegistrationRequest
        fields = [
            'id',
            'telegram_id',
            'telegram_username',
            'telegram_phone_number',
            'allow',
            'client',
            'client_wholesale',
            'client_small_wholesale'
        ]

    def update(self, instance, validated_data):
        instance.allow = validated_data.get('allow', instance.allow)
        instance.save()
        customer = CustomUser.objects.get(username=instance.telegram_id)
        customer.is_active = instance.allow
        customer.client = validated_data['client']
        customer.client_wholesale = validated_data['client_wholesale']
        customer.client_small_wholesale = validated_data['client_small_wholesale']
        customer.approved = instance.allow
        customer.save()
        asyncio.run(send_approve_message(customer))
        return instance








