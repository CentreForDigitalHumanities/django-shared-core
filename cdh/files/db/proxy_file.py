from django.core.files import File

from ..utils import get_storage


class ProxyFile(File):
    """
    """
    DEFAULT_CHUNK_SIZE = 64 * 2 ** 10

    def __init__(self, child_instance, file_instance, field, name):
        super().__init__(None, name)
        self.child_instance = child_instance
        self.file_instance = file_instance
        self.field = field
        self.storage = get_storage()
        self._committed = True

    def __hash__(self):
        return hash(self.name)

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
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, file):
        self._file = file

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    @property
    def actual_name(self):
        return self.file_instance.uuid

    @property
    def path(self):
        self._require_file()
        return self.storage.path(self.name)

    @property
    def url(self):
        raise NotImplementedError

    @property
    def size(self):
        self._require_file()
        if not self._committed:
            return self.file.size
        return self.storage.size(self.actual_name)

    def open(self, mode='rb'):
        self._require_file()
        if getattr(self, '_file', None) is None:
            self.file = self.storage.open(self.actual_name, mode)
        else:
            self.file.open(mode)
        return self

    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    # In addition to the standard File API, FieldFiles have extra methods
    # to further manipulate the underlying file, as well as update the
    # associated model instance.

    def save(self, content, save=True):
        # If we overwrite the file this instance represents, we need to first
        # delete the old one, as otherwise we would lose the new file
        if self.storage.exists(self.actual_name):
            self.storage.delete(self.actual_name)
        self.storage.save(
            self.actual_name,
            content,
            max_length=self.field.max_length
        )
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.file_instance.save()

    save.alters_data = True

    def delete(self, save=True):
        if not self:
            return
        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.actual_name)

        self.name = None
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
            'name':       self.name,
            'closed':     False,
            '_committed': True,
            '_file':      None,
            'instance':   self.instance,
            'field':      self.field,
        }

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.storage = get_storage()
