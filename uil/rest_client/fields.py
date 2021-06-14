import collections
from abc import ABC, abstractmethod
from datetime import date, datetime, time
from functools import total_ordering
from typing import Union

import itertools
from backports.datetime_fromisoformat import MonkeyPatch
from django.core import exceptions, validators
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from uil.rest_client.collections.collections import ResourceCollection, _TypeCollection
from uil.rest_client.resources import Resource
from uil.rest_client.registry import registry
from uil.rest_client.logging import field_logger as logger

MonkeyPatch.patch_fromisoformat()


@total_ordering
class _BaseField(ABC):
    """Abstract class containing the bulk of the field code"""

    creation_counter = 0

    default_error_messages = {
        'invalid_choice': _('Value %(value)r is not a valid choice.'),
        'null': _('This field cannot be null.'),
        'blank': _('This field cannot be blank.'),
        'unique': _('%(model_name)s with this %(field_label)s '
                    'already exists.'),
        # Translators: The 'lookup_type' is one of 'date', 'year' or 'month'.
        # Eg: "Title must be unique for pub_date year"
        'unique_for_date': _("%(field_label)s must be unique for "
                             "%(date_field_label)s %(lookup_type)s."),
    }
    empty_values = list(validators.EMPTY_VALUES)
    default_validators = []

    def __init__(self, verbose_name: str = None, default: object = None,
                 choices: object = None, name: str = None,
                 null: bool = False, blank: bool = False,
                 error_messages: dict = None, validators: tuple = ()):
        """
        A field contains data within a REST resources.

        :param verbose_name: A code friendly name for this field, defaults to the variable name
        :param default: A default value to be used when no value is given
        :param choices: Optional, used to restrict the values in this field
        :param name: A human friendly name for this field, defaults to the variable name
        :param null: If this field can be null
        :param blank: If this field can be left blank
        :param error_messages: Any custom error messages
        :param validators: Any custom validators
        """
        self.name = name
        self.verbose_name = verbose_name
        self.resource = None

        self.default = default

        if isinstance(choices, collections.Iterator):
            choices = list(choices)
        self.choices = choices or []
        self.null = null
        self.blank = blank

        self._validators = list(validators)

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self._error_messages = error_messages  # Store for deconstruction later
        self.error_messages = messages

        _BaseField.creation_counter += 1
        self.creation_counter = _BaseField.creation_counter

    def set_attributes_from_name(self, name: str) -> None:
        if not self.name:
            self.name = name

        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')

    def contribute_to_class(self, cls: Resource, name: str) -> None:
        """
        Register the field with the model class it belongs to.

        If private_only is True, create a separate instance of this field
        for every subclass of cls, even if cls is not an abstract model.
        """
        self.set_attributes_from_name(name)
        self.resource = cls
        cls._meta.add_field(self)

    @cached_property
    def validators(self) -> list:
        """
        Some validators can't be created at field initialization time.
        This method provides a way to delay their creation until required.
        """
        return list(itertools.chain(self.default_validators, self._validators))

    def run_validators(self, value: object) -> None:
        if value in self.empty_values:
            return

        errors = []
        for v in self.validators:
            try:
                v(value)
            except exceptions.ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)

    def validate(self, value: object) -> None:
        """
        Validate value and raise ValidationError if necessary. Subclasses
        should override this to provide validation logic.
        """
        if self.choices and value not in self.empty_values:
            for option_key, option_value in self.choices:
                if isinstance(option_value, (list, tuple)):
                    # This is an optgroup, so look inside the group for
                    # options.
                    for optgroup_key, optgroup_value in option_value:
                        if value == optgroup_key:
                            return
                elif value == option_key:
                    return
            raise exceptions.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={
                    'value': value
                },
            )

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'],
                                             code='null')

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(self.error_messages['blank'],
                                             code='blank')

    def clean(self, value: object) -> object:
        """
        Convert the value's type and run validation. Validation errors
        from to_python() and validate() are propagated. Return the correct
        value if no error is raised.
        """
        logger.debug(f"{repr(self)}: Cleaning {repr(value)}")
        value = self.to_python(value)
        logger.debug(f"{repr(self)}: Resolved to {repr(value)}")
        self.validate(value)
        self.run_validators(value)
        logger.debug(f"{repr(self)}: Validated value")
        return value

    def __eq__(self, other: object) -> bool:
        # Needed for @total_ordering
        if isinstance(other, _BaseField):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, _BaseField):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash(self.creation_counter)

    def __str__(self):
        resource = self.resource
        return '{}.{}'.format(resource.__class__.__name__, self.name)

    def __repr__(self):
        path = '{}.{}'.format(self.__class__.__module__,
                              self.__class__.__qualname__)
        name = getattr(self, 'name', None)
        if name is not None:
            return '<{}: {}>'.format(path, name)
        return '<{}>'.format(path)

    def to_python(self, value: object) -> object:
        """Returns the python version of the supplied value. By default, it's
        the same as the value supplied, but this can be overridden by fields
        to provide a conversion to a different datatype
        """
        logger.debug(f"{repr(self)}: serializing to python: {repr(value)}")
        return value

    @abstractmethod
    def to_api(self, value: object) -> object:
        """This method should return a python datatype that can be deserialized
        properly primarily by the json module.
        """
        logger.debug(f"{repr(self)}: deserializing to api: {repr(value)}")
        pass


