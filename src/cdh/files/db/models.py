import logging
import uuid

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from cdh.files.db import manager
from cdh.files.db.wrappers import FileWrapper


USE_CHAR32_UUIDS = getattr(settings, "USE_CHAR32_UUIDS", False,)
logger = logging.getLogger('cdh.files')


class _FileWrapperDict:
    """Instance-local dict. Normally you'd just set a var in your __init__,
    but Django models don't like custom __init__'s. """

    def __get__(self, instance, *args, **kwargs):
        if instance is None:
            return self

        if not hasattr(instance, '_file_wrapper_cache'):
            instance._file_wrapper_cache = {}

        return instance._file_wrapper_cache

    def __set__(self, instance, value):
        instance._file_wrapper_cache = value


class MySQLSafeUUIDField(models.UUIDField,):
    """
    Workaround class.

    Django 5.0 switched from DB column type for UUID's on MySQL/MariaDB.
    The standard UUIDField is not aware of this change, and will fail to
    insert UUID's into the char(32) columns. For applications that run into
    this problem, this UUID field is provided which respects the setting
    USE_CHAR32_UUIDS in settings.py to support older fields.

    Details: https://docs.djangoproject.com/en/6.0/releases/5.0/#migrating-existing-uuidfield-on-mariadb-10-7
    """

    def __init__(self, *args, **kwargs):
        self.use_char32_uuids = USE_CHAR32_UUIDS
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        if self.use_char32_uuids:
            return "char(32)"
        return super().db_type(connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if self.use_char32_uuids and type(value) is bytes:
            # A char32 UUID takes a good 'ol string, not bytes
            value = value.hex
        return value


class BaseFile(models.Model):
    class Meta:
        abstract = True

    objects = manager.FileManager()

    # Human-facing PK; Also acts as the filename on disk
    uuid = MySQLSafeUUIDField(
        "Universally Unique IDentifier",
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )

    original_filename = models.CharField(max_length=255)

    content_type = models.CharField(max_length=100)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_on = models.DateTimeField(auto_now_add=True)

    modified_on = models.DateTimeField(auto_now=True)

    _file_wrappers = _FileWrapperDict()

    @property
    def _num_child_instances(self):
        out = 0
        for related_object in self._meta.related_objects:
            if not related_object or not related_object.related_name:
                continue

            related_manager = getattr(self, related_object.related_name, None)

            if related_manager:
                qs = related_manager.all()
                qs._result_cache = None
                out += qs.count()

        return out

    @property
    def _child_instances(self):
        out = []
        for related_object in self._meta.related_objects:
            if not related_object or not related_object.related_name:
                continue

            related_manager = getattr(self, related_object.related_name, None)

            if related_manager:
                out.extend(related_manager.all())

        return out

    @cached_property
    def _related_fields(self):
        out = []
        for related_object in self._meta.related_objects:
            if not related_object or not related_object.field:
                continue

            out.append(related_object.field)

        return out

    @property
    def _child_fields(self):
        out = []
        for related_object in self._meta.related_objects:
            if not related_object or not related_object.field:
                continue

            related_manager = getattr(self, related_object.related_name, None)
            if related_manager and related_manager.exists():
                out.append(related_object.field)

        return out

    def has_file_wrapper(self, field=None):
        return field in self._file_wrappers and self._file_wrappers[field]

    def get_file_wrapper(self, field=None, only_existing=True):
        from cdh.files.db import FileField
        if field and not issubclass(field.__class__, FileField):
            raise ValueError("Invalid field (e.g. not None or subclass of "
                             "FileField)")

        if field not in self._file_wrappers:
            if field is not None:
                # If we only want FWs for existing relations,
                # check _child_fields
                # Otherwise, check _related_fields
                if only_existing and field not in self._child_fields:
                    raise ValueError(
                        "This field is not known to be attached to this File "
                        "instance"
                    )
                if not only_existing and field not in self._related_fields:
                    raise ValueError(
                        "This field is not known to be attached to this File "
                        "class")

            self._file_wrappers[field] = FileWrapper(
                file_instance=self,
                field=field,
                original_filename=self.original_filename,
            )

        return self._file_wrappers[field]

    def set_file_wrapper(self, value, field):
        # Local import to prevent cycles
        from cdh.files.db import FileField
        # The 'None' variant should never be set from outside this class
        # As wel as non-FileWrapper's
        if not field or not issubclass(field, FileField):
            raise ValueError("Cannot set non-field keys")

        # The 'None' variant should never be set from outside this class
        # As wel as non-FileWrapper's
        if value is None or not issubclass(value, FileWrapper):
            raise ValueError("Value is None or not a (subclass of) "
                             "FileWrapper!")

        self._file_wrappers[field] = value

    def clear_file_wrapper(self, field):
        # Local import to prevent cycles
        from cdh.files.db import FileField
        if field is None or not issubclass(field, FileField):
            raise ValueError("Cannot delete non-field keys")

        self._file_wrappers[field] = None

    def clear_file_wrappers(self,):
        self._file_wrappers = {}


class File(BaseFile):
    pass
