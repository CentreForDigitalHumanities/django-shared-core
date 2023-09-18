"""
Adapted from django-encrypted-model-fields by
"""
from __future__ import unicode_literals

import django.db
import django.db.models as django_models
from django.core import validators
from django.utils.functional import cached_property

from .crypter import encrypt_str
from .mixin import EncryptedMixin

__all__ = ['EncryptedCharField', 'EncryptedBooleanField',
           'EncryptedBigIntegerField', 'EncryptedTextField',
           'EncryptedDateField', 'EncryptedDateTimeField',
           'EncryptedEmailField', 'EncryptedIntegerField',
           'EncryptedNullBooleanField', 'EncryptedNumberMixin',
           'EncryptedPositiveIntegerField',
           'EncryptedPositiveSmallIntegerField',
           'EncryptedSmallIntegerField', ]


class EncryptedCharField(EncryptedMixin, django_models.CharField):
    pass


class EncryptedTextField(EncryptedMixin, django_models.TextField):
    pass


class EncryptedDateField(EncryptedMixin, django_models.DateField):
    pass


class EncryptedDateTimeField(EncryptedMixin, django_models.DateTimeField):
    pass


class EncryptedEmailField(EncryptedMixin, django_models.EmailField):
    pass


class EncryptedBooleanField(EncryptedMixin, django_models.BooleanField):

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value
        if value is True:
            value = '1'
        elif value is False:
            value = '0'

        # decode the encrypted value to a unicode string, else this breaks in pgsql
        return encrypt_str(str(value)).decode('utf-8')


class EncryptedNullBooleanField(EncryptedMixin,
                                django_models.BooleanField):
    """
    From Django 2.2+, using NullBooleanField is discouraged. Please use
    EncryptedBooleanField! This class is still present as it is used by
    migrations.
    This class has been modified to inherit from BooleanField, with null and
    blank always to True.

    TODO: Remove this once all migrations have been squashed
    """

    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value
        if value is True:
            value = '1'
        elif value is False:
            value = '0'

        # decode the encrypted value to a unicode string, else this breaks in pgsql
        return encrypt_str(str(value)).decode('utf-8')


class EncryptedNumberMixin(EncryptedMixin):
    max_length = 20

    @cached_property
    def validators(self):
        # Encrypted fields are stored as textfields, so they don't really have
        # min-max limits like normal numbers. Just don't go crazy ;)
        return []


class EncryptedIntegerField(EncryptedNumberMixin,
                            django_models.IntegerField):
    description = "An IntegerField that is encrypted before " \
                  "inserting into a database using the python cryptography " \
                  "library"
    pass


class EncryptedPositiveIntegerField(EncryptedNumberMixin,
                                    django_models.PositiveIntegerField):
    pass


class EncryptedSmallIntegerField(EncryptedNumberMixin,
                                 django_models.SmallIntegerField):
    pass


class EncryptedPositiveSmallIntegerField(EncryptedNumberMixin,
                                         django_models.PositiveSmallIntegerField):
    pass


class EncryptedBigIntegerField(EncryptedNumberMixin,
                               django_models.BigIntegerField):
    pass
