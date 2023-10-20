from django.contrib.auth.models import AnonymousUser
from threading import local

_thread_locals = local()


def _do_set_current_user(user_fun):
    setattr(_thread_locals, 'user', user_fun.__get__(user_fun, local))


def _set_current_user(user=None):
    """
    Sets current user in local thread.
    Can be used as a hook e.g. for shell jobs (when request object is not
    available).
    """
    _do_set_current_user(lambda self: user)


def _do_set_current_request(request_fun):
    setattr(_thread_locals, 'request', request_fun.__get__(request_fun, local))


def _set_current_request(request=None):
    """
    Sets current user in local thread.
    Can be used as a hook e.g. for shell jobs (when request object is not
    available).
    """
    _do_set_current_request(lambda self: request)


class ThreadLocalUserMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        try:
            response = self.get_response(request)
        except Exception as e:
            self.process_exception(request, e)
            raise
        return self.process_response(request, response)

    def process_request(self, request):
        _do_set_current_request(lambda self: request)

    def process_response(self, request, response):
        # Clear the local cache, just to be sure it won't leak
        _do_set_current_request(lambda self: None)
        return response

    def process_exception(self, request, exception):
        # Clear the local cache, just to be sure it won't leak
        _do_set_current_request(lambda self: None)


def get_current_session():
    current_request = getattr(_thread_locals, 'request', None)
    if callable(current_request):
        return current_request().session

    if current_request is None:
        return None

    return current_request.session


def get_current_request():
    current_request = getattr(_thread_locals, 'request', None)
    if callable(current_request):
        return current_request()

    return current_request


def get_current_user():
    current_request = getattr(_thread_locals, 'request', None)
    if callable(current_request):
        return current_request().user

    if current_request is None:
        return None

    return current_request.user


def get_current_authenticated_user():
    current_user = get_current_user()
    if isinstance(current_user, AnonymousUser):
        return None
    return current_user
