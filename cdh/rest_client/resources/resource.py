from .base import ResourceMetaclass


class Resource(metaclass=ResourceMetaclass):
    """This class can be extended to describe a REST resources.
    It's inspired by Django's models, and as such, configuring the resources
    is done in a similar manner. Each resources should be defined by creating
    class that extends this one.

    In this class, one can define it's fields by creating class attributes
    containing the appropriate fields (defined in fields.py).

    A resources can be connected to an API endpoint by specifying the path
    at which this resources can be retrieved. This is done by setting the path
    variable in the inline Meta class. This is optional however.

    One might also want to limit the available operations for this resources to
    reflect the API's capabilities. This is done by supplying a list of
    supported operations in the supported_operations variable of the Meta class.

    For a detailed overview of these operations, please see their corresponding
    client methods. (Found in client.py, or by calling help on Resource.client).

    Available Meta variables:
    - path (optional): Specifies the REST endpoint location for this resources.
      Required for client operations. One might leave this unconfigured if the
      resources in question is part of a different resources/collection and does
      not have it's own endpoint.
      Please note that the API host will be joined to the path. Please specify
      a path relative to the host value supplied in settings.py
    - path_variables (optional): A list of variable names that are to be
      included in the path. If a variable name corresponds to a field name, the
      value of said field will be used, otherwise the value will be retrieved
      from the kwargs of the client method call. (Note: if kwargs are used, they
      will not be used in the request body/parameters)
      To specify where in the path these variables should be used, one can add
      '{variable_name}' in the path variable. For example:

      ::code: python

        class Meta:
            path = "/item/{pk}/"
            path_variables = ['pk']

    - identifier_field (optional): A string containing the name of the field
      that represents a identifier for this resources. Only used in the default
      __str__ implementation. It's just a helpful thing to have when debugging.
    - supported_operations (optional): A list of operation the API supports for
      this resources. Does not affect anything if no path is specified.
      Defaults to all operations.
    - client_class (optional): You can use this variable to specify a different
      client.
    - default_return_resource (optional): You can specify a different resources
      class that the API sends back on PUT operations. This is a default value,
      and can be overridden on the operation call itself. See the client
      documentation for more info. If none is supplied, a boolean is returned
      instead.
    """

    _meta = None

    def __init__(self, **kwargs):
        opts = self._meta

        for name, field in opts.fields.items():
            if name in kwargs:
                cleaned_value = field.clean(kwargs[name])
                setattr(self, name, cleaned_value)
            else:
                setattr(self, name, field.default)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)

    def __str__(self):
        pk_value = "[unknown]"
        if self._meta.identifier_field:
            pk_value = getattr(self, self._meta.identifier_field, pk_value)
        return '{} object ({})'.format(self.__class__.__name__, pk_value)

    def to_api(self) -> dict:
        """Returns the data in this resources as a dict, to be converted to
        a form the API understands.

        :return: dict
        """
        return {
            name: field.to_api(getattr(self, name)) for (name, field) in
            self._meta.fields.items()
        }

    def put(self, return_resource=None, as_json=False, **kwargs):
        """Proxy method that autofills the obj parameter"""
        return self.client.put(
            self,
            return_resource=return_resource,
            as_json=as_json,
            **kwargs
        )

    def delete(self, **kwargs):
        """Proxy method that autofills the obj parameter"""
        self.client.delete(self, **kwargs)