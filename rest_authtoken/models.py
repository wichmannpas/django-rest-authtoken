from datetime import timedelta
from hashlib import sha512
from os import urandom
from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class AuthToken(models.Model):
    hashed_token = models.BinaryField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='auth_tokens',
        on_delete=models.CASCADE)

    created = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return '{}: {}'.format(self.user, self.hashed_token)

    @property
    def age(self) -> timedelta:
        return timezone.now() - self.created

    def logout(self, token: Union[str, None] = None):
        """
        Log this token out.
        """
        self.delete()

    @staticmethod
    def create_token_for_user(user: get_user_model()) -> bytes:
        """
        Create a new random auth token for user.
        """
        token = urandom(48)
        AuthToken.objects.create(
            hashed_token=AuthToken._hash_token(token),
            user=user)
        return token

    @staticmethod
    def get_user_for_token(token: bytes) -> Union[get_user_model(), None]:
        auth_token = AuthToken.get_auth_token(token)
        if auth_token:
            return auth_token.user

    @staticmethod
    def get_auth_token(token: bytes) -> Union[get_user_model(), None]:
        try:
            auth_token = AuthToken.objects.get(
                hashed_token=AuthToken._hash_token(token))

            if auth_token.age > settings.AUTH_TOKEN_VALIDITY:
                # token expired.
                auth_token.delete()
                return None

            return auth_token
        except AuthToken.DoesNotExist:
            return None

    @staticmethod
    def _hash_token(token: bytes) -> bytes:
        """
        Hash a token.
        """
        return sha512(token).digest()
