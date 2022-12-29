
from rest_framework import serializers

from .models import Schedule, ORDER_STATUS
from .models import StoreHouse
from .models import Manufacturer
from .models import ProductCategory
from .models import Product
from .models import ProductModification
from .models import Order
from .models import Cart
from .models import CartProduct


class ScheduleSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    class Meta:
        model = Schedule
        fields = ['id', 'start_time', 'end_time']


class StoreHouseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)

    class Meta:
        model = StoreHouse
        fields = ['id', 'name']


class ManufacturerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)

    class Meta:
        model = Manufacturer
        fields = ['id', 'name']


class ProductCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    products = serializers.StringRelatedField(many=True)

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'products']


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=500)
    quantity = serializers.IntegerField()
    manufacturer = serializers.PrimaryKeyRelatedField(
        queryset=Manufacturer.objects.all(),
        allow_null=True,
        required=False
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        allow_null=True,
        required=False
    )
    store_house = serializers.PrimaryKeyRelatedField(
        queryset=StoreHouse.objects.all(),
        allow_null=True,
        required=False
    )
    available = serializers.BooleanField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'quantity', 'manufacturer', 'category', 'store_house', 'available']


class ProductModificationSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=ProductModification.objects.all())
    specifications = serializers.CharField(max_length=500)
    price = serializers.DecimalField(max_digits=20, decimal_places=2)
    quantity = serializers.IntegerField()
    available = serializers.BooleanField()

    class Meta:
        model = ProductModification
        fields = ['id', 'product', 'specifications', 'price', 'quantity', 'available']


class CartSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    owner = serializers.CharField(read_only=True)
    total = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    done = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    products = serializers.StringRelatedField(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'order', 'owner', 'products', 'total', 'done', 'created_at']

    def create(self, validated_data):
        username = self.context['request'].user.username
        new_order = Order.objects.create(owner=username)
        cart = Cart.objects.create(
            order=new_order,
            owner=username,
        )
        return cart


class OrderSerializer(serializers.ModelSerializer):
    identifier = serializers.UUIDField(read_only=True)
    owner = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    delivered_at = serializers.DateTimeField(read_only=True)
    cart = serializers.StringRelatedField(many=False)

    class Meta:
        model = Order
        fields = ['id', 'identifier', 'owner', 'created_at', 'status', 'delivered_at']


