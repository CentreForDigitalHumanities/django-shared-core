import os

from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.functional import LazyObject, cached_property

from cdh.files import settings


@deconstructible
class UiLFileStorage(FileSystemStorage):
    """
    Standard filesystem storage
    """
    # The combination of O_CREAT and O_EXCL makes os.open() raise OSError if
    # the file already exists before it's opened.
    OS_OPEN_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0)

    def __init__(self):
        # Override init to strip arguments
        super().__init__()

    @cached_property
    def base_location(self):
        return settings.FILE_ROOT

    @cached_property
    def file_permissions_mode(self):
        return settings.FILE_UPLOAD_PERMISSIONS

    @cached_property
    def directory_permissions_mode(self):
        return settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS


class DefaultStorage(LazyObject):
    def _setup(self):
        self._wrapped = UiLFileStorage()


default_storage = DefaultStorage()
