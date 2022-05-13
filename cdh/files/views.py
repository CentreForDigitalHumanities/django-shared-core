from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.functional import cached_property
from django.views import generic
from typing import Optional

from cdh.files.db import TrackedFileField
from cdh.files.db import File
from cdh.files.db.wrappers import FileWrapper


class BaseFileView(generic.View):
    http_method_names = ['get', 'head', 'options']
    uuid_path_parameter = 'uuid'
    file_class = File
    always_download = False

    def get(self, request, **kwargs):
        if self._file_wrapper is None:
            return HttpResponseNotFound()

        if self.always_download:
            content_disposition = f"attachment; " \
                                  f"filename={self.get_name()}"
        else:
            content_disposition = f"inline; " \
                                  f"filename={self.get_name()}"

        with self._file_wrapper.file as file:
            response = HttpResponse(
                content=file,
                content_type=self._file_wrapper.content_type,
            )

            response['Content-Disposition'] = content_disposition
            return response

    def get_name(self) -> str:
        return self._file_wrapper.name

    def get_queryset(self):
        uuid = self.kwargs.get(self.uuid_path_parameter)
        return self.file_class.objects.filter(uuid=uuid)

    @cached_property
    def _file_wrapper(self) -> Optional[FileWrapper]:
        qs = self.get_queryset()
        if qs.exists():
            return qs.get().get_file_wrapper()
        return None


class FieldLimitedFileViewMetaclass(type):
    """This metaclass makes sure the class attributes are all filled in.

    The programmer either needs to define model_field directly or
    indirectly through model and model_field_name. This metaclass will
    make sure the other set is filled in from the other
    """

    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)

        # If we are making the base class, we stop here as the base should be
        # regarded as an abstract class
        if attrs['__module__'] == 'cdh.files.views' and \
            attrs['__qualname__'] == 'BaseFieldLimitedFileView':
            return cls

        if cls.model_field is None and (
                    cls.model_field_name is None or
                    cls.model is None
        ):
            raise ImproperlyConfigured(
                "Either set model_field or a combination of model and "
                "model_field_name."
            )

        if cls.model_field is None:
            try:
                if isinstance(cls.model, str):
                    cls.model = apps.get_model(cls.model)

                cls.model_field = cls.model._meta.get_field(
                    cls.model_field_name
                )
            # These except clauses are reversed in terms of what call causes it
            # KeyError is thrown by get_field, LookupError by get_model
            # As KeyError is a subclass of LookupError, we need this reverse
            # ordering to make sure the right error is handled for the two
            # error cases. (In other words, LookupError would also catch
            # KeyError otherwise).
            except KeyError:
                raise ImproperlyConfigured(
                    f"Could not find {cls.model_field_name} in model "
                    f"{cls.model._meta.name}"
                )
            except LookupError:
                raise ImproperlyConfigured(
                    f"{cls.model} is not a registered Django model"
                )

        # If we got a TrackedFileField, we need to track down the FileField
        # of the through model instead. (No pun intended)
        if isinstance(cls.model_field, TrackedFileField):
            through_model = cls.model_field.remote_field.through
            # This should retrieve the FileField actually holding the File; it's
            # a bit tricky to get it, as it's filename can differ if using custom
            # File model.
            cls.model_field = through_model._meta.get_field(
                cls.model_field.m2m_reverse_field_name()
            )

        if cls.model is None:
            cls.model = cls.model_field.model

        if cls.model_field_name is None:
            cls.model_field_name = cls.model_field.name

        cls.file_class = cls.model_field.related_model

        return cls


class BaseFieldLimitedFileView(
    BaseFileView,
    metaclass=FieldLimitedFileViewMetaclass
):
    file_class = None  # Not needed, will be autofilled
    model_field = None
    model = None
    model_field_name = None

    @cached_property
    def _file_wrapper(self) -> Optional[FileWrapper]:
        qs = self.get_queryset()

        if not qs.exists():
            return None

        file = qs.get()

        if self.model_field in file._child_fields:
            return file.get_file_wrapper(self.model_field)

        return None
