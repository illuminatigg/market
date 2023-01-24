from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientRegistrationAPIView, AllowRegistrationRequestsUpdateAPIView, EmployeeRegistrationAPIView
from .views import HelpAPIView, ClientsViewSet, IsAllowedClientCheck

router = DefaultRouter()
router.register(r'registration-requests', AllowRegistrationRequestsUpdateAPIView, basename='client_registration')
router.register(r'clients', ClientsViewSet, basename='clients')
urlpatterns = [
    path('client-registration/', ClientRegistrationAPIView.as_view()),
    path('employee-registration/', EmployeeRegistrationAPIView.as_view()),
    path('help-message/', HelpAPIView.as_view()),
    path('client-auth/', IsAllowedClientCheck.as_view()),
]
urlpatterns += router.urls
