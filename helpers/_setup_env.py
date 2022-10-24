"""Helper module that sets up a minimal Django environment"""
import os
import sys

import django


def setup_environment():
    # Append curdir to path, needed for imports to work
    sys.path.insert(0, '.')
    os.environ['DJANGO_SETTINGS_MODULE'] = '_fake_settings'

    django.setup()
