from base64 import urlsafe_b64encode, urlsafe_b64decode

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import APISettings
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.views import APIView

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


class LogoutView(APIView):
    permission_classes = IsAuthenticated,

    def delete(self, request: Request) -> Response:
        auth_header = request.META.get('HTTP_AUTHORIZATION').split()

        if len(auth_header) != 2 or auth_header[0].lower() != 'token':
            raise ParseError('no token')

        try:
            auth_token = urlsafe_b64decode(auth_header[1])
        except ValueError:
            raise ParseError('invalid token')

        auth_token = AuthToken.get_auth_token(auth_token)

        if not auth_token:
            raise ParseError('invalid token')

        auth_token.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterViewSet(GenericViewSet):
    serializer_class = UserRegistrationSerializer

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('', status=status.HTTP_201_CREATED)
