from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ScheduleViewSet
from .views import StoreHouseViewSet
from .views import ManufacturerViewSet
from .views import ProductCategoryViewSet
from .views import ProductViewSet
from .views import ProductModificationViewSet
from .views import WholesalePriceViewSet
from .views import StartMessageViewSet
from .views import EndMessageViewSet
from .views import StatisticAPIView
from .views import SmallWholesalePriceViewSet
from .views import FileLoader
from .views import HelpMessageViewSet
from .views import DeleteAllProducts
from .views import ReportFileView
from .views import OpenedOrdersView

router = DefaultRouter()
router.register(r'schedule', ScheduleViewSet, basename='schedules')
router.register(r'storehouse', StoreHouseViewSet, basename='storehouses')
router.register(r'manufacturer', ManufacturerViewSet, basename='manufacturers')
router.register(r'product-category', ProductCategoryViewSet, basename='product_categories')
router.register(r'product', ProductViewSet, basename='products')
router.register(r'modification', ProductModificationViewSet, basename='modifications')
router.register(r'whole-sale', WholesalePriceViewSet, basename='whole_sale')
router.register(r'small-whole-sale', SmallWholesalePriceViewSet, basename='small_whole_sale')
router.register(r'start-message', StartMessageViewSet, basename='start_message')
router.register(r'end-message', EndMessageViewSet, basename='end_message')
router.register(r'help-message', HelpMessageViewSet, basename='help_message')


urlpatterns = [
    path('statistics/', StatisticAPIView.as_view()),
    path('file/', FileLoader.as_view()),
    path('delete-all-products/', DeleteAllProducts.as_view()),
    path('daily-report/', ReportFileView.as_view()),
    path('opened-orders/', OpenedOrdersView.as_view())


]
urlpatterns += router.urls
