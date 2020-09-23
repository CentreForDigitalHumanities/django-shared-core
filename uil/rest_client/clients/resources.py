from django.core.exceptions import ImproperlyConfigured
from requests.exceptions import ConnectionError

from ._base import BaseClient, host_unreachable
from ..registry import registry
from ..operations import Operations
from ..exceptions import OperationNotEnabled


class ResourceClient(BaseClient):
    """Default API client for resources"""

    def __init__(self):
        super(ResourceClient, self).__init__()

        self.supported_operations = None
        self._get_enabled = False
        self._get_over_post_enabled = False
        self._delete_enabled = False
        self._update_enabled = False
        self._put_enabled = False
        self._send_as_json = False

    def contribute_to_class(self, cls, _) -> None:
        """This configures the client to the specific resources class"""
        meta = cls._meta
        self.path = meta.path
        self.path_variables = meta.path_variables
        self.meta = meta
        self.supported_operations = meta.supported_operations
        self._send_as_json = meta.default_send_as_json

        # The rest is irrelevant if we don't have a path configured
        if not self.path:
            return

        # Looping like this feels faster than 5 'x in self.supported_operations'
        # calls
        for operation in self.supported_operations:
            if not isinstance(operation, Operations):
                raise ImproperlyConfigured("Invalid operation supplied!")

            if operation == Operations.get:
                self._get_enabled = True
            elif operation == Operations.get_over_post:
                self._get_over_post_enabled = True
            elif operation == Operations.delete:
                self._delete_enabled = True
            elif operation == Operations.put:
                self._put_enabled = True
            else:
                raise NotImplementedError(
                    "Operation not implemented! Please add operation '{}' "
                    "support!".format(
                        operation.name
                    )
                )

        if self._get_enabled and self._get_over_post_enabled:
            raise ImproperlyConfigured(
                "Resources cannot have both get and get_over_post configured!")

    def get(self, **kwargs):
        """Gets a resources from the API. Either over GET or GET_OVER_POST,
        depending on configuration.

        Any kwargs supplied, that are not used for path variables, will be sent
        to the API. In case of GET, these will be supplied as parameters. In
        case of GET_OVER_POST, these will be supplied in the POST body.

        :param kwargs: Any additional info to be sent.
        :return:
        """
        if not self._get_enabled and not self._get_over_post_enabled:
            raise OperationNotEnabled

        method = self._http_client.get
        if self._get_over_post_enabled:
            method = self._http_client.post

        url, kwargs = self._make_url(**kwargs)

        try:
            request = method(
                url,
                kwargs,
                headers=self._make_auth_headers(),
            )
        except ConnectionError:
            host_unreachable()
            return None

        if request.ok:
            return self.meta.resource(**request.json())

        self._handle_api_error(request)

    def put(self, obj, return_resource=None, as_json=None, **kwargs):
        """Posts a resources to the API. Please note that while it's called put,
        the actual HTTP method used is POST. PUT is not as supported as POST in
        many API frameworks, including Django.

        Any kwargs supplied, that are not used for path variables, will be sent
        to the API as parameters.

        Update/creation/update behaviour is up to the API.

        :param obj: The resources to be sent in the POST body.
        :param return_resource: An optional class that describes the resources
        that the server returns as a response. (A default can be specified on
        a resources level)
        :param as_json: If the request's json argument should be used over
        'data'. Defaults to False. When True, the client will send the data
        as a JSON string to the server. If False, it will instead encode the
        data as 'multipart/form-data'. JSON is more flexible, as it allows
        for nested data structures.
        :param kwargs: Any additional info to be sent.
        :return: A return_response instance, or a Boolean (False indicated
        a connection error)
        """
        if not self._put_enabled:
            raise OperationNotEnabled

        if not return_resource:
            return_resource = self.meta.default_return_resource

        if isinstance(return_resource, str):
            app_label = obj._meta.app_label

            if len(return_resource.split('.')) == 2:
                app_label, return_resource = return_resource.split('.')
            return_resource = registry.get_resource(app_label, return_resource)

        if not as_json:
            as_json = self._send_as_json

        url, kwargs = self._make_url(obj, **kwargs)

        try:
            request_kwargs = {
                'params': kwargs,
                'headers': self._make_auth_headers(),
            }

            if as_json:
                request_kwargs['json'] = obj.to_api()
            else:
                request_kwargs['data'] = obj.to_api()

            request = self._http_client.post(
                url,
                **request_kwargs
            )
        except ConnectionError:
            host_unreachable()
            return False

        if request.ok:
            if return_resource:
                return return_resource(**request.json())

            return True

        self._handle_api_error(request)

    def delete(self, obj=None, **kwargs):
        """Performs a delete operation.

        :param obj: A resources object to retrieve path variable values from
        :param kwargs: Any additional http parameters to sent
        :return: a bool indicating if the request was executed successfully
        """
        if not self._delete_enabled:
            raise OperationNotEnabled

        url, kwargs = self._make_url(obj, **kwargs)

        try:
            request = self._http_client.delete(
                url,
                params=kwargs,
                headers=self._make_auth_headers(),
            )
        except ConnectionError:
            host_unreachable()
            return False

        return request.ok

    def __str__(self):
        return '{} client for resources {}'.format(
            self.__class__.__name__,
            self.meta.resource.__class__.__name__
        )

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)

