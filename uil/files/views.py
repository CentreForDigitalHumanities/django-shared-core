from django.http import HttpResponse, HttpResponseNotFound
from django.utils.functional import cached_property
from django.views import generic
from typing import Optional

from uil.files.db import File
from uil.files.db.wrappers import FileWrapper


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

    def get_name(self):
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
