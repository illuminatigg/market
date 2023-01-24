from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import RegistrationRequest, CustomUser, Profile
from .serializers import ClientRegistrationRequestSerializer, ApproveRegistrationRequestsSerializer, EmployeeSerializer
from .messages import AUTH_MESSAGE
from .serializers import ClientSerializer
from .local_permissions import IsAUser


class ClientRegistrationAPIView(APIView):
    """Метод запроса на регистрацию клиента(только для тг)"""

    def post(self, request):
        registration, created = RegistrationRequest.objects.get_or_create(
            telegram_id=request.data.get('telegram_id'),
            telegram_username=request.data.get('telegram_username'),
            telegram_phone_number=None
        )
        if created:
            customer = CustomUser.objects.create_user(
                username=registration.telegram_id,
                password=registration.telegram_id + registration.telegram_username,
                is_active=False,

            )
            Profile.objects.create(
                user=customer,
                telegram_id=registration.telegram_id,
                telegram_username=registration.telegram_username,
                telegram_phone_number=None,
                token=registration.token
            )
            return Response({'response_message': 'Заявка успешно создана'}, status=status.HTTP_201_CREATED)
        else:
            if registration.allow:
                return Response(
                    {'response_message': 'Ваш аккаунт уже зарегистрирован'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'response_message': f'Запрос в обработке. Дата создания: {registration.created_at}'},
                    status=status.HTTP_200_OK
                )


class AllowRegistrationRequestsUpdateAPIView(GenericViewSet, ListModelMixin, UpdateModelMixin, RetrieveModelMixin):
    """Метод на предоставление разрешения доступа к магазину"""
    queryset = RegistrationRequest.objects.filter(allow=False)
    serializer_class = ApproveRegistrationRequestsSerializer
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]


class EmployeeRegistrationAPIView(APIView):
    """Метод создания персонала"""
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeesAPIView(APIView):
    """Список сотрудников"""

    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]

    def get(self, request):
        employees = CustomUser.objects.filter(client=False)
        return JsonResponse({'employees': employees}, safe=False)


class HelpAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({'message': AUTH_MESSAGE}, safe=False)


class IsAllowedClientCheck(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user = CustomUser.objects.get(username=request.data['telegram_id'])
        except Exception as ex:
            return JsonResponse({'message': 'Аккаунт не зарегистрирован.'})
        if user and user.is_active:
            return JsonResponse({'message': 'ok'})
        else:
            return JsonResponse({'message': 'Регистрация в обработке.'})


class ClientsViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin, RetrieveModelMixin):
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    serializer_class = ClientSerializer
    queryset = CustomUser.objects.filter(client=True)
