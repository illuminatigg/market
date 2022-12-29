from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .serializers import ScheduleSerializer
from .serializers import StoreHouseSerializer
from .serializers import ManufacturerSerializer
from .serializers import ProductCategorySerializer
from .serializers import ProductSerializer
from .serializers import ProductModificationSerializer
from .models import StoreHouse
from .models import Schedule
from .models import Manufacturer
from .models import ProductCategory
from .models import Product
from .models import ProductModification
from .mixins import PermissionsMixin


class ScheduleViewSet(ModelViewSet, PermissionsMixin):
    """Класс расписания граффика работы бота"""
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.first()


class StoreHouseViewSet(ModelViewSet, PermissionsMixin):
    """Класс склада (возвращает, название склада и список товаров и модификации)"""
    serializer_class = StoreHouseSerializer
    queryset = StoreHouse.objects.all().prefetch_related(
        'products',
        'products__modifications'
    )


class ManufacturerViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = ManufacturerSerializer
    queryset = Manufacturer.objects.all()


class ProductCategoryViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()


class ProductViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductModificationViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = ProductModificationSerializer
    queryset = ProductModification.objects.all()





