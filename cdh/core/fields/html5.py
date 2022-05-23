from django import forms


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
