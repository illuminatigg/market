from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ClientRegistrationAPIView, AllowRegistrationRequestsUpdateAPIView

router = DefaultRouter()
router.register(r'registration-requests', AllowRegistrationRequestsUpdateAPIView, basename='client_registration')
urlpatterns = [
    path('client-registration/', ClientRegistrationAPIView.as_view()),
]
urlpatterns += router.urls
