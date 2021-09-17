import logging
import uuid

from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, FieldError
from django.db import models
from django.utils.functional import cached_property

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

    app_name = models.CharField(max_length=100)

    model_name = models.CharField(max_length=100)

    field_name = models.CharField(max_length=255)

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

    def set_child_info_from_field(self, field):
        # Local import to prevent dependency cycles
        from uil.files.db import FileField
        if not isinstance(field, FileField):
            return
        self.app_name = field.model._meta.app_label  # NoQA
        self.model_name = field.model._meta.object_name  # NoQA
        self.field_name = field.name

    @cached_property
    def _child_model(self):
        if self.app_name and self.model_name:
            try:
                app_config = apps.get_app_config(self.app_name)
                return app_config.get_model(self.model_name)
            except LookupError:
                logger.warning("Could not load owning model class "
                               "when creating the file wrapper")
                return None

    @cached_property
    def _child_instance(self):
        if self._child_model and self.field_name:
            try:
                return self._child_model.objects.get(
                    **{
                        self.field_name: self.pk
                    }
                )
            except (self._child_model.DoesNotExist, FieldError):
                logger.warning("Could not retrieve owning model instance "
                               "when creating the file wrapper")
        else:
            logger.warning("Creating a file wrapper instance without "
                           "knowledge of which model or field this file "
                           "belongs to!")

        return None

    @cached_property
    def _child_field(self):
        try:
            if self._child_model and self.field_name:
                return self._child_model._meta.get_field(self.field_name)
        except FieldDoesNotExist:
            pass  # Do nothing, the code below is sufficient

        logger.warning("Could not load the field on the child class")

        return None

    @property
    def _has_file_wrapper(self):
        return self._file_wrapper is not None

    def _get_file_wrapper(self):
        if self._file_wrapper is None:
            self._file_wrapper = FileWrapper(
                self._child_instance,
                self,
                self._child_field,
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




