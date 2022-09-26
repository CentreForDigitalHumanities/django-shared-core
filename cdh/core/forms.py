from typing import List, Optional

from django import forms
from django.forms.widgets import CheckboxInput, CheckboxSelectMultiple, \
    RadioSelect, Select

from cdh.core.file_loading import add_js_file


class TemplatedFormMixin:
    """Mixin for Django Form to enable the UU-Form styling

    :param str form_template: the form_template to use
    :param bool show_help_column: if False, the help column will be removed on
                                  every field
    :param bool always_show_help_column: if False, the help column will be
                                         removed on fields that don't have help
                                         texts
    """

    template_name = 'cdh.core/form_template.html'
    # If False, it will hide the help column on every field
    show_help_column = True
    # If False, it will hide the help column on fields without a help text
    always_show_help_column = True

    def get_context(self):
        context = super().get_context()

        for field, errors in context['fields']:
            if errors:
                field.field.widget.attrs['class'] = 'form-control is-invalid'
            else:
                field.field.widget.attrs['class'] = 'form-control'

        context['show_help_column'] = self.show_help_column
        context['always_show_help_column'] = self.always_show_help_column

        return context


class TemplatedForm(TemplatedFormMixin, forms.Form):
    """Extension of the default Form to enable the UU-Form styling

    Uses :class:`.TemplatedFormMixin`
    """
    pass


class TemplatedModelForm(TemplatedFormMixin, forms.ModelForm):
    """Extension of the default Form to enable the UU-Form styling

    Uses :class:`.TemplatedFormMixin`
    """
    pass


class BootstrapSelect(Select):
    """Override of Django's version to use the right Bootstrap classes"""

    def get_context(self, *args, **kwargs):
        if 'form-control' in self.attrs['class']:
            self.attrs['class'] = self.attrs['class'].replace(
                'form-control',
                'form-select'
            )
        else:
            self.attrs['class'] += ' form-select'

        return super().get_context(*args, **kwargs)


class BootstrapCheckboxInput(CheckboxInput):
    """Override of Django's version to use the right Bootstrap classes"""
    template_name = "cdh.core/forms/widgets/bootstrap_checkbox.html"


class BootstrapRadioSelect(RadioSelect):
    """Override of Django's version to use the right Bootstrap classes"""
    template_name = "cdh.core/forms/widgets/bootstrap_radio.html"
    option_template_name = "cdh.core/forms/widgets/bootstrap_radio_option.html"


class BootstrapCheckboxSelectMultiple(CheckboxSelectMultiple):
    """Override of Django's version to use the right Bootstrap classes"""
    template_name = "cdh.core/forms/widgets/bootstrap_radio.html"
    option_template_name = "cdh.core/forms/widgets/bootstrap_radio_option.html"


class PasswordField(forms.CharField):
    """Override of Django's version to use the right HTML5 input"""
    widget = forms.PasswordInput


class ColorInput(forms.TextInput):
    """Override of Django's version to use the right HTML5 input"""
    input_type = 'color'


class ColorField(forms.CharField):
    """Override of Django's version to use the right HTML5 input"""
    widget = ColorInput


class TelephoneInput(forms.TextInput):
    """Override of Django's version to use the right HTML5 input"""
    input_type = 'tel'


class TelephoneField(forms.CharField):
    """Override of Django's version to use the right HTML5 input"""
    widget = TelephoneInput


class DateInput(forms.DateInput):
    """Override of Django's version to use the right HTML5 input"""
    input_type = 'date'


class DateField(forms.DateField):
    """Override of Django's version to use the right HTML5 input"""
    widget = DateInput


class TimeInput(forms.DateInput):
    """Override of Django's version to use the right HTML5 input"""
    input_type = 'time'


class TimeField(forms.DateField):
    """Override of Django's version to use the right HTML5 input"""
    widget = TimeInput


class DateTimeInput(forms.DateTimeInput):
    """Override of Django's version to use the right HTML5 input"""
    input_type = 'datetime-local'


class DateTimeField(forms.DateField):
    """Override of Django's version to use the right HTML5 input"""
    widget = DateTimeInput


class SplitDateTimeWidget(forms.SplitDateTimeWidget):
    """Override of Django SplitDateTimeWidget to use HTML5 fields"""
    def __init__(self, attrs=None, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
        widgets = (
            DateInput(
                attrs=attrs if date_attrs is None else date_attrs,
                format=date_format,
            ),
            TimeInput(
                attrs=attrs if time_attrs is None else time_attrs,
                format=time_format,
            ),
        )
        forms.MultiWidget.__init__(self, widgets)


class SplitDateTimeField(forms.SplitDateTimeField):
    """Override of Django SplitDateTimeField to use HTML5 fields"""
    widget = SplitDateTimeWidget


class TinyMCEWidget(forms.Widget):
    """A TinyMCE widget for HTML editting"""
    template_name = "cdh.core/forms/widgets/tinymce.html"

    def __init__(
            self,
            menubar: bool = False,
            plugins: Optional[List[str]] = None,
            toolbar: Optional[str] = 'undo redo casechange blocks bold '
                                     'italic underline link bullist numlist'
                                     ' | code',
            *args,
            **kwargs
    ):
        """
        All parameters should have sensible defaults.

        :param bool menubar: if the TinyMCE menubar needs to be shown.
                             Probably not
        :param plugins: a list of TinyMCE plugins to load
        :param str plugins: a TinyMCE toolbar definition
        """
        super().__init__(*args, **kwargs)

        if plugins is None:
            plugins = [
                'link', 'image', 'visualblocks', 'wordcount', 'lists', 'code',
            ]

        self.menubar = menubar
        self.plugins = plugins
        self.toolbar = toolbar

        add_js_file('cdh.core/js/tinymce/tinymce.min.js')
        add_js_file('cdh.core/js/tinymce/tinymce-jquery.min.js')
        add_js_file('cdh.core/js/tinymce/shim.js')

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)

        context['menubar'] = self.menubar
        context['plugins'] = ",".join(self.plugins)
        context['toolbar'] = self.toolbar

        return context

