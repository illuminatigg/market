from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import RegistrationRequest, CustomUser
from .serializers import RegistrationRequestSerializer, RegistrationRequestsSerializer, EmployeeSerializer


class ClientRegistrationAPIView(APIView):
    """Метод запроса на регистрацию клиента(только для тг)"""

    def post(self, request):
        serializer = RegistrationRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllowRegistrationRequestsUpdateAPIView(GenericViewSet, ListModelMixin, UpdateModelMixin, RetrieveModelMixin):
    """Метод на предоставление разрешения доступа к магазину"""
    queryset = RegistrationRequest.objects.filter(allow=False)
    serializer_class = RegistrationRequestsSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, BasicAuthentication]


class EmployeeRegistrationAPIView(APIView):
    """Метод создания персонала"""
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, BasicAuthentication]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeesAPIView(APIView):
    """Список сотрудников"""

    permission_classes = [IsAdminUser]

    def get(self, request):
        employees = CustomUser.objects.filter(client=False)
        return JsonResponse({'employees': employees}, safe=False)
