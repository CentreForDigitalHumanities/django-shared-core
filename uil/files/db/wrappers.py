import uuid
from typing import Optional, Union

from django.core.files import File
import magic
from django.db.models import Manager

from .. import settings
from ..utils import get_storage


class FileWrapper(File):
    """
    """
    DEFAULT_CHUNK_SIZE = 64 * 2 ** 10

    def __init__(self, file_instance, field, original_filename):
        self.file = None
        self.original_filename = original_filename
        self.file_instance = file_instance
        self._field = field
        self.storage = get_storage()
        self._committed = True
        self._removed = False

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
            return super().__bool__()
        except AttributeError:
            # When this file has been deleted, it might still exist in memory
            # However, at that point self._file has been removed from the object
            # Thus, AttributeError is raised by out parent's __bool__
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

    # The standard File contains most of the necessary properties, but
    # FieldFiles can be instantiated without a name, so that needs to
    # be checked for here.

    def _require_file(self):
        if not self:
            raise ValueError(
                "The '%s' attribute has no file associated with it." % self.field.name)

    def _get_file(self):
        self._require_file()
        if getattr(self, '_file', None) is None:
            self._file = self.storage.open(self.name_on_disk, 'rb')
        return self._file

    def _set_file(self, file):
        self._file = file

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
        if not self:
            return

        # Check if we only have one reference to this file
        # If we have more than 1 reference, and we're not forcing a deletion,
        # stop right here!
        if self.file_instance and \
           self.file_instance._num_child_instances > 1 and \
           not force:
            return

        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name_on_disk)

        self.original_filename = None
        self._committed = False

        if save:
            self.file_instance.delete()

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


class TrackedFileWrapper(PrivateCacheMixin):

    def __init__(self, manager: Manager, instance, field):
        super().__init__()
        self._manager = manager
        self._instance = instance
        self._field = field
        self._through_model = self._field.remote_field.through

    def _get_linking_instance(self, obj: Union[FileWrapper, File]):
        if isinstance(obj, FileWrapper):
            obj = obj.file_instance

        return self._through_model.objects.get(file_id=obj)

    def _resolve_to_file_wrapper(self, obj):
        """Tries to map the input to a FileWrapper in this M2M;
        accepts a FileWrapper itself, a File instance and an int/uuid for a
        File instance"""
        if isinstance(obj, FileWrapper):
            return obj
        if isinstance(obj, self._field.related_model):
            return obj.file_wrapper
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
        if self.is_cached('current'):
            return self.get_cached_value('current')

        file_instance = self._manager.order_by('-modified_on').first()

        if file_instance:
            self.cache_value('current', file_instance.file_wrapper)
            return file_instance.file_wrapper

        return None

    def _set_current_file(self, value):
        if value is None:
            raise ValueError("Cannot set current_file to None. Please use the delete_all method.")

        resolved_value = self._resolve_to_file_wrapper(value)

        if not resolved_value:
            raise ValueError() # TODO: adding new file
        resolved_value.save()
        self.cache_value('current', resolved_value)

    def _del_current_file(self):
        self.invalidate_cache_value('current')
        current_file = self._get_current_file()

        if current_file:
            # current_file.delete(False) TODO: check if this is indeed unnecessary
            self._manager.remove(current_file.file_instance)

    current_file = property(
        _get_current_file,
        _set_current_file,
        _del_current_file
    )

    @property
    def all(self):
        return map(
            lambda file: self._resolve_to_file_wrapper(file),
            self._manager.all()
        )

    def add(self, file):
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
        self.invalidate_cache_value('current')

    add.alters_data = True

    def delete(self, file):
        if file is None:
            raise ValueError("Cannot delete None!")

        file = self._resolve_to_file_wrapper(file)
        link = self._get_linking_instance(file)
        link.delete()

    def delete_all(self):
        self._manager.all().delete()
        self.invalidate_cache_value('current')

    delete_all.alters_data = True
