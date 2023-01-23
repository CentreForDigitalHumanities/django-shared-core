from base64 import b64encode
from urllib.parse import urljoin

import cdh.integration_platform.settings as settings
from cdh.rest.client.clients import ResourceClient
from cdh.rest.client.logging import transaction_logger as logger
from cdh.rest.client.clients._base import host_unreachable


class TokenClient(ResourceClient):

    def __init__(self):
        super().__init__()

        self._host = settings.HOST
        self._consumer_key = settings.CONSUMER_CREDENTIALS['key']
        self._consumer_secret = settings.CONSUMER_CREDENTIALS['secret']

    def get(self, **kwargs):
        return super().get(
            grant_type="client_credentials",
            **kwargs
        )

    def revoke(self, token):

        if not isinstance(token, str):
            token = token.access_token

        method = self._http_client.post

        url = urljoin(self._host, "/revoke")

        try:
            logger.info(f"{repr(self)}: Revoking at {url}")
            request = method(
                url,
                {'token': token},
                headers=self._make_auth_headers(),
            )
        except ConnectionError:
            logger.warning(f"{repr(self)}: Host {url} unreachable")
            host_unreachable()
            return None

        if request.ok:
            logger.info(f"{repr(self)}: Token revoked")
            logger.debug(f"{repr(self)}: {request.content}")
            return True

        self._handle_api_error(request)

    def _make_auth_headers(self) -> dict:
        credentials = b64encode(
            f"{self._consumer_key}:{self._consumer_secret}".encode()
        ).decode("utf-8")

        headers = {
            'Authorization': f"Basic {credentials}"
        }
        logger.debug(f"Using headers: {headers}")

        return headers
