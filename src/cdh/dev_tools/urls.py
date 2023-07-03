import debug_toolbar
from django.urls import path, include

urlpatterns = [
    path('debug_toolbar/', include(debug_toolbar.urls)),
]
