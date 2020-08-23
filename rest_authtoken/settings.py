from datetime import timedelta

from django.conf import settings
from django.utils.module_loading import import_string

USER_SERIALIZER = getattr(settings, 'USER_SERIALIZER', None)
if USER_SERIALIZER:
    USER_SERIALIZER = import_string(USER_SERIALIZER)

AUTH_TOKEN_VALIDITY = getattr(settings, 'AUTH_TOKEN_VALIDITY', timedelta(days=1))

REGISTRATION_ENABLED = getattr(settings, 'REGISTRATION_ENABLED', False)
REGISTRATION_EMAIL_CONFIRM = getattr(settings, 'REGISTRATION_EMAIL_CONFIRM', False)
REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD = getattr(
    settings, 'REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD', False)
REGISTRATION_EMAIL_CONFIRM_TOKEN_VALIDITY = getattr(
    settings, 'REGISTRATION_EMAIL_CONFIRM_TOKEN_VALIDITY', timedelta(days=1))
REGISTRATION_EMAIL = getattr(
    settings, 'REGISTRATION_EMAIL', None)
REGISTRATION_CONFIRM_REDIRECT_PATH = getattr(
    settings, 'REGISTRATION_CONFIRM_REDIRECT_PATH', '/')
REGISTRATION_CONFIRM_INVALID_REDIRECT_PATH = getattr(
    settings, 'REGISTRATION_CONFIRM_INVALID_REDIRECT_PATH', None)
