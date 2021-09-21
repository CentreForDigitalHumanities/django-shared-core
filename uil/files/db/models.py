import logging
import uuid

from django.conf import settings
from django.db import models

from uil.files.db import manager
from uil.files.db.wrappers import FileWrapper


logger = logging.getLogger('uil.files')


class File(models.Model):

    objects = manager.FileManager()

    # Human-facing PK; Also acts as the filename on disk
    uuid = models.UUIDField(
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

    _file_wrapper = None

    @property
    def _num_child_instances(self):
        out = 0
        for related_object in self._meta.related_objects:
            if not related_object or not related_object.related_name:
                continue

            related_manager = getattr(self, related_object.related_name, None)

            if related_manager:
                out += related_manager.count()

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

    @property
    def _child_fields(self):
        out = []
        for related_object in self._meta.related_objects:
            if not related_object or not related_object.field:
                continue

            out.append(related_object.field)

        return out

    @property
    def _has_file_wrapper(self):
        return self._file_wrapper is not None

    def _get_file_wrapper(self):
        if self._file_wrapper is None:
            self._file_wrapper = FileWrapper(
                self,
                None,
                self.original_filename
            )

        return self._file_wrapper

    def _set_file_wrapper(self, file):
        self._file_wrapper = file

    def _del_file_wrapper(self):
        del self._file_wrapper

    file_wrapper = property(
        _get_file_wrapper,
        _set_file_wrapper,
        _del_file_wrapper
    )




