from typing import Tuple
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from ..exceptions import *
from ..logging import transaction_logger as logger
from cdh.core.middleware import get_current_authenticated_user, \
    get_current_request, \
    get_current_session


class BaseClient:
    """
    This class provides common instance attributes and methods for both the
    Collection and Resource clients.
    """

    def __init__(self):
        self.path = None
        self.path_variables = []
        self.meta = None

        self._http_client = requests
        self._host = settings.API_HOST

    @staticmethod
    def _make_auth_headers() -> dict:
        """
        This class returns a dict of headers to be used for authentication.

        If there is no authenticated user, an empty dict will be returned

        :return:
        """
        headers = {}

        current_user = get_current_authenticated_user()
        if current_user:
            session = get_current_session()
            if 'token' in session:
                headers['Authorization'] = 'Bearer {}'.format(session['token'])

        logger.debug(f"Using headers: {headers}")

        return headers

    @staticmethod
    def _handle_api_error(request: requests.Response) -> None:
        """Common function to handle API errors
        :param request:
        :return:
        """
        if request.status_code == 404:
            logger.warning("Resource does not exist")
            raise ObjectDoesNotExist

        if request.status_code == 401:
            raise Unauthorized(request)

        if request.status_code == 403:
            raise Forbidden(request)

        raise ApiError(request.status_code, request.text)

    def _make_url(self, res=None, **kwargs) -> Tuple[str, dict]:
        """This method takes the resources path, uses string format to inject
        path variables and combines it with the host to create the full URI for
        the request

        :param res: A resources object to get path variable values from
        :param kwargs: All kwargs for this operation call, to get path variables
        :return: A fully qualified URI to be used in the http request
        """
        url = self.path
        logger.debug(f"Creating URL: {url}")
        if self.path_variables:
            values = {}
            for path_var in self.path_variables:
                if res and path_var in self.meta.fields:
                    value = getattr(res, path_var)
                    value = self.meta.fields[path_var].clean(value)
                    values[path_var] = value
                elif path_var in kwargs:
                    values[path_var] = kwargs.pop(path_var)
                else:
                    raise RuntimeError(
                        'No value found for path variable {}'.format(path_var)
                    )
            logger.debug(f"Using values: {values}")
            url = url.format(**values)

        return urljoin(self._host, url), kwargs


def host_unreachable():
    """This will add a error message, if one was not already added"""
    messages_lst = messages.get_messages(get_current_request())
    messages_lst = [message.message for message in messages_lst]
    message = _('api:host_unreachable')

    if message not in messages_lst:
        messages.error(get_current_request(), _('api:host_unreachable'))
