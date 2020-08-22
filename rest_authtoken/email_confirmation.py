from base64 import urlsafe_b64encode

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from .models import EmailConfirmationToken
from .settings import REGISTRATION_EMAIL, \
    REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD


def send_confirmation_email(user: get_user_model()):
    """
    Send a confirmation email to the specified user.
    May only be called for a user object with an unverified email address.
    """
    assert not getattr(
        user, REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD), 'email already confirmed'

    token = urlsafe_b64encode(
        EmailConfirmationToken.create_token_for_user(user)).decode()

    path = reverse('rest_authtoken:confirm_email', args=(token,))
    url = REGISTRATION_EMAIL['BASE_URL'] + path

    message = REGISTRATION_EMAIL['MESSAGE'].format(
        username=user.username,
        url=url,
    )

    send_mail(
        REGISTRATION_EMAIL['SUBJECT'],
        message,
        REGISTRATION_EMAIL['FROM'],
        [user.email],
        fail_silently=False
    )
