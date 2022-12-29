from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication, BasicAuthentication


class PermissionsMixin:
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, BasicAuthentication]