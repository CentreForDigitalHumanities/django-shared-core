from django.urls import path

from .views import CustomFileView, CustomSingleFileCreateView, \
    CustomSingleFileListView, \
    CustomSingleFileUpdateView, CustomTrackedFileListView, \
    FieldLimitedSingleFileView, FieldLimitedTrackedFileView, FileView, \
    SingleFileCreateView, \
    SingleFileListView, SingleFileUpdateView, TrackedCustomFileCreateView, \
    TrackedCustomFileUpdateView, TrackedFileCreateView, \
    TrackedFileListView, TrackedFileUpdateView

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

    path('tracked/all/', TrackedFileListView.as_view(), name='tracked_list'),
    path('custom-tracjed/all/', CustomTrackedFileListView.as_view(),
         name='customtracked_list'),
    path('tracked/', TrackedFileCreateView.as_view(), name='tracked_create'),
    path('custom-tracked/', TrackedCustomFileCreateView.as_view(),
         name='customtracked_create'),
    path('tracked/<int:pk>/', TrackedFileUpdateView.as_view(),
         name='tracked_update'),
    path('custom-tracked/<int:pk>/', TrackedCustomFileUpdateView.as_view(),
         name='customtracked_update'),

    path('file/<uuid:uuid>/', FileView.as_view(), name='file_view'),
    path('custom-file/<uuid:uuid>/', CustomFileView.as_view(),
         name='custom_file_view'),
    path('field-limited-file/<uuid:uuid>/',
         FieldLimitedSingleFileView.as_view(),
         name='field_limited_file_view'),
    path('field-limited-tracked-file/<uuid:uuid>/',
         FieldLimitedTrackedFileView.as_view(),
         name='field_limited_tracked_file_view'),
]
