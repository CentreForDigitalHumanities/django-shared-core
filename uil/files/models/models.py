import uuid
from io import UnsupportedOperation

from django.conf import settings
from django.core.files.base import endswith_cr, endswith_lf, equals_lf
from django.core.files.utils import FileProxyMixin
from django.db import models

from ..utils import get_storage


class FileAccessMixin(FileProxyMixin):
    """
    """
    DEFAULT_CHUNK_SIZE = 64 * 2 ** 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = kwargs.get('file', None)
        del kwargs['file']
        if hasattr(self.file, 'name'):
            name = getattr(self.file, 'name', None)
        self.name = name
        if hasattr(self.file, 'mode'):
            self.mode = self.file.mode

        self._committed = True
        self.storage = get_storage()

    def __bool__(self):
        return bool(self.name)

    def chunks(self, chunk_size=None):
        """
        Read the file and yield chunks of ``chunk_size`` bytes (defaults to
        ``File.DEFAULT_CHUNK_SIZE``).
        """
        chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        try:
            self.seek(0)
        except (AttributeError, UnsupportedOperation):
            pass

        while True:
            data = self.read(chunk_size)
            if not data:
                break
            yield data

    def multiple_chunks(self, chunk_size=None):
        """
        Return ``True`` if you can expect multiple chunks.

        NB: If a particular file representation is in memory, subclasses should
        always return ``False`` -- there's no good reason to read from memory in
        chunks.
        """
        return self.size > (chunk_size or self.DEFAULT_CHUNK_SIZE)

    def __iter__(self):
        # Iterate over this file-like object by newlines
        buffer_ = None
        for chunk in self.chunks():
            for line in chunk.splitlines(True):
                if buffer_:
                    if endswith_cr(buffer_) and not equals_lf(line):
                        # Line split after a \r newline; yield buffer_.
                        yield buffer_
                        # Continue with line.
                    else:
                        # Line either split without a newline (line
                        # continues after buffer_) or with \r\n
                        # newline (line == b'\n').
                        line = buffer_ + line
                    # buffer_ handled, clear it.
                    buffer_ = None

                # If this is the end of a \n or \r\n line, yield.
                if endswith_lf(line):
                    yield line
                else:
                    buffer_ = line

        if buffer_ is not None:
            yield buffer_

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def _require_file(self):
        if not self:
            raise ValueError("The '%s' attribute has no file associated with it." % self.field.name)

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
    def path(self):
        self._require_file()
        return self.storage.path(self.name)

    @property
    def url(self):
        self._require_file()
        return self.storage.url(self.name)

    @property
    def size(self):
        self._require_file()
        if not self._committed:
            return self.file.size
        return self.storage.size(self.name)

    def open(self, mode='rb'):
        self._require_file()
        if getattr(self, '_file', None) is None:
            self.file = self.storage.open(self.name, mode)
        else:
            self.file.open(mode)
        return self

    # open() doesn't alter the file's contents, but it does reset the pointer
    open.alters_data = True

    @property
    def closed(self):
        file = getattr(self, '_file', None)
        return file is None or file.closed

    def close(self):
        file = getattr(self, '_file', None)
        if file is not None:
            file.close()

    def __getstate__(self):
        state = super().__getstate__()  # type: dict
        return state.update({
            'name': self.name,
            'closed': False,
            '_committed': True,
            '_file': None,
        })

    def __setstate__(self, state):
        self.__dict__.update(state)


class FileModel(models.Model):
    class Meta:
        abstract = True

    # Human-facing PK; Also acts as the filename on disk
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )

    app_name = models.CharField(max_length=100)

    model_name = models.CharField(max_length=100)

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


class File(FileAccessMixin, FileModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.uuid:
            self.name = self.uuid

    def save_file(self, content, save=True):
        name = self.uuid
        self.name = self.storage.save(name, content)
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.save()
    save_file.alters_data = True

    def delete_file(self, save=True):
        if not self:
            return
        # Only close the file if it's already open, which we know by the
        # presence of self._file
        if hasattr(self, '_file'):
            self.close()
            del self.file

        self.storage.delete(self.name)

        self.name = None
        self._committed = False

        if save:
            self.delete()
    delete_file.alters_data = True
