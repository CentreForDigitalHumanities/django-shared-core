from django.core.exceptions import ImproperlyConfigured

import uil.files.settings as settings # NoQA, absolute import somehow needed


def get_storage():
    storage = settings.UIL_FILES_STORAGE  # type: str
    module_name, class_name = storage.rsplit('.', 1)
    try:
        module = __import__(module_name)
        cls = getattr(module, class_name)
        return cls()
    except (ImportError, AttributeError):
        raise ImproperlyConfigured(
            "UIL_FILES_STORAGE doesn't seem to be set to an importable class!"
        )
