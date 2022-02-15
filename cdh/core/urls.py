from django.urls import path
from django.views.decorators.cache import cache_page

from .js_urls.views import JsUrlsView

app_name = 'cdh.core'

urlpatterns = [
    path('js-urls/', cache_page(60 * 15)(JsUrlsView.as_view()), name='js_urls'),
]
