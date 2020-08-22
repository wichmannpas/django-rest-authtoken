from datetime import timedelta
from hashlib import sha512
from os import urandom
from typing import Optional, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .settings import AUTH_TOKEN_VALIDITY, REGISTRATION_EMAIL_CONFIRM_TOKEN_VALIDITY


class AbstractToken(models.Model):
    class Meta:
        abstract = True

    TOKEN_VALIDITY = AUTH_TOKEN_VALIDITY

    hashed_token = models.BinaryField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)ss',
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

    @classmethod
    def create_token_for_user(cls, user: get_user_model(), **kwargs) -> bytes:
        """
        Create a new random auth token for user.
        """
        token = urandom(48)
        cls.objects.create(
            hashed_token=cls._hash_token(token),
            user=user,
            **kwargs)
        return token

    @classmethod
    def get_user_for_token(cls, token: bytes) -> Optional[get_user_model()]:
        auth_token = cls.get_token(token)
        if auth_token:
            return auth_token.user

    @classmethod
    def get_token(cls, token: bytes) -> Optional['AbstractToken']:
        try:
            auth_token = cls.objects.select_related('user').get(
                hashed_token=cls._hash_token(token))

            if auth_token.age > cls.TOKEN_VALIDITY:
                # token expired.
                auth_token.delete()
                return None

            return auth_token
        except cls.DoesNotExist:
            return None

    @classmethod
    def clear_expired_tokens(cls) -> int:
        """
        Clear tokens that are expired.
        """
        valid_min_creation = timezone.now() - cls.TOKEN_VALIDITY
        deleted_count, detail = cls.objects.filter(created__lt=valid_min_creation).delete()
        return deleted_count

    @staticmethod
    def _hash_token(token: bytes) -> bytes:
        """
        Hash a token.
        """
        return sha512(token).digest()


class AuthToken(AbstractToken):
    pass


class EmailConfirmationToken(AbstractToken):
    TOKEN_VALIDITY = REGISTRATION_EMAIL_CONFIRM_TOKEN_VALIDITY

    email = models.EmailField()

    @classmethod
    def create_token_for_user(cls, user: get_user_model()) -> bytes:
        return super().create_token_for_user(user, email=user.email)
