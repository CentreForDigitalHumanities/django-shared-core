from django import forms

from dev_files.models import SingleFile, CustomSingleFile


class SingleFileForm(forms.ModelForm):
    class Meta:
        model = SingleFile
        fields = ['required_file', 'nullable_file']


class CustomSingleFileForm(forms.ModelForm):
    class Meta:
        model = CustomSingleFile
        fields = ['required_file', 'nullable_file']
