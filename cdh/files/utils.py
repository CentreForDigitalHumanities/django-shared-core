import importlib

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage

import uil.files.settings as settings # NoQA, absolute import somehow needed


def get_storage() -> Storage:
    storage = settings.STORAGE  # type: str
    module_name, class_name = storage.rsplit('.', 1)
    try:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        if callable(cls):
            return cls()
        if isinstance(cls, Storage):
            return cls

        raise ImproperlyConfigured
    except (ImportError, AttributeError, ImproperlyConfigured):
        raise ImproperlyConfigured(
            "CDH_FILES_STORAGE doesn't seem to be set to an importable class!"
        )
