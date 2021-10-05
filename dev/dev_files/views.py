from django.urls import reverse
from django.views import generic

from .models import SingleFile, CustomSingleFile
from .forms import CustomSingleFileForm, SingleFileForm


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
