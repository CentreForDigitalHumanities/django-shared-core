from base64 import b64encode

import cdh.integration_platform.settings as settings
from cdh.rest.client.clients import ResourceClient
from cdh.rest.client.logging import transaction_logger as logger


class TokenClient(ResourceClient):

    def __init__(self):
        super().__init__()

        self._host = settings.HOST
        self._consumer_key = settings.DIGITAL_IDENTITY_API_CREDENTIALS['key']
        self._consumer_secret = settings.DIGITAL_IDENTITY_API_CREDENTIALS['secret']


    def get(self, **kwargs):
        return super().get(
            grant_type="client_credentials",
            **kwargs
        )

    def _make_auth_headers(self) -> dict:
        credentials = b64encode(
            f"{self._consumer_key}:{self._consumer_secret}".encode()
        ).decode("utf-8")

        headers = {
            'Authorization': f"Basic {credentials}"
        }
        logger.debug(f"Using headers: {headers}")

        return headers
