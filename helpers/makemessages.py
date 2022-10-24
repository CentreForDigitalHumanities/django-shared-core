#!/usr/bin/env python
"""As this project doesn't contain a django project, we can't make migrations
the normal way. This script solves this problem by executing the
makemigrations command in a minimal django environment"""
from django.core.management import call_command

import _setup_env

_setup_env.setup_environment()

call_command(
    'makemessages',
    locale=['nl', 'en'],
    no_obsolete=True,
    ignore=['__init__.py']
)
