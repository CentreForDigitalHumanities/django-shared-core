"""
    JS URLs views
    =============

    This module defines views allowing to expose the Javascript helper and catalog of URLs allowing
    to provide reverse-like functionality on the client side.

"""
from django.views.generic import TemplateView

from .conf import settings
from .serializer import get_urls_as_json


class JsUrlsView(TemplateView):
    """ Renders a Javascript helper allowing to reverse Django URLs. """

    content_type = 'application/javascript'
    template_name = 'cdh.core/js_urls.js'

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        context['function_name'] = settings.FUNCTION_NAME
        context['urls'] = get_urls_as_json()
        return context
