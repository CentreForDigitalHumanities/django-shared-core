from django.urls import path

from .views import ExampleDataListView, ListView

app_name = "dev_vue"

urlpatterns = [
    path("uu-list/", ListView.as_view(), name="list"),
    path("uu-list/<int:pk>/", ListView.as_view(), name="dummy"),
    path("api/data/", ExampleDataListView.as_view(), name="data"),
]
