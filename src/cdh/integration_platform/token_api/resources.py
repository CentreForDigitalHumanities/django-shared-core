from cdh.rest.client import resources, fields, Operations
from .client import TokenClient
from .fields import ExpiryField


class Token(resources.Resource):
    class Meta:
        path = "/token"
        supported_operations = [Operations.get_over_post]
        client_class = TokenClient

    access_token = fields.TextField()

    scope = fields.TextField()

    token_type = fields.TextField()

    expires_in = ExpiryField()

    def revoke(self):
        self.client.revoke(self)

    def __str__(self):
        return '<{} ({})>'.format(
            self.__class__.__name__,
            self.access_token
        )
