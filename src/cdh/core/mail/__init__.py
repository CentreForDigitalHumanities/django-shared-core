"""A set of classes and utilities to facilitate sending HTML emails.

The :py:mod:`.utils` module contains some helpers for basic usage and sending
mass-but-personalized emails. The utils are somewhat limited;

The :py:mod:`.classes` module contains the actual working code, and can be used
directly for more advanced usages.

The :py:mod:`.views` and :py:mod:`.widgets` modules contain helpers for dealing
with custom template emails.
"""
from .classes import *
from .utils import *
from .views import *
from .widgets import *
