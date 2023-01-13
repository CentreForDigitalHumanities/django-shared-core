from django.conf import settings

HOST = getattr(
    settings,
    'INTEGRATION_PLATFORM_HOST',
    '',
)

CONSUMER_CREDENTIALS = getattr(
    settings,
    'INTEGRATION_PLATFORM_CONSUMER_CREDENTIALS',
    {
        'key': '',
        'secret': ''
    }
)
