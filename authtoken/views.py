from base64 import urlsafe_b64encode

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import APISettings
from rest_framework.viewsets import GenericViewSet, ViewSet

from .models import AuthToken
from .serializers import UserRegistrationSerializer


authtoken_settings = APISettings(
    {
        'USER_SERIALIZER': getattr(settings, 'USER_SERIALIZER', None),
    },
    {
        'USER_SERIALIZER': None,
    },
    {'USER_SERIALIZER'}
)


class LoginViewSet(ViewSet):
    def create(self, request: Request) -> Response:
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password'))
        if not user:
            return Response(
                _('invalid credentials.'),
                status=status.HTTP_401_UNAUTHORIZED)

        token = AuthToken.create_token_for_user(user)

        data = {
            'token': urlsafe_b64encode(token),
        }

        if authtoken_settings.USER_SERIALIZER:
            data['user'] = authtoken_settings.USER_SERIALIZER(
                instance=user, read_only=True).data

        return Response(data)


class RegisterViewSet(GenericViewSet):
    serializer_class = UserRegistrationSerializer

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('', status=status.HTTP_201_CREATED)
