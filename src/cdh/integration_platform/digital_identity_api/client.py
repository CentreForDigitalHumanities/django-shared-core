import cdh.integration_platform.settings as settings
from cdh.integration_platform.token_api import TokenService
from cdh.rest.client.clients import ResourceClient
from cdh.rest.client.logging import transaction_logger as logger


class DIAClient(ResourceClient):

    def __init__(self):
        super().__init__()

        self._host = settings.HOST

    def get(
        self,
        identity,
        identity_type,
        person=True,
        role=True,
        email=True,
        external_id=True,
        **kwargs
    ):
        def serializeBoolean(x):
            if x: return 'true'
            return 'false'
        kwargs['id_type'] = identity_type
        kwargs['id'] = identity
        kwargs['person'] = serializeBoolean(person)
        kwargs['role'] = serializeBoolean(role)
        kwargs['email'] = serializeBoolean(email)
        kwargs['external_id'] = serializeBoolean(external_id)
        return super().get(
            **kwargs
        )


    def _make_auth_headers(self) -> dict:
        credentials = TokenService.get_token()

        headers = {
            'Authorization': f"Bearer {credentials}",
            'Accept': "application/json"
        }
        logger.debug(f"Using headers: {headers}")

        return headers
