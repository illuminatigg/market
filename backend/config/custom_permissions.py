from rest_framework.permissions import BasePermission
from accounts.models import CustomUser


class ClientPermission(BasePermission):

    def has_permission(self, request, view):
        username = request.data.get('telegram_id')
        try:
            user = CustomUser.objects.get(username=username, is_active=True)
            return True
        except Exception as ex:
            print(ex)
            return False
