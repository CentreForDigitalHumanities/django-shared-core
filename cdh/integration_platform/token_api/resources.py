from cdh.rest.client import resources, fields, Operations
from .client import TokenClient


class Token(resources.Resource):
    class Meta:
        path = "/token"
        supported_operations = [Operations.get_over_post]
        client_class = TokenClient

    access_token = fields.TextField()

    scope = fields.TextField()

    token_type = fields.TextField()

    expires_in = fields.IntegerField()
