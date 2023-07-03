from datetime import datetime

from debug_toolbar.panels import Panel
from django.conf import settings


class DebugHttpClientWrapper:

    def __init__(self, original_client, data_object):
        self.original_client = original_client
        self.data_object = data_object

    def _wrapper(self, method, *args, **kwargs):
        try:
            original_method = getattr(self.original_client, method)
            result = original_method(*args, **kwargs)
            self.data_object.log_request(method, (args, kwargs), result)
            return result
        except Exception as e:
            raise e

    def get(self, *args, **kwargs):
        return self._wrapper('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._wrapper('post', *args, **kwargs)

    def update(self, *args, **kwargs):
        return self._wrapper('update', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._wrapper('delete', *args, **kwargs)


def get_to_api_wrapper(to_api_func, data_object):

    def wrapped_to_api(*args, **kwargs) -> dict:
        result = to_api_func(*args, **kwargs)
        data_object.log_serialization(result)
        return result

    return wrapped_to_api


def get_from_api_wrapper(from_api_func, data_object):

    def wrapped_from_api(*args, **kwargs) -> dict:
        result = from_api_func(*args, **kwargs)
        data_object.log_deserialization(result)
        return result

    return wrapped_from_api


class BaseData:
    def __init__(self, app_name, item):
        self.app_name = app_name
        self.item = item
        self.requests = []
        self.serializations = []
        self.deserializations = []

        if item.client is not None and not isinstance(item.client, DebugHttpClientWrapper):
            item.client._http_client = DebugHttpClientWrapper(item.client._http_client, self)

        if hasattr(item, 'to_api'):
            item.to_api = get_to_api_wrapper(item.to_api, self)

        if hasattr(item, 'from_api') and False:
            item.from_api = get_to_api_wrapper(item.from_api, self)

    def log_request(self, method, arguments, data):
        self.requests.append((method, datetime.now(), arguments, data))

    def log_serialization(self, data):
        self.serializations.append((datetime.now(), data))

    def log_deserialization(self, data):
        self.deserializations.append((datetime.now(), data))

    def name(self):
        return self.item.__name__

    def has_client(self):
        return self.item._meta.path is not None and len(self.item._meta.supported_operations) != 0


class ResourceData(BaseData):
    pass


class CollectionData(BaseData):
    pass


class RestClientPanel(Panel):
    name = 'REST Client'
    template = 'dev_tools/panels/resources.html'
    has_content = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = []
        self.collections = []

    @property
    def scripts(self):
        scripts = super().scripts
        return scripts

    def nav_title(self):
        return self.name

    def nav_subtitle(self):
        # TODO
        return f"{len(self.resources)} resources loaded"

    def title(self):
        return self.name

    def generate_stats(self, request, response):
        """
        Main panel view.
        """
        self.record_stats({
            'resources': self.resources,
            'collections': self.collections,
        })

    def enable_instrumentation(self):
        self.resources = []
        self.collections = []
        if 'cdh.rest' in settings.INSTALLED_APPS:
            from cdh.rest.client.registry import registry

            for app, resources in registry.resource_registry.items():
                for name, resource in resources.items():
                    self.resources.append(ResourceData(app, resource))

            for app, collections in registry.collection_registry.items():
                if app == "rest":
                    continue
                for name, collection in collections.items():
                    self.collections.append(CollectionData(app, collection))


    # @classmethod
    # def get_urls(cls):
    #     return urlpatterns


