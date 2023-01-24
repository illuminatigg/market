from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication


class PermissionsMixin:
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]