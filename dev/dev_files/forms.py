from django import forms

from dev_files.models import SingleFile, CustomSingleFile, TrackedCustomFile, \
    TrackedFile


class SingleFileForm(forms.ModelForm):
    template_name = 'cdh.core/form_template.html'

    class Meta:
        model = SingleFile
        fields = ['required_file', 'nullable_file']


class CustomSingleFileForm(forms.ModelForm):
    class Meta:
        model = CustomSingleFile
        fields = ['required_file', 'nullable_file']


class TrackedFileForm(forms.ModelForm):
    template_name = 'cdh.core/form_template.html'
    
    class Meta:
        model = TrackedFile
        fields = ['files', ]


class TrackedCustomFileForm(forms.ModelForm):
    class Meta:
        model = TrackedCustomFile
        fields = ['files', ]
