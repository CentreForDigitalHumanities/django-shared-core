from django.urls import path

from .views import *

app_name = 'dev_integration_platform'

urlpatterns = [
    path('', IPHome.as_view(), name='home'),
    path('dia/simple/', DIASimpleTestView.as_view(), name='dia_simple'),
    path('dia/users/', DIAUsersFormTestCreateView.as_view(), name='dia_users'),
    path('dia/users/<int:pk>/', DIAUsersFormTestView.as_view(),
         name='dia_users'),
]

