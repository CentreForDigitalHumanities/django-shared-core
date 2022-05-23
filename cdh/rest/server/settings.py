from django.conf import settings
from django.contrib.auth import get_user_model

from .token_algorithms import Algorithms

USER_MODEL = getattr(
    settings,
    "CDH_REST_SERVER_USER_MODEL",
    get_user_model()
)

REST_PERMITTED_CLIENTS = getattr(
    settings,
    "CDH_REST_SERVER_PERMITTED_CLIENTS",
    []
)

JWT_ALGORITHM = getattr(
    settings,
    "CDH_REST_SERVER_JWT_ALGORITHM",
    Algorithms.SHA
)

JWT_PRIVATE_KEY = getattr(
    settings,
    "CDH_REST_SERVER_JWT_PRIVATE_KEY",
    None
)

JWT_PUBLIC_KEY = getattr(
    settings,
    "CDH_REST_SERVER_JWT_PUBLIC_KEY",
    None
)

JWT_SECRET_KEY = getattr(
    settings,
    "CDH_REST_SERVER_JWT_SECRET_KEY",
    settings.SECRET_KEY
)
