from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ScheduleViewSet
from .views import StoreHouseViewSet
from .views import ManufacturerViewSet
from .views import ProductCategoryViewSet
from .views import ProductViewSet
from .views import ProductModificationViewSet

router = DefaultRouter()
router.register(r'schedule', ScheduleViewSet, basename='schedules')
router.register(r'storehouse', StoreHouseViewSet, basename='storehouses')
router.register(r'manufacturer', ManufacturerViewSet, basename='manufacturers')
router.register(r'product-category', ProductCategoryViewSet, basename='product_categories')
router.register(r'product', ProductViewSet, basename='products')
router.register(r'modification', ProductModificationViewSet, basename='modifications')


urlpatterns = [
    # path('client-registration/', ClientRegistrationAPIView.as_view()),
    # path('employee-registration/', EmployeeRegistrationAPIView.as_view()),
]
urlpatterns += router.urls