class BasicTypeField(_BaseField):
    """Abstract class used by simple types like bool, str and int. """
    basic_type = None

    def __init__(self, *args, **kwargs):
        super(BasicTypeField, self).__init__(*args, **kwargs)

    def to_api(self, value: object) -> basic_type:
        """Cleans and validates values before casting them to the right
        API type
        """
        logger.debug(f"{repr(self)}: deserializing to api: {repr(value)}")
        if value is None:
            return value
        try:
            value = self.clean(value)
            return self.basic_type(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={
                    'value': value
                },
            )


class IntegerField(BasicTypeField):
    """Field containing an int"""
    basic_type = int


class FloatField(BasicTypeField):
    """Field containing a float"""
    basic_type = float


class TextField(BasicTypeField):
    """Field containing a string"""
    basic_type = str


class BoolField(BasicTypeField):
    """Field containing a boolean"""
    basic_type = bool


class DateTimeField(_BaseField):
    """Field that parses a ISO-formatted datetime-string"""
    type = datetime

    def to_python(self, value: str) -> type:
        logger.debug(f"{repr(self)}: serializing to python: {repr(value)}")
        if value is None:
            return value

        if isinstance(value, self.type):
            return value

        try:
            # Fix the fact that datetime.fromisoformat doesn't adhere to iso
            # 8601 properly when 'Z(ulu)' is used instead of '+00:00'
            if value[-1] == 'Z':
                value = "{}+00:00".format(value[:-1])

            return self.type.fromisoformat(value)
        except (TypeError, ValueError) as e:
            raise exceptions.ValidationError(
                "Some error!",
                code='invalid',
                params={
                    'value': value
                },
            )

    def to_api(self, value: type) -> str:
        logger.debug(f"{repr(self)}: deserializing to api: {repr(value)}")
        value = self.clean(value)

        if value is None:
            return None

        return value.isoformat()


class DateField(DateTimeField):
    """Field that parses a ISO-formatted date-string"""
    type = date


class TimeField(DateTimeField):
    """Field that parses a ISO-formatted date-string"""
    type = time


class CollectionField(_BaseField):
    """Field referencing a collection"""

    def __init__(self, collection, **kwargs):
        """

        :param collection: The collection to use
        :param kwargs: See ::class:BaseField for other options
        """
        super(CollectionField, self).__init__(**kwargs)
        self.collection = collection

    def to_api(self, value: Union[ResourceCollection, _TypeCollection]):
        """Transforms the collection into a list, and chains the call to it's
        children.
        """
        logger.debug(f"{repr(self)}: deserializing to api: {repr(value)}")

        if value is None or value in self.empty_values:
            return []

        return value.to_api()

    def to_python(self, value: list):
        """Creates a collection object from the supplied list"""
        cls = self.collection
        logger.debug(f"{repr(self)}: serializing to python: {repr(value)}")

        if isinstance(cls, str):
            app_label = self.resource._meta.app_label

            if len(cls.split('.')) == 2:
                app_label, cls = cls.split('.')

            cls = registry.get_collection(app_label, cls)

        return cls(value)


class ResourceField(_BaseField):
    """Field referencing a resources"""

    def __init__(self, resource, **kwargs):
        """
        :param resource: The resources to use
        :param kwargs: See ::class:BaseField for other options
        """
        super(ResourceField, self).__init__(**kwargs)
        self.resource_class = resource

    def to_api(self, value: Resource):
        """Transforms the resources into a dict, and chains the call to it's
        children.
        """
        logger.debug(f"{repr(self)}: deserializing to api: {repr(value)}")

        if value is None or value in self.empty_values:
            if not self.null or not self.blank:
                raise ValueError('Cannot serialize null, as it\'s not allowed!')
            return None

        if isinstance(value, int):
            return value

        return value.to_api()

    def to_python(self, value: dict):
        """Creates a resources object from the supplied dict"""
        cls = self.resource_class
        logger.debug(f"{repr(self)}: serializing to python: {repr(value)}")

        if value is None:
            if not self.null or not self.blank:
                raise ValueError("Tried to serialize null, but it's not "
                                 "allowed")
            return value

        if isinstance(cls, str):
            app_label = self.resource._meta.app_label

            if len(cls.split('.')) == 2:
                app_label, cls = cls.split('.')
            cls = registry.get_resource(app_label, cls)

        if isinstance(value, int):
            return value

        return cls(**value)
