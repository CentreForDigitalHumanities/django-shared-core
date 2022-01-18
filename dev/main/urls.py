
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import FormsStylesView, HomeView, JqueryUIFormStylesView, StylesView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('styles/', StylesView.as_view(), name='styles'),
    path('styles_form/', FormsStylesView.as_view(), name='styles_form'),
    path('styles_form_jquery/', JqueryUIFormStylesView.as_view(), name='styles_form_jquery'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]