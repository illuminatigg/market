from rest_framework.permissions import BasePermission
from .models import CustomUser


class IsAUser(BasePermission):

    def has_permission(self, request, view):
        print(request.user)
        if CustomUser.objects.get(username=request.user):
            return True
        else:
            return False