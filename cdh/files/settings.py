from django.conf import settings

STORAGE = getattr(
    settings,
    'CDH_FILES_STORAGE',
    'dh.files.storage.default_storage',
)

FILE_ROOT = getattr(
    settings,
    'CDH_FILES_FILE_ROOT',
    'cdh_files',
)

FILE_UPLOAD_PERMISSIONS = getattr(
    settings,
    'CDH_FILES_FILE_UPLOAD_PERMISSIONS',
    settings.FILE_UPLOAD_PERMISSIONS,
)

FILE_UPLOAD_DIRECTORY_PERMISSIONS = getattr(
    settings,
    'CDH_FILES_FILE_UPLOAD_DIRECTORY_PERMISSIONS',
    settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS,
)

_tlum_loaded = 'cdh.core.middleware.ThreadLocalUserMiddleware' in \
               settings.MIDDLEWARE

TRACK_CREATED_BY = getattr(
    settings,
    'CDH_FILES_TRACK_CREATED_BY',
    _tlum_loaded,
)
