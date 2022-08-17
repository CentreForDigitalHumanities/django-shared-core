from django import forms
from django.forms.widgets import CheckboxInput, CheckboxSelectMultiple, \
    RadioSelect


class TemplatedFormMixin:
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
    pass


class TemplatedModelForm(TemplatedFormMixin, forms.ModelForm):
    pass


class BootstrapCheckboxInput(CheckboxInput):
    template_name = "cdh.core/forms/widgets/bootstrap_checkbox.html"


class BootstrapRadioSelect(RadioSelect):
    template_name = "cdh.core/forms/widgets/bootstrap_radio.html"
    option_template_name = "cdh.core/forms/widgets/bootstrap_radio_option.html"


class BootstrapCheckboxSelectMultiple(CheckboxSelectMultiple):
    template_name = "cdh.core/forms/widgets/bootstrap_radio.html"
    option_template_name = "cdh.core/forms/widgets/bootstrap_radio_option.html"


class PasswordField(forms.CharField):
    widget = forms.PasswordInput


class ColorInput(forms.TextInput):
    input_type = 'color'


class ColorField(forms.CharField):
    widget = ColorInput


class TelephoneInput(forms.TextInput):
    input_type = 'tel'


class TelephoneField(forms.CharField):
    widget = TelephoneInput


class DateInput(forms.DateInput):
    input_type = 'date'


class DateField(forms.DateField):
    widget = DateInput


class TimeInput(forms.DateInput):
    input_type = 'time'


class TimeField(forms.DateField):
    widget = TimeInput


class DateTimeInput(forms.DateInput):
    input_type = 'datetime-local'


class DateTimeField(forms.DateField):
    widget = DateTimeInput


class SplitDateTimeWidget(forms.SplitDateTimeWidget):
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
    widget = SplitDateTimeWidget
