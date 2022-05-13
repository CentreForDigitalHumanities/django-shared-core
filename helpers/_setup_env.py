"""Helper module that sets up a minimal Django environment"""
import sys

import django
from django.conf import settings


def setup_environment():
    # Append curdir to path, needed for imports to work
    sys.path.insert(0, '.')

    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'cdh.core',
            'cdh.vue',
            'cdh.files',
        ),
    )

    django.setup()
