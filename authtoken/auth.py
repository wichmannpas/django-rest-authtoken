from base64 import urlsafe_b64decode
import binascii

from django.utils.translation import ugettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .models import AuthToken


class AuthTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = _('Invalid auth token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid auth token.')
            raise AuthenticationFailed(msg)

        try:
            token = urlsafe_b64decode(auth[1])
        except ValueError:
            msg = _('Invalid auth token.')
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    def authenticate_credentials(self, token: bytes, request=None):
        """
        Authenticate the token with optional request for context.
        """
        user = AuthToken.get_user_for_token(token)

        if user is None:
            raise AuthenticationFailed(_('Invalid auth token.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return user, token

    def authenticate_header(self, request):
        return 'Token'
