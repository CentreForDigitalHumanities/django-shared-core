from django.urls import reverse
from django.views import generic

from cdh.files.views import BaseFieldLimitedFileView, BaseFileView

from .models import CustomFile, SingleFile, CustomSingleFile, TrackedCustomFile, \
    TrackedFile
from .forms import CustomSingleFileForm, SingleFileForm, TrackedCustomFileForm, \
    TrackedFileForm


class SingleFileListView(generic.ListView):
    model = SingleFile

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['title'] = 'Single file list'
        context['new_url'] = reverse('dev_files:single_create')
        context['update_url_name'] = 'dev_files:single_update'

        return context


class CustomSingleFileListView(generic.ListView):
    model = CustomSingleFile
    template_name = 'dev_files/singlefile_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['title'] = 'Custom single file list'
        context['new_url'] = reverse('dev_files:customsingle_create')
        context['update_url_name'] = 'dev_files:customsingle_update'

        return context


class SingleFileCreateView(generic.CreateView):
    model = SingleFile
    form_class = SingleFileForm

    def get_success_url(self):
        return reverse('dev_files:single_update', args=[self.object.pk])


class SingleFileUpdateView(generic.UpdateView):
    model = SingleFile
    form_class = SingleFileForm

    def get_success_url(self):
        return reverse('dev_files:single_update', args=[self.object.pk])


class CustomSingleFileCreateView(generic.CreateView):
    model = CustomSingleFile
    form_class = CustomSingleFileForm
    template_name = 'dev_files/singlefile_form.html'

    def get_success_url(self):
        return reverse('dev_files:customsingle_update', args=[self.object.pk])


class CustomSingleFileUpdateView(generic.UpdateView):
    model = CustomSingleFile
    form_class = CustomSingleFileForm
    template_name = 'dev_files/singlefile_form.html'

    def get_success_url(self):
        return reverse('dev_files:customsingle_update', args=[self.object.pk])


class FileView(BaseFileView):
    pass


class CustomFileView(FileView):
    file_class = CustomFile


class FieldLimitedSingleFileView(BaseFieldLimitedFileView):
    model = SingleFile
    model_field_name = 'required_file'


class FieldLimitedTrackedFileView(BaseFieldLimitedFileView):
    model = TrackedFile
    model_field_name = 'files'


class TrackedFileListView(generic.ListView):
    model = TrackedFile

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['title'] = 'Tracked file list'
        context['new_url'] = reverse('dev_files:tracked_create')
        context['update_url_name'] = 'dev_files:tracked_update'

        return context


class CustomTrackedFileListView(generic.ListView):
    model = TrackedCustomFile
    template_name = 'dev_files/trackedfile_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['title'] = 'Custom tracked file list'
        context['new_url'] = reverse('dev_files:customtracked_create')
        context['update_url_name'] = 'dev_files:customtracked_update'

        return context


class TrackedFileCreateView(generic.CreateView):
    model = TrackedFile
    form_class = TrackedFileForm

    def get_success_url(self):
        return reverse('dev_files:tracked_update', args=[self.object.pk])


class TrackedFileUpdateView(generic.UpdateView):
    model = TrackedFile
    form_class = TrackedFileForm

    def get_success_url(self):
        return reverse('dev_files:tracked_update', args=[self.object.pk])


class TrackedCustomFileCreateView(generic.CreateView):
    model = TrackedCustomFile
    form_class = TrackedCustomFileForm
    template_name = 'dev_files/trackedfile_form.html'

    def get_success_url(self):
        return reverse('dev_files:customtracked_update', args=[self.object.pk])


class TrackedCustomFileUpdateView(generic.UpdateView):
    model = TrackedCustomFile
    form_class = TrackedCustomFileForm
    template_name = 'dev_files/trackedfile_form.html'

    def get_success_url(self):
        return reverse('dev_files:customtracked_update', args=[self.object.pk])
