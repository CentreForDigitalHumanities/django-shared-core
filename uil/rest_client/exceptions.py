from requests import Response


class ApiError(Exception):
    """General API errors"""

    def __init__(self, status_code, message, *args):
        super(ApiError, self).__init__(*args)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return 'ApiError ({}): {}'.format(self.status_code, self.message)

    def __repr__(self):
        return "<ApiError ({}): '{}'>".format(self.status_code, self.message)


class Forbidden(ApiError):

    def __init__(self, response: Response):
        super().__init__(
            response.status_code,
            "Forbidden for resource {}, using creds: {}".format(
                response.url,
                'Authorization' in response.request.headers
            )
        )
        self.response = response


class Unauthorized(ApiError):

    def __init__(self, response: Response):
        super().__init__(
            response.status_code,
            "Unauthorized for resource {}, using creds: {}".format(
                response.url,
                'Authorization' in response.request.headers
            )
        )
        self.response = response


class OperationNotEnabled(Exception):
    """Thrown when a call was made to a resources/collection operation that was
    not enabled by it's config."""