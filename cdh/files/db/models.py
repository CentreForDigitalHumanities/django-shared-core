import uuid

from django.conf import settings
from django.db import models

from uil.files.db.proxy_file import ProxyFile


class File(models.Model):

    # Human-facing PK; Also acts as the filename on disk
    uuid = models.UUIDField(
        "Universally Unique IDentifier",
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

    _proxy_file = None

    @property
    def _has_file_proxy(self):
        return self._proxy_file is not None

    def _get_proxy_file(self):
        if self._proxy_file is None:
            self._proxy_file = ProxyFile(
                None, self, None, self.original_filename
            )

        return self._proxy_file

    def _set_proxy_file(self, file):
        self._proxy_file = file

    def _del_proxy_file(self):
        del self._proxy_file

    proxy_file = property(_get_proxy_file, _set_proxy_file, _del_proxy_file)

