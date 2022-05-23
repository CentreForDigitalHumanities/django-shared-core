import inspect
import copy

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from .options import TypeCollectionOptions, ResourceCollectionOptions
from ..registry import registry


class _CollectionBaseMetaclass(type):
    """
    Base class for the collection metaclasses. It is similar to the
    ResourceMetaclass. However, this class overrides _options to None in order
    to discourage programmers from using this class directly. This should be set
    on every extension of this metaclass.
    """
    _options = None

    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__

        parents = [b for b in bases if isinstance(b, _CollectionBaseMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attrs)

        module = attrs.pop('__module__')
        new_attrs = {
            '__module__': module
        }
        classcell = attrs.pop('__classcell__', None)
        if classcell is not None:
            new_attrs['__classcell__'] = classcell
        new_class = super_new(mcs, name, bases, new_attrs)
        attr_meta = attrs.pop('Meta', None)

        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        app_label = None

        # Look for an application configuration to attach the model to.
        app_config = apps.get_containing_app_config(module)

        if getattr(meta, 'app_label', None) is None:
            if app_config is None:
                raise RuntimeError(
                    "resources class %s.%s doesn't declare an explicit "
                    "app_label and isn't in an application in "
                    "INSTALLED_APPS." % (module, name)
                )

            else:
                app_label = app_config.label

        meta = new_class._get_options_class()(meta, app_label)
        meta.contribute_to_class(new_class, '_meta')

        for parent in parents:
            if hasattr(parent, '_meta') and parent._meta:
                for field, value in parent._meta.fields.items():
                    if field not in attrs:
                        attrs[field] = copy.copy(value)

        if 'client' not in attrs:
            new_class.client = meta.client_class()
            new_class.client.contribute_to_class(new_class, 'client')

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        new_class.register_class()

        return new_class

    def _get_options_class(cls):
        if cls._options is None:
            raise ImproperlyConfigured(
                "{} has no _options defined! Either the programmer forgot to "
                "set it, or you are using a metaclass you shouldn't be "
                "using.".format(cls.__class__.__name__)
            )

        return cls._options

    def register_class(cls):
        registry.register_collection(cls._meta.app_label, cls)

    def add_to_class(cls, name: str, value: object) -> None:
        """This either runs a class' contribute_to_class method, or adds the
        object to the class as a class attribute.
        """
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ResourceCollectionMetaclass(_CollectionBaseMetaclass):
    """Metaclass for resources collections.
    """
    _options = ResourceCollectionOptions


class TypeCollectionMetaclass(_CollectionBaseMetaclass):
    """Metaclass for type collections.
    """
    _options = TypeCollectionOptions

