from rest_framework import serializers

from .models import Schedule, ORDER_STATUS, SmallWholesalePrice, ProductsUploadFile, HelpRules, ReportFile
from .models import StoreHouse
from .models import Manufacturer
from .models import ProductCategory
from .models import Product
from .models import ProductModification
from .models import Order
from .models import Cart
from .models import CartProduct
from .models import WholesalePrice
from .models import StartMessage
from .models import EndMessage


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
    available = serializers.BooleanField()

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'available']


class ProductCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    products = serializers.StringRelatedField(many=True)

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'products']


class WholesalePriceSerializer(serializers.ModelSerializer):
    modification = serializers.PrimaryKeyRelatedField(queryset=ProductModification.objects.all())
    quantity_from = serializers.IntegerField()
    quantity_to = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        model = WholesalePrice
        fields = ['id', 'modification', 'quantity_from', 'quantity_to', 'price']


class SmallWholesalePriceSerializer(serializers.ModelSerializer):
    modification = serializers.PrimaryKeyRelatedField(queryset=ProductModification.objects.all())
    quantity_from = serializers.IntegerField()
    quantity_to = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        model = SmallWholesalePrice
        fields = ['id', 'modification', 'quantity_from', 'quantity_to', 'price']


class ProductModificationSerializer(serializers.ModelSerializer):
    specifications = serializers.CharField(max_length=500)
    price_rub = serializers.DecimalField(max_digits=20, decimal_places=2)
    price_dollar = serializers.DecimalField(max_digits=20, decimal_places=2)
    quantity = serializers.IntegerField()
    start_quantity = serializers.CharField(read_only=True)
    available = serializers.BooleanField()
    available_for_wholesale = serializers.BooleanField()
    available_for_small_wholesale = serializers.BooleanField()
    wholesale_prices = WholesalePriceSerializer(many=True, required=False, read_only=True)
    small_wholesale_prices = SmallWholesalePriceSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = ProductModification
        fields = [
            'id',
            'product',
            'specifications',
            'price_rub',
            'price_dollar',
            'start_quantity',
            'quantity',
            'available',
            'available_for_wholesale',
            'available_for_small_wholesale',
            'wholesale_prices',
            'small_wholesale_prices',
        ]


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=500)
    quantity = serializers.IntegerField(required=False)
    start_quantity = serializers.CharField(read_only=True, required=False)
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
    modifications = ProductModificationSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'quantity', 'start_quantity', 'manufacturer', 'category', 'store_house', 'available', 'modifications']


class CartProductSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.specifications')
    class Meta:
        model = CartProduct
        fields = ['product', 'price', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    done = serializers.BooleanField(read_only=True)
    created_at = serializers.DateField(read_only=True)
    products = CartProductSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['products', 'total', 'done', 'created_at', 'products']


class OrderSerializer(serializers.ModelSerializer):
    identifier = serializers.UUIDField(read_only=True)
    owner = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    cart = CartSerializer()

    class Meta:
        model = Order
        fields = ['id', 'identifier', 'owner', 'created_at', 'status', 'cart']


class StartMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = StartMessage
        fields = ['text']


class EndMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = EndMessage
        fields = ['text']


class BotManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name']


class BotProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'quantity']


class BotModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModification
        fields = ['id', 'specifications', 'price', 'quantity']


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductsUploadFile
        fields = ['file']


class HelpRulesSerializer(serializers.ModelSerializer):

    class Meta:
        model = HelpRules
        fields = ['text']


class ReportFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportFile
        fields = ['file', 'created_at']
