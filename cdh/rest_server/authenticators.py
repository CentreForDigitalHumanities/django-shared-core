from rest_framework import authentication

from .settings import USER_MODEL
from .token import JwtToken


class JwtAuthentication(authentication.TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, key):
        decoded = JwtToken.validate_token(key)

        user = USER_MODEL.objects.get(pk=decoded['pk'])

        user.is_authenticated = True

        return (user, decoded)
