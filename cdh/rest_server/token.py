import jwt

import cdh.rest_server.settings as settings
from .token_algorithms import Algorithms


class JwtToken:

    def __init__(self):
        self._algorithm = None
        self._encode_key = None
        self._decode_key = None

        self._algorithm = Algorithms(settings.JWT_ALGORITHM)

        if self._algorithm == Algorithms.RSA:
            with open(settings.JWT_PRIVATE_KEY, 'r') as key_file:
                self._encode_key = key_file.read()

            with open(settings.JWT_PUBLIC_KEY, 'r') as key_file:
                self._decode_key = key_file.read()

        elif self._algorithm == Algorithms.SHA:
            self._encode_key = settings.JWT_SECRET_KEY
            self._decode_key = settings.JWT_SECRET_KEY

    def validate_token(self, token):
        try:
            decoded = jwt.decode(
                token,
                self._decode_key,
                algorithms=[self._algorithm.value]
            )
        except jwt.DecodeError:
            return None

        return decoded

    def make_token(self, user):
        payload = {
            "pk": user.pk
        }

        return jwt.encode(
            payload,
            self._encode_key,
            algorithm=self._algorithm.value
        )


JwtToken = JwtToken()
