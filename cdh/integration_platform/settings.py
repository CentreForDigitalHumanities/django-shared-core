from django.conf import settings

HOST = getattr(
    settings,
    'INTEGRATION_PLATFORM_HOST',
    '',
)

DIGITAL_IDENTITY_API_CREDENTIALS = getattr(
    settings,
    'DIGITAL_IDENTITY_API_CREDENTIALS',
    {
        'key': '',
        'secret': ''
    }
)
