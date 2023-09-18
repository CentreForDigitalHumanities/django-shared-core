from djangosaml2.views import LoginView, LogoutInitView
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import CustomEmailFormView, CustomEmailPreviewView, \
    CustomTemplateFormsStylesView, \
    FormsStylesView, HomeView, \
    JqueryUIFormStylesView, MonthFieldClearView, MonthFieldTestView, StylesView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('styles/', StylesView.as_view(), name='styles'),
    path('styles_form/', FormsStylesView.as_view(), name='styles_form'),
    path(
        'styles_form_custom/',
        CustomTemplateFormsStylesView.as_view(),
        name='custom_styles_form'
    ),
    path('styles_form_jquery/', JqueryUIFormStylesView.as_view(), name='styles_form_jquery'),
    path('custom_email_form/', CustomEmailFormView.as_view(),
         name='custom_email_form'),
    path('custom_email_form/preview/', CustomEmailPreviewView.as_view(),
         name='custom_email_form_preview'),
    path('month_field_test/', MonthFieldTestView.as_view(),
         name='month_field_test'),
    path('month_field_test/clear/', MonthFieldClearView.as_view(),
         name='month_field_test_clear'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutInitView.as_view(), name='logout'),
]
