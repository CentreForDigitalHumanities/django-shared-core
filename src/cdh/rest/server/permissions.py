from rest_framework.permissions import BasePermission

from .settings import REST_PERMITTED_CLIENTS


class IsPermittedClient(BasePermission):

    def has_permission(self, request, view) -> bool:
        client_ip = request.META.get('REMOTE_ADDR', None)
        client_host = request.META.get('REMOTE_HOST', None)

        if not client_ip or client_ip not in REST_PERMITTED_CLIENTS:
            return False

        if client_host:
            return client_host in REST_PERMITTED_CLIENTS

        return True
