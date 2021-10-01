
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import HomeView, StylesView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('styles/', StylesView.as_view(), name='styles'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
