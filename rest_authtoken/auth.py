from base64 import urlsafe_b64decode

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
            msg = 'invalid auth header, No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'invalid auth token'
            raise AuthenticationFailed(msg)

        try:
            token = urlsafe_b64decode(auth[1])
        except ValueError:
            msg = 'invalid auth token'
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    def authenticate_credentials(self, token: bytes, request=None):
        """
        Authenticate the token with optional request for context.
        """
        user = AuthToken.get_user_for_token(token)

        if user is None:
            raise AuthenticationFailed('invalid auth token')

        if not user.is_active:
            raise AuthenticationFailed('invalid auth token')

        return user, token

    def authenticate_header(self, request):
        return 'Token'
