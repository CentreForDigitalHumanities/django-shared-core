from django.conf import settings

STORAGE = getattr(
    settings,
    'CDH_FILES_STORAGE',
    'cdh.files.storage.default_storage',
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

# This is a hard-kill switch on any file deletion. It works by making the
# remove call on the storage backend a no-op. (So it will delete DB references,
# but not the actual file).
# This is intended for when you think the files-app is eating your files.
# It should be safe to enable; HOWEVER! If your code manipulates the underlying
# `FileWrapper` objects directly, you may encounter issues.
# (You should refrain from doing that, but be warned)
FILE_BLOCK_DELETION = getattr(
    settings,
    'CDH_FILES_FILE_BLOCK_DELETION',
    False,
)

_tlum_loaded = 'cdh.core.middleware.ThreadLocalUserMiddleware' in \
               settings.MIDDLEWARE

TRACK_CREATED_BY = getattr(
    settings,
    'CDH_FILES_TRACK_CREATED_BY',
    _tlum_loaded,
)
