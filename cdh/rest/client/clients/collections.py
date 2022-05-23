from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import ConnectionError

from ._base import BaseClient, host_unreachable
from ..operations import Operations
from cdh.rest.exceptions import OperationNotEnabled
from ..logging import transaction_logger as logger


class CollectionClient(BaseClient):
    """Default API client for resources"""

    def __init__(self):
        super(CollectionClient, self).__init__()

        self.operation = None

    def contribute_to_class(self, cls, _):
        """This configures the client to the specific collection class"""
        meta = cls._meta
        self.path = meta.path
        self.path_variables = meta.path_variables
        self.meta = meta
        self.operation = meta.operation

        if not self.operation == Operations.get and \
                not self.operation == Operations.get_over_post:
            logger.warning(f"{repr(self)}: GET and GET_OVER_POST are "
                           f"both enabled. Will use GET_OVER_POST. Please "
                           f"don't do this.")

    def get(self, **kwargs):
        """Gets a collection from the API. Either over GET or GET_OVER_POST,
        depending on configuration.

        Any kwargs supplied, that are not used for path variables, will be sent
        to the API. In case of GET, these will be supplied as parameters. In
        case of GET_OVER_POST, these will be supplied in the POST body.

        :param kwargs: Any additional info to be sent.
        :return:
        """
        if not self.path:
            raise OperationNotEnabled

        method = self._http_client.get
        if self.operation == Operations.get_over_post:
            method = self._http_client.post

        url, kwargs = self._make_url(**kwargs)

        try:
            logger.info(f"GETting {url}")
            request = method(
                url,
                kwargs,
                headers=self._make_auth_headers(),
            )
        except ConnectionError as e:
            logger.warning(f"Host {url} unreachable")
            host_unreachable()
            return None

        if request.ok:
            logger.info(f"Data retrieved")
            return self.meta.collection(request.json())

        if request.status_code == 404:
            logger.warning(f"Data not found")
            raise ObjectDoesNotExist

        self._handle_api_error(request)

    def __str__(self):
        return '{} client for collection {}'.format(
            self.__class__.__name__,
            self.meta.resource.__class__.__name__
        )

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)



