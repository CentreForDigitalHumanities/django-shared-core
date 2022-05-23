from django.core.exceptions import ImproperlyConfigured

from ..operations import Operations


class ResourceCollectionOptions:

    def __init__(self, meta, app_label):
        self.meta = meta
        self.collection = None
        self.resource = None
        self.path = None
        self.path_variables = []
        self.operation = Operations.get
        self.client_class = None
        self.app_label = app_label

    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)
        self.collection = cls

        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for key, value in meta_attrs.items():
                if key in self.__dict__:
                    self.__dict__[key] = value

            if not self.resource:
                raise ImproperlyConfigured(
                    "Collections need to have a resources configured in its "
                    "Meta class"
                )

        if not self.client_class:
            from ..clients import CollectionClient
            self.client_class = CollectionClient

    def __str__(self):
        return "{} for {}".format(self.__class__.__name__, self.collection)


class TypeCollectionOptions:

    def __init__(self, meta, app_label):
        self.meta = meta
        self.collection = None
        self.path = None
        self.path_variables = []
        self.operation = Operations.get
        self.client_class = None
        self.app_label = app_label

    def contribute_to_class(self, cls, name):
        setattr(cls, name, self)
        self.collection = cls

        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for key, value in meta_attrs.items():
                if key in self.__dict__:
                    self.__dict__[key] = value

        if not self.client_class:
            from ..clients import CollectionClient
            self.client_class = CollectionClient

    def __str__(self):
        return "{} for {}".format(self.__class__.__name__, self.collection)
