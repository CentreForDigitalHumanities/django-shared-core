import uuid
from typing import Optional, Union, TYPE_CHECKING

from django.core.files import File
import magic
from django.db.models import Manager

from .. import settings
from ..mime_names import get_name_from_mime
from ..utils import get_storage


if TYPE_CHECKING:
    from . import TrackedFileField
    from .models import BaseFile


class FileWrapper(File):
    """
    """
    DEFAULT_CHUNK_SIZE = 64 * 2 ** 10

    def __init__(self, file_instance, field, original_filename):
        # self.file = None
        self.original_filename = original_filename
        self.file_instance = file_instance
        self._field = field
        self.storage = get_storage()
        self._committed = True
        self._removed = False

    def __getattr__(self, item):
        # Sometimes the ORM expects a different field than id/pk; this function
        # checks if the requested attribute is said field, return id.
        if item == self._field.target_field.attname:
            return self.file_instance.id

        raise AttributeError(f"No such attribute '{item}'")

    @property
    def name(self):
        if self._field and self._field.filename_generator:
            return self.field.filename_generator(self)
        return self.original_filename

    @property
    def name_on_disk(self):
        if self.file_instance:
            if not self.file_instance.uuid:
                self.file_instance.uuid = uuid.uuid4()
            return str(self.file_instance.uuid)
        else:
            raise RuntimeError("No file instance. Can not retrieve filename "
                               "without it! (Please assign this object to a "
                               "FileField field of a model before saving)")

    @property
    def field(self):
        if self._field:
            return self._field

        if self.file_instance and self.file_instance._child_fields:
            return self.file_instance._child_fields[0]

        return None

    def __hash__(self):
        return hash(self.name_on_disk)

    def __bool__(self):
        try:
            return bool(self.file)
        except AttributeError:
            return False

    # Alias these to the file_instance, as sometimes the ORM expects these
    # values
    id = property(
        lambda self: self.file_instance.id,
        lambda self, value: setattr(self.file_instance, 'id', value),
        lambda self: delattr(self.file_instance, 'id')
    )
    pk = property(
        lambda self: self.file_instance.pk,
        lambda self, value: setattr(self.file_instance, 'pk', value),
        lambda self: delattr(self.file_instance, 'pk')
    )

    # For easier access
    uuid = property(lambda self: self.file_instance.uuid)
    content_type = property(lambda self: self.file_instance.content_type)
    created_by = property(lambda self: self.file_instance.created_by)
    created_on = property(lambda self: self.file_instance.created_on)
    modified_on = property(lambda self: self.file_instance.modified_on)

    def get_content_type_display(self):
        return get_name_from_mime(self.content_type, 'Unknown file type')

    # The standard File contains most of the necessary properties, but
    # FieldFiles can be instantiated without a name, so that needs to
    # be checked for here.

    def _require_file(self):
        if not self:
            raise ValueError(
                "The '%s' attribute has no file associated with it." % self.field.name)

    def _get_file(self):
        try:
            if getattr(self, '_file', None) is None:
                self._file = self.storage.open(self.name_on_disk, 'rb')
        except FileNotFoundError:
            self._file = None
        return self._file

    def _set_file(self, file):
        self._file = file
        # You might think, why? Well, due to a very complicated descriptor chain
        # this might actually fail to set, in which case we really should stop
        # NOW #speakingFromExperience
        # It will only fail after a code change, so assert should be fine
        assert self._file == file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    @property
    def path(self):
        self._require_file()
        return self.storage.path(self.name_on_disk)

    @property
    def url(self):
        raise NotImplementedError

    @property
    def size(self):
        self._require_file()
        if not self._committed:
            return self.file.size
        return self.storage.size(self.name_on_disk)

    def open(self, mode='rb'):
        self._require_file()
        if getattr(self, '_file', None) is None:
            self.file = self.storage.open(self.name_on_disk, mode)
        else:
            self.file.open(mode)
        return self

    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    # In addition to the standard File API, FieldFiles have extra methods
    # to further manipulate the underlying file, as well as update the
    # associated model instance.

    def save(self, content=None, original_filename=None):
        if content is None:
            content = self.file

        if original_filename is None and hasattr(content, 'name'):
            original_filename = content.name

        # If we overwrite the file this instance represents, we need to first
        # delete the old one, as otherwise we would lose the new file
        if self.storage.exists(self.name_on_disk):
            self.storage.delete(self.name_on_disk)
        self.storage.save(
            self.name_on_disk,
            content,
            max_length=self.field.max_length
        )
        self._committed = True

        # Use magic to determine the mime type. It's pretty obvious, I know
        # I just liked saying 'use MAGIC'
        with self.open() as file:
            mime = magic.from_buffer(file.read(2048), mime=True)
        self.file_instance.content_type = mime

        if original_filename:
            self.file_instance.original_filename = original_filename

        # TRACK_CREATED_BY should only be enabled if the right middleware is
        # loaded, so we don't check it. (A system check enforces it,
        # so we can actually be sure in this case)
        if settings.TRACK_CREATED_BY: # NoQA; We are allowed to access this linter
            from uil.core.middleware import get_current_user
            current_user = get_current_user()
            # Make sure we don't try to safe using AnonymousUser
            if current_user and not current_user.is_anonymous:
                self.file_instance.created_by = get_current_user()

        self.file_instance.save()

    save.alters_data = True

    def delete(self, save=True, force=False):
        """Deletes the file on disk. If save = True, the metadata object will
        also be deleted. Note: only delete the metadata object if no other DB
        object is referencing it, otherwise you'll get nasty Integrity
        errors!

        :param save: Whether to also delete the metadata in the DB, defaults
                     to True
        :param force: Whether to force a deletion if multiple DB objects still
                      refer to it, defaults to False
        """
        if not self.storage.exists(self.name_on_disk):
            return

        # By default, only delete if there are no references in the DB anymore
        deletion_threshold = 0

        # If we are instructed to also destroy our file_instance and we still
        # have a reference, we allow deletion with 1 more reference
        if save and self.file_instance:
            model = self.file_instance.__class__
            if model.objects.filter(pk=self.file_instance.pk).exists():
                deletion_threshold += 1

        # Check if we only have the allowed amount number of references or fewer
        # If we have more, and we're not forcing a deletion, stop right here!
        if self.file_instance and \
           self.file_instance._num_child_instances > deletion_threshold and \
           not force:
            return

        # First, delete our metadata model. The check above _should_ make sure
        # we don't get integrity errors, but it's better to have this fail
        # because of those errors before we have actually deleted the file
        if save:
            self.file_instance.delete()

        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name_on_disk)

        self.original_filename = None
        self._committed = False
        self.file_instance.clear_file_wrappers()

    delete.alters_data = True

    @property
    def closed(self):
        file = getattr(self, '_file', None)
        return file is None or file.closed

    def close(self):
        file = getattr(self, '_file', None)
        if file is not None:
            file.close()

    def __getstate__(self):
        # FieldFile needs access to its associated model field, an instance and
        # the file's name. Everything else will be restored later, by
        # FileDescriptor below.
        return {
            'original_filename': self.original_filename,
            'closed':            False,
            '_committed':        True,
            '_removed':          self._removed,
            '_file':             None,
            'file_instance':     self.file_instance,
            'field':             self.field,
        }

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.storage = get_storage()


