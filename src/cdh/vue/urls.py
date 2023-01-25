from django.urls import path

from .views import VueJSView, VueCSSView

app_name = 'cdh.vue'

urlpatterns = [
    path("js/<str:component>/", VueJSView.as_view(), name='vue-js'),
    path("css/<str:component>/", VueCSSView.as_view(), name='vue-css'),
]