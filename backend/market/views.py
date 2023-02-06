import datetime
import os
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.core.files.storage import FileSystemStorage, default_storage
import pandas as pd
from django.core.files import File

from accounts.models import CustomUser
from config.settings import MEDIA_ROOT
from .filters import ProductFilter
from .mixins import PermissionsMixin
from .models import EndMessage, Order, SmallWholesalePrice, ProductsUploadFile, HelpRules, ReportFile
from .models import Manufacturer
from .models import Product
from .models import ProductCategory
from .models import ProductModification
from .models import Schedule
from .models import StartMessage
from .models import StoreHouse
from .models import WholesalePrice
from .serializers import EndMessageSerializer, SmallWholesalePriceSerializer, FileSerializer, HelpRulesSerializer, \
    ReportFileSerializer, OrderSerializer
from .serializers import ManufacturerSerializer
from .serializers import ProductCategorySerializer
from .serializers import ProductModificationSerializer
from .serializers import ProductSerializer
from .serializers import ScheduleSerializer
from .serializers import StartMessageSerializer
from .serializers import StoreHouseSerializer
from .serializers import WholesalePriceSerializer
from .tasks import excel_to_db


def get_now_time():
    now = datetime.datetime.now()
    return now.time()


class ScheduleViewSet(ModelViewSet, PermissionsMixin):
    """Класс расписания граффика работы бота"""
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.all()


class StoreHouseViewSet(ModelViewSet, PermissionsMixin):
    """Класс склада (возвращает, название склада и список товаров и модификации)"""
    serializer_class = StoreHouseSerializer
    queryset = StoreHouse.objects.all().prefetch_related(
        'products',
        'products__modifications'
    )


class ManufacturerViewSet(ModelViewSet, PermissionsMixin):
    """Класс производителя"""
    serializer_class = ManufacturerSerializer
    queryset = Manufacturer.objects.all().prefetch_related('products', 'products__modifications')


class ProductCategoryViewSet(ModelViewSet, PermissionsMixin):
    """Класс категории товара"""
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()


class ProductViewSet(ModelViewSet, PermissionsMixin):
    """Класс товара"""
    serializer_class = ProductSerializer
    queryset = Product.objects.all().prefetch_related('modifications')
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductModificationViewSet(ModelViewSet, PermissionsMixin):
    """Класс модификаций товара"""
    serializer_class = ProductModificationSerializer
    queryset = ProductModification.objects.all().prefetch_related('wholesale_prices')


# class OrdersAPIView(APIView, PermissionsMixin):
#     """Метод возвращает закрытые заказы"""
#     def get(self, request):
#         orders = Order.objects.filter(status='created').select_related('cart')
#         return Response()


class WholesalePriceViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = WholesalePriceSerializer
    queryset = WholesalePrice.objects.all()


class SmallWholesalePriceViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = SmallWholesalePriceSerializer
    queryset = SmallWholesalePrice.objects.all()


class StartMessageViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = StartMessageSerializer
    queryset = StartMessage.objects.all()


class EndMessageViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = EndMessageSerializer
    queryset = EndMessage.objects.all()


class HelpMessageViewSet(ModelViewSet, PermissionsMixin):
    serializer_class = HelpRulesSerializer
    queryset = HelpRules.objects.all()


class StatisticAPIView(APIView, PermissionsMixin):

    def get(self, request):
        date = datetime.datetime.now().date()
        yesterday_date = date - datetime.timedelta(days=1)
        clients = CustomUser.objects.filter(approved=True)
        orders = Order.objects.all()
        previous_orders = Order.objects.filter(
            opened_at=yesterday_date
        ).prefetch_related('cart', 'cart__products')
        sold_products_count = 0
        total = 0
        for order in previous_orders:
            total += order.cart.total
            for product in order.cart.products:
                sold_products_count += product.quantity
        payload = {
            'clients': previous_orders.count(),
            'orders': previous_orders.count(),
            'sold': sold_products_count,
            'total_price': clients.count(),
            'orders_all': orders.count()
        }
        return Response({'statistic': payload}, status=status.HTTP_200_OK)


