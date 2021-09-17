from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views import generic

from uil.files.db import File
from uil.files.db.wrappers import FileWrapper


class BaseFileView(generic.View):
    http_method_names = ['get', 'head', 'options']
    uuid_path_parameter = 'uuid'

    def get(self, request, **kwargs):
        response = HttpResponse()
        response.content = self._file.name
        return response

    @cached_property
    def _file(self) -> FileWrapper:
        uuid = self.kwargs.get(self.uuid_path_parameter)
        file = File.objects.get(uuid=uuid)

        return file.file_wrapper
