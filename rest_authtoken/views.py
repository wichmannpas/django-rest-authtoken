from base64 import urlsafe_b64decode, urlsafe_b64encode

from django.contrib.auth import authenticate, user_logged_in
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet

from .models import AuthToken, EmailConfirmationToken
from .serializers import UserRegistrationSerializer
from .settings import REGISTRATION_CONFIRM_INVALID_REDIRECT_PATH, \
    REGISTRATION_CONFIRM_REDIRECT_PATH, \
    REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD, USER_SERIALIZER


class LoginViewSet(ViewSet):
    @staticmethod
    def create(request: Request) -> Response:
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password'))
        if not user:
            return Response(
                'invalid credentials',
                status=status.HTTP_401_UNAUTHORIZED)

        token = AuthToken.create_token_for_user(user)

        data = {
            'token': urlsafe_b64encode(token),
        }

        if USER_SERIALIZER:
            data['user'] = USER_SERIALIZER(
                instance=user, read_only=True).data

        user_logged_in.send(sender=user.__class__, request=request, user=user)

        return Response(data)


class LogoutView(APIView):
    permission_classes = IsAuthenticated,

    @staticmethod
    def delete(request: Request) -> Response:
        auth_header = request.META.get('HTTP_AUTHORIZATION').split()

        if len(auth_header) != 2 or auth_header[0].lower() != 'token':
            raise ValidationError('no token')

        try:
            auth_token = urlsafe_b64decode(auth_header[1])
        except ValueError:
            raise ValidationError('invalid token')

        auth_token = AuthToken.get_token(auth_token)

        if not auth_token:
            raise ValidationError('invalid token')

        auth_token.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterViewSet(GenericViewSet):
    serializer_class = UserRegistrationSerializer

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)


@transaction.atomic
def confirm_email(request, token: str):
    def invalid_action():
        if REGISTRATION_CONFIRM_INVALID_REDIRECT_PATH:
            return HttpResponseRedirect(REGISTRATION_CONFIRM_INVALID_REDIRECT_PATH)
        else:
            return HttpResponseBadRequest('invalid token!')

    try:
        token = urlsafe_b64decode(token)
    except ValueError:
        return invalid_action()
    token = EmailConfirmationToken.get_token(token)
    if not token:
        return invalid_action()

    user = token.user
    if user.email != token.email:
        return invalid_action()

    setattr(user, REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD, True)
    user.save(update_fields=(REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD,))
    token.delete()

    return HttpResponseRedirect(REGISTRATION_CONFIRM_REDIRECT_PATH)
