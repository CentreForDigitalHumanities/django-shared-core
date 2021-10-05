from django.urls import path

from .views import CustomSingleFileCreateView, CustomSingleFileListView, \
    CustomSingleFileUpdateView, SingleFileCreateView, \
    SingleFileListView, SingleFileUpdateView

app_name = 'dev_files'

urlpatterns = [
    path('single/all/', SingleFileListView.as_view(), name='single_list'),
    path('custom-single/all/', CustomSingleFileListView.as_view(),
         name='customsingle_list'),
    path('single/', SingleFileCreateView.as_view(), name='single_create'),
    path('custom-single/', CustomSingleFileCreateView.as_view(),
         name='customsingle_create'),
    path('single/<int:pk>/', SingleFileUpdateView.as_view(),
         name='single_update'),
    path('custom-single/<int:pk>/', CustomSingleFileUpdateView.as_view(),
         name='customsingle_update'),
]