class PrivateCacheMixin:

    def __init__(self, *args, **kwargs):
        self._cache = {}

    def is_cached(self, key):
        return key in self._cache and self._cache[key] is not None

    def get_cached_value(self, key):
        if self.is_cached(key):
            return self._cache[key]

        return None

    def cache_value(self, key, value):
        self._cache[key] = value

    def invalidate_cache_value(self, key):
        self._cache[key] = None

    def invalidate_caches(self):
        self._cache = {}


class TrackedFileWrapper(PrivateCacheMixin):

    def __init__(self, manager: Manager, instance, field: 'TrackedFileField'):
        super().__init__()
        self._manager = manager
        self._instance = instance
        self._field = field
        self._through_model = self._field.remote_field.through
        # This should retrieve the FileField actually holding the File; it's
        # a bit tricky to get it, as it's filename can differ if using custom
        # File model.
        self._file_field = self._through_model._meta.get_field(
            self._field.m2m_reverse_field_name()
        )

    def __repr__(self):
        return f"<{self.__class__.__module__}.{self.__class__.__name__} " \
               f"for {self._instance.__class__.__module__}." \
               f"{self._instance.__class__.__name__}." \
               f"{self._field.attname}>"

    def _get_linking_instance(self, obj: Union[FileWrapper, File]) -> Optional:
        """Given a FileWrapper or File, this method will try to find the
        object linking it to an object."""
        if not self._has_linking_instance(obj):
            return None

        if isinstance(obj, FileWrapper):
            obj = obj.file_instance

        kwargs = {
            self._file_field.attname: obj
        }
        return self._through_model.objects.get(**kwargs)

    def _has_linking_instance(self, obj: Union[FileWrapper, File]) -> bool:
        """Given a FileWrapper or File, this method will try to find the
        object linking it to an object."""
        if isinstance(obj, FileWrapper):
            obj = obj.file_instance

        kwargs = {
            self._file_field.attname: obj
        }
        return self._through_model.objects.filter(**kwargs).exists()

    def _resolve_to_file_wrapper(self, obj: Union[
        uuid.UUID, FileWrapper, 'BaseFile', int, str
    ]) -> Optional[FileWrapper]:
        """Tries to map the input to a FileWrapper in this M2M;
        accepts a FileWrapper itself, a File instance and an int/uuid for a
        File instance"""
        if isinstance(obj, FileWrapper):
            return obj
        if isinstance(obj, self._field.related_model):
            return obj.get_file_wrapper(self._file_field)
        if isinstance(obj, int):
            try:
                return self._resolve_to_file_wrapper(self._manager.get(pk=obj))
            except self._field.related_model.DoesNotExist:
                pass
        if isinstance(obj, uuid.UUID):
            try:
                return self._resolve_to_file_wrapper(self._manager.get(
                    uuid=obj))
            except self._field.related_model.DoesNotExist:
                pass
        if isinstance(obj, str):
            try:
                obj = uuid.UUID(obj)
                return self._resolve_to_file_wrapper(obj)
            except ValueError:
                pass

        return None

    def _get_current_file(self) -> Optional[FileWrapper]:
        """Tries to retrieve the file representing the 'current' value of
        this field."""
        if self.is_cached('current'):
            return self.get_cached_value('current')

        try:
            linking_instance = self._through_model.objects.get(current=True)
        except self._through_model.DoesNotExist:
            return None

        if linking_instance:
            value = getattr(
                linking_instance,
                self._field.m2m_reverse_field_name()
            )
            self.cache_value(
                'current',
                value
            )
            return value

        return None

    def _set_current_file(self, value: Union[
        uuid.UUID, FileWrapper, 'BaseFile', int, str
    ]) -> None:
        """Tries to set a new file representing the 'current' value of
        this field. It can be a file that's already tracked, or a new one.
        """
        if value is None:
            self._del_current_file()
            return

        resolved_value = self._resolve_to_file_wrapper(value)

        # If we don't retrieved a value, just use .add;
        # Even if we get a value, the fact that we got a FileWrapper doesn't
        # mean it's _our_ FileWrapper. We could of course check FW._field or
        # FW.file_instance._child_fields; however, it's way easier to just do
        # an .exists check on the linking table. (As that's cheaper in terms
        # of computation and DB access).
        if not resolved_value or not self._has_linking_instance(resolved_value):
            return self.add(value)

        resolved_value.save()
        self._set_as_current(resolved_value)

    def _del_current_file(self) -> None:
        """Deletes the file currently represeting the """
        self.invalidate_caches()
        current_file = self._get_current_file()

        if current_file:
            self.delete(current_file)

    current_file = property(
        _get_current_file,
        _set_current_file,
        _del_current_file
    )
    current_file.fset.alters_data = True
    current_file.fdel.alters_data = True

    def _set_as_current(self, file_wrapper: FileWrapper) -> None:
        self._through_model.objects.update(current=False)

        link = self._get_linking_instance(file_wrapper)
        link.current = True
        link.save()

        self.cache_value('current', file_wrapper)

    @property
    def all(self):
        return map(
            lambda file: self._resolve_to_file_wrapper(file),
            self._manager.all()
        )

    def add(self, file: Union[
        uuid.UUID, FileWrapper, 'BaseFile', int, str
    ]) -> None:
        through_obj = self._through_model()
        setattr(
            through_obj,
            self._field.m2m_field_name(),
            self._instance
        )
        setattr(
            through_obj,
            self._field.m2m_reverse_field_name(),
            file
        )
        file_wrapper = getattr(through_obj, self._field.m2m_reverse_field_name())
        file_wrapper.save()

        through_obj.save()

        self._set_as_current(file_wrapper)
    add.alters_data = True

    def set_as_current(self, file: Union[
        uuid.UUID, FileWrapper, 'BaseFile', int, str
    ]) -> None:
        if file is None:
            raise ValueError("Cannot set None as current! (Did you mean to "
                             "delete stuff?)")

        file = self._resolve_to_file_wrapper(file)
        self._set_as_current(file)
    set_as_current.alters_data = True

    def delete(self, file: Union[
        uuid.UUID, FileWrapper, 'BaseFile', int, str
    ]) -> None:
        if file is None:
            raise ValueError("Cannot delete None!")

        file = self._resolve_to_file_wrapper(file)
        link = self._get_linking_instance(file)
        link.delete()
        file.delete()

        if link.current:
            self.invalidate_caches()
    delete.alters_data = True

    def delete_all(self) -> None:
        """Delete all files currently tracked"""
        self._manager.all().delete()
        self.invalidate_caches()
    delete_all.alters_data = True
