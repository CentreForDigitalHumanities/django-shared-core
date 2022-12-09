from pprint import pformat

from cdh.rest.client import resources, fields, Operations
from .client import DIAClient


class EmailAddress(resources.Resource):

    employee = fields.TextField(null=True, blank=True)
    student = fields.TextField(null=True, blank=True)

    def __str__(self):
        return pformat({
            'employee': self.employee,
            'student': self.student,
        })


class Communication(resources.Resource):

    email = fields.ResourceField(EmailAddress)  # Specs says this is
    # emailAddress, not email

    def __str__(self):
        return pformat({
            'email': self.email
        })


class Identity(resources.Resource):
    class Meta:
        path = "/api/digitalidentity/v2/person/{id_type}/{id}"
        path_variables = ["id_type", "id"]
        supported_operations = [Operations.get]
        client_class = DIAClient

    solisId = fields.TextField()

    status = fields.TextField(null=True, blank=True) # The api seems to return strings of
    # 'null' here, but not with prefix

    initials = fields.TextField()

    givenName = fields.TextField()

    prefix = fields.TextField(null=True, blank=True)

    # TODO: roles, external_id

    surname = fields.TextField()

    communication = fields.ResourceField(Communication)

    def __str__(self):
        return pformat({
            'solisId': self.solisId,
            'status': self.status,
            'initials': self.initials,
            'givenName': self.givenName,
            'prefix': self.prefix,
            'surname': self.surname,
            'communication': self.communication,
        })
