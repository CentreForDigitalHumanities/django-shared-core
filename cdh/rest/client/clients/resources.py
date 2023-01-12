from django.core.exceptions import ImproperlyConfigured
from requests.exceptions import ConnectionError

from ._base import BaseClient, host_unreachable
from ..registry import registry
from ..operations import Operations
from cdh.rest.exceptions import OperationNotEnabled
from ..logging import transaction_logger as logger


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
                logger.debug(f"{repr(self)}: GET enabled")
            elif operation == Operations.get_over_post:
                self._get_over_post_enabled = True
                logger.debug(f"{repr(self)}: GET over POST enabled")
            elif operation == Operations.delete:
                self._delete_enabled = True
                logger.debug(f"{repr(self)}: DELETE enabled")
            elif operation == Operations.put:
                self._put_enabled = True
                logger.debug(f"{repr(self)}: PUT enabled")
            else:
                raise NotImplementedError(
                    "Operation not implemented! Please add operation '{}' "
                    "support!".format(
                        operation.name
                    )
                )

        if self._get_enabled and self._get_over_post_enabled:
            logger.warning(f"{repr(self)}: GET and GET_OVER_POST are "
                           f"both enabled. Will use GET_OVER_POST. Please "
                           f"don't do this.")

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
            logger.info(f"{repr(self)}: GETting {url}")
            request = method(
                url,
                kwargs,
                headers=self._make_auth_headers(), # TODO use auth param instead
            )
        except ConnectionError:
            logger.warning(f"{repr(self)}: Host {url} unreachable")
            host_unreachable()
            return None

        if request.ok:
            logger.info(f"{repr(self)}: Data retrieved")
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
        logger.debug(f"{repr(self)}: Preparing PUT transaction")
        if not self._put_enabled:
            raise OperationNotEnabled

        if not return_resource:
            logger.debug(f"{repr(self)}: No return resource specified, falling"
                         f" back to default return response")
            return_resource = self.meta.default_return_resource

        if isinstance(return_resource, str):
            app_label = obj._meta.app_label
            logger.debug(f"{repr(self)}: Resolving return resource")

            if len(return_resource.split('.')) == 2:
                app_label, return_resource = return_resource.split('.')
            return_resource = registry.get_resource(app_label, return_resource)

        if not as_json:
            logger.debug(f"{repr(self)}: No as_json specified, falling back on default")
            as_json = self._send_as_json

        url, kwargs = self._make_url(obj, **kwargs)

        try:
            request_kwargs = {
                'params': kwargs,
                'headers': self._make_auth_headers(),
            }
            logger.info(f"{repr(self)}: PUTting {url}")

            if as_json:
                request_kwargs['json'] = obj.to_api()
            else:
                request_kwargs['data'] = obj.to_api()

            logger.debug(f"{repr(self)}: {request_kwargs}")

            request = self._http_client.post(
                url,
                **request_kwargs
            )
        except ConnectionError:
            logger.warning(f"{repr(self)}: Host {url} unreachable")
            host_unreachable()
            return False

        if request.ok:
            if return_resource:
                logger.info(f"{repr(self)}: Data retrieved")
                return return_resource(**request.json())

            logger.info(f"{repr(self)}: Transaction successful")
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
            logger.info(f"{repr(self)}: DELETEing {url}")
            request = self._http_client.delete(
                url,
                params=kwargs,
                headers=self._make_auth_headers(),
            )
        except ConnectionError:
            logger.warning(f"{repr(self)}: Host {url} unreachable")
            host_unreachable()
            return False

        return request.ok

    def __str__(self):
        return '{} for {}'.format(
            self.__class__.__name__,
            self.meta.resource.__name__
        )

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)

