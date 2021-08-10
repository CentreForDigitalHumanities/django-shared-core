from django.conf import settings

STORAGE = getattr(
    settings,
    'UIL_FILES_STORAGE',
    'uil.files.storage.default_storage',
)

FILE_ROOT = getattr(
    settings,
    'UIL_FILES_FILE_ROOT',
    'uil_files',
)

FILE_UPLOAD_PERMISSIONS = getattr(
    settings,
    'UIL_FILES_FILE_UPLOAD_PERMISSIONS',
    settings.FILE_UPLOAD_PERMISSIONS,
)

FILE_UPLOAD_DIRECTORY_PERMISSIONS = getattr(
    settings,
    'UIL_FILES_FILE_UPLOAD_DIRECTORY_PERMISSIONS',
    settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS,
)

_tlum_loaded = 'uil.core.middleware.ThreadLocalUserMiddleware' in \
               settings.MIDDLEWARE

TRACK_CREATED_BY = getattr(
    settings,
    'UIL_FILES_TRACK_CREATED_BY',
    _tlum_loaded,
)
