#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def get_root_dir() -> str:
    """Get's the directory directly above this files location"""
    cwd = os.getcwd()
    return cwd.rsplit(os.sep, 1)[0]


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_project.settings')
    # Include our root in the path, otherwise we won't be able to load our
    # actual libraries
    sys.path.insert(1, get_root_dir())
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
