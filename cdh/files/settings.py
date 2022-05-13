from django.conf import settings

UIL_FILES_STORAGE = getattr(
    settings,
    'UIL_FILES_STORAGE',
    settings.DEFAULT_FILE_STORAGE
)