class FileLoader(APIView, PermissionsMixin):

    def post(self, request):
        file = ProductsUploadFile.objects.create(file=request.FILES['file'])
        excel_to_db.delay(file.file.path, file.id)
        return Response('saved', status=status.HTTP_201_CREATED)


class DeleteAllProducts(APIView, PermissionsMixin):

    def get(self, request):
        try:
            Manufacturer.objects.all().delete()
            return Response('Все продукты успешно удалены.', status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(f'Что то пошло не так: {ex}', status=status.HTTP_400_BAD_REQUEST)


class ReportFileView(APIView, PermissionsMixin):

    def get(self, request):
        fields = {
            'Товар': [],
            'Колличество': [],
            'Стоимость': [],
            'Общая сумма': [],
            'Дата создания заказа': [],
            'Номер заказа': [],
            'Клиент': []
        }
        orders = Order.objects.all().prefetch_related('cart', 'cart__products', 'cart__products__product') # добавить фильтрацию по статусу
        user = CustomUser.objects.all().prefetch_related('profiles')
        file_name = f'report {datetime.date.today().strftime("%d-%m-%Y")}.xlsx'
        for order in orders:
            try:
                owner = user.get(username=order.owner)
            except Exception as ex:
                print(ex)
                continue

            for index, prod in enumerate(order.cart.products.all()):
                fields['Товар'].append(prod.product.specifications)
                fields['Колличество'].append(prod.quantity)
                fields['Стоимость'].append(prod.price)
                fields['Общая сумма'].append(order.cart.total if index == 0 else ' ')
                fields['Дата создания заказа'].append(datetime.datetime.now() if index == 0 else ' ')
                fields['Номер заказа'].append(order.identifier if index == 0 else ' ')
                fields['Клиент'].append(owner.nickname if owner.nickname else owner.profiles.telegram_username)

        file_path = os.path.join(MEDIA_ROOT, file_name)
        dataframe = pd.DataFrame(fields)
        dataframe.to_excel(file_path, sheet_name=file_name, index=False)
        report_file = ReportFile()
        with open(file_path, 'rb') as f:
            report_file.file.save(file_name, File(f))
            report_file.save()
        os.remove(file_path)
        serializer = ReportFileSerializer(report_file)
        return Response(serializer.data)


class OpenedOrdersView(APIView, PermissionsMixin):

    def get(self, request):
        orders = Order.objects.filter(status='opened').prefetch_related('cart', 'cart__products', 'cart__products__product')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class MarketManufacturersAll(APIView):
#     permission_classes = [ClientPermission]
#
#     def get(self, request):
#         allowed = work_time(get_now_time())
#         if allowed:
#             manufacturers = Manufacturer.objects.all()
#             serializer = ManufacturerSerializer(manufacturers, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {'message': f'В данный момент времени заказы не принимаются'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# class MarketProductsByManufacturer(APIView):
#     # permission_classes = [ClientPermission]
#
#     def get(self, request):
#         if allowed:
#             products = Product.objects.filter(
#                 manufacturer__name=request.data['manufacturer']
#             ).select_related('manufacturer', 'category', 'store_house').prefetch_related(
#                 'modifications')
#             serializer = ClientProductSerializer(products, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {'message': f'В данный момент времени заказы не принимаются'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# class MarketFilteredProducts(APIView):
#     # permission_classes = [ClientPermission]
#
#     def get(self, request):
#         allowed = work_time(get_now_time())
#         if allowed:
#             name = request.data['product_name']
#             products = Product.objects.filter(
#                 manufacturer__name=name
#             ).select_related('manufacturer', 'category', 'store_house').prefetch_related('modifications')
#             serializer = ClientProductSerializer(products, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {'message': f'В данный момент времени заказы не принимаются'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# class MarketProductCategoryAll(APIView):
#     # permission_classes = [ClientPermission]
#
#     def get(self, request):
#         allowed = work_time(get_now_time())
#         if allowed:
#             categories = ProductCategory.objects.all()
#             print(len(categories))
#             serializer = ClientProductCategorySerializer(categories, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {'message': f'В данный момент времени заказы не принимаются'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# # class ClientCart(APIView):
# #     permission_classes = [ClientPermission]
# #
# #     def post(self, request):
# #         allowed = work_time(get_now_time())
# #         print(allowed)
# #         if allowed:
# #             client_cart, created = Cart.objects.get_or_create(
# #                 owner=request.data.get('telegram_id'),
# #                 created_at=datetime.datetime.now().date()
# #             )
# #             if created:
# #                 new_order = Order.objects.create(owner=request.data.get('telegram_id'))
# #                 client_cart.order = new_order
# #                 client_cart.save()
# #                 return Response({'id': client_cart.id}, status=status.HTTP_201_CREATED)
# #             return Response({'id': client_cart.id}, status=status.HTTP_200_OK)
# #         else:
# #             return Response(
# #                 {'message': f'В данный момент времени заказы не принимаются'},
# #                 status=status.HTTP_400_BAD_REQUEST
# #             )
#
#
# class MarketModificationByProduct(APIView):
#     permission_classes = [ClientPermission]
#
#     def get(self, request):
#         allowed = work_time(get_now_time())
#         if allowed:
#             categories = ProductModification.objects.filter(
#                 product__name=request.data['product']
#             )
#             serializer = ClientProductModificationSerializer(categories, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {'message': f'В данный момент времени заказы не принимаются'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# # class MarketAddProductsToCart(APIView):
# #     permission_classes = [ClientPermission]
# #
# #     def post(self, request):
# #         cart = Cart.objects.get(owner=request.data.get('telegram_id'))
# #         products = request.data.get('products_to_cart')
# #         for product in products:
# #             CartProduct.objects.create(
# #                 cart=cart,
# #                 product=product.id,
# #                 price=product.price
# #             )
# #
#
#
# from .serializers import BotManufacturerSerializer, BotProductSerializer, BotModificationSerializer
#
#
# class BotMarketView(APIView):
#     permission_classes = [ClientPermission]
#
#     def get(self, request):
#         allowed = work_time(get_now_time())
#         if allowed:
#             if request.data.get('return_manufacturers'):
#                 manufacturers = Manufacturer.objects.all()
#                 serializer = BotManufacturerSerializer(manufacturers, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             elif request.data.get('return_product'):
#                 products = Product.objects.filter(
#                     manufacturer__name=request.data.get('manufacturer_name')
#                 )
#                 serializer = BotProductSerializer(products, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             elif request.data.get('return_modification'):
#                 modifications = ProductModification.objects.filter(
#                     product__name=request.data.get('product_name')
#                 )
#                 serializer = BotModificationSerializer(modifications, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {'message': f'В данный момент времени заказы не принимаются'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#
# class BotCartView(APIView):
#     permission_classes = [ClientPermission]
#
#     def get(self, request):
#         allowed = work_time(get_now_time())
#         if allowed:
#             client_cart, created = Cart.objects.get_or_create(
#                 owner=request.data.get('telegram_id'),
#                 created_at=datetime.datetime.now().date()
#             )
#             if created:
#                 new_order = Order.objects.create(owner=request.data.get('telegram_id'))
#                 client_cart.order = new_order
#                 client_cart.save()
#                 return Response({'id': client_cart.id}, status=status.HTTP_201_CREATED)
#             return Response({'id': client_cart.id}, status=status.HTTP_200_OK)
#
#         else:
#             return Response(
#                 {'message': f'В данный момент времени заказы не принимаются'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#     def put(self, request, pk, format=None):
#         cart = Cart.objects.get(id=pk)
#         product_modification = ProductModification.objects.get(id=request.data.get('product_modification_id'))
#         cart_product = CartProduct.objects.create(
#             cart=cart,
#             product=product_modification,
#             price=request.data.get('product_modification_price'),
#             quantity=request.data.get('quantity')
#         )
#
