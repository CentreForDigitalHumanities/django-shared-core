from ._base import ResourceCollectionMetaclass, TypeCollectionMetaclass


class _CollectionMixin:
    """This mixin can be used to provide common collection code,
    like iteration support and a nice __repr__ implementation. """
    __slots__ = ['_items']

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def __setitem__(self, key, value):
        raise Exception("'{}' is immutable!".format(self.__class__.__name__))

    def __str__(self):
        return '{} collection'.format(
            self.__class__.__name__
        )

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self._items))


class ResourceCollection(_CollectionMixin, metaclass=ResourceCollectionMetaclass):
    """This class can be extended to describe a JSON object collection.
    A resources collection does not have fields of its own, one needs to
    specify the resources contained in the collection instead. At the moment, a
    collection can only hold one type of resources and cannot hold different
    collections.

    A collection can be connected to an API endpoint by specifying the path
    at which this resources can be retrieved. This is done by setting the path
    variable in the inline Meta class.This is optional however.

    At the moment, only get operations are supported for collections. You can
    choose plain GET or emulate GET over a POST request for more security.

    Note: you are not able to change the contents of a collection, as this
    would imply you can update the collection in the API. This class have been
    locked down to discourage people from trying to do so.

    For a detailed overview of these operations, please see their corresponding
    client methods. (Found in client.py, or by calling help on Resource.client).

    Available Meta variables:
    - resources (required): The resources class contained in this collection
    - path (optional): Specifies the REST endpoint location for this resources.
      Required for client operations. One might leave this unconfigured if the
      resources in question is part of a different resources/collection and does
      not have it's own endpoint.
      Please note that the API host will be joined to the path. Please specify
      a path relative to the host value supplied in settings.py
    - path_variables (optional): A list of variable names that are to be
      included in the path. If a variable name corresponds to a field name, the
      value of said field will be used, otherwise the value will be retrieved
      from the kwargs of the client method call.
      To specify where in the path these variables should be used, one can add
      '{variable_name}' in the path variable. For example:

      ::code: python

        class Meta:
            path = "/item/{pk}/"
            path_variables = ['pk']

    - operation (optional): Whether to use GET or GET_OVER_POST
      Defaults to GET. Does not affect anything if no path is specified.
    - client_class (optional): You can use this variable to specify a different
      client.
    """
    _meta = None

    def __init__(self, values, is_json=True):
        opts = self._meta

        if values is None:
            self._items = []
            return

        try:
            objects = list(values)

            if is_json:
                self._items = [opts.resource(**obj) for obj in objects if not
                isinstance(obj, int)]
            else:
                self._items = values
        except TypeError as e:
            raise e

    def to_api(self) -> list:
        """Returns the data in this collection as a list, to be converted to
        a form the API understands.

        :return: list
        """
        vals = [item.to_api() for item in self._items]
        return vals

    def __str__(self):
        return '{} collection for resources {}'.format(
            self.__class__.__name__,
            self._meta.resource.__class__.__name__
        )


class _TypeCollection(_CollectionMixin, metaclass=TypeCollectionMetaclass):
    """
    Base class for collections of basic types. (Read: a JSON list of
    strings|booleans|integers|etc)
    """
    type = None
    _meta = None

    def __init__(self, values, is_json=True):
        if values is None:
            self._items = []
            return

        try:
            objects = list(values)

            if is_json:
                self._items = [self.type(obj) for obj in objects if not
                               isinstance(obj, int)]
            else:
                self._items = values
        except TypeError as e:
            raise e

    def to_api(self) -> list:
        """Returns the data in this collection as a list, to be converted to
        a form the API understands.

        :return: list
        """
        return self._items


class StringCollection(_TypeCollection):
    type = str


class IntegerCollection(_TypeCollection):
    type = int


class FloatCollection(_TypeCollection):
    type = float
