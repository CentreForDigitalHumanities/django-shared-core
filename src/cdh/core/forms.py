from datetime import date
from typing import List, Optional

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import CheckboxInput, CheckboxSelectMultiple, \
    DateInput, MultiWidget, NumberInput, RadioSelect, Select, TextInput
from django.utils.translation import gettext_lazy as _

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
    # If False, it will supress the is-valid feedback on submit
    show_valid_fields = True

    def get_context(self):
        context = super().get_context()

        form_was_changed = len(self.changed_data) != 0

        for field, errors in context['fields']:
            # Fix for fields that do not set this attr
            if 'class' not in field.field.widget.attrs:
                field.field.widget.attrs['class'] = ''

            field.field.widget.attrs['class'] += ' form-control'

            if errors:
                field.field.widget.attrs['valid'] = 'is-invalid'
                field.field.widget.attrs['class'] += ' is-invalid'
            elif form_was_changed and self.show_valid_fields:
                # Only add if the data on the form was changed, as that would
                # indicate a validation step gone wrong.
                field.field.widget.attrs['class'] += ' is-valid'
                field.field.widget.attrs['valid'] = 'is-valid'

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

    def get_context(self, name, value, attrs):
        if 'class' not in attrs:
            attrs['class'] = ""

        if 'form-control' in attrs['class']:
            attrs['class'] = attrs['class'].replace(
                'form-control',
                'form-select'
            )
        else:
            attrs['class'] += ' form-select'

        return super().get_context(name, value, attrs)


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


class TimeInput(forms.TimeInput):
    """Override of Django's version to use the right HTML5 input"""
    input_type = 'time'


class TimeField(forms.TimeField):
    """Override of Django's version to use the right HTML5 input"""
    widget = TimeInput


class DateTimeInput(forms.DateTimeInput):
    """Override of Django's version to use the right HTML5 input"""
    input_type = 'datetime-local'


class DateTimeField(forms.DateTimeField):
    """Override of Django's version to use the right HTML5 input"""
    widget = DateTimeInput


class BootstrapMultiWidgetMixin:
    template_name = 'cdh.core/forms/widgets/bootstrap_multiwidget.html'

    def get_context(self, name, value, attrs):
        subwidgets = {}
        if 'subwidgets' in self.attrs:
            subwidgets = self.attrs['subwidgets']
        context = super().get_context(name, value, attrs)

        for subwidget_name, subwidget_attrs in subwidgets.items():
            if subwidget_name in context['widget']['subwidgets']:
                context['widget']['subwidgets']['attrs'].update(
                    subwidget_attrs)

        return context


class BootstrapMultiWidget(BootstrapMultiWidgetMixin, MultiWidget):
    pass


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


class BootstrapSplitDateTimeWidget(BootstrapMultiWidgetMixin,
                                   SplitDateTimeWidget):
    pass


class BootstrapSplitDateTimeField(forms.SplitDateTimeField):
    """Override of Django SplitDateTimeField to use bootstrap multiwidget"""
    widget = BootstrapSplitDateTimeWidget


class SplitDateTimeField(forms.SplitDateTimeField):
    """Override of Django SplitDateTimeField to use HTML5 fields"""
    widget = SplitDateTimeWidget


class MonthInput(TextInput):
    input_type = 'month'

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}

        attrs['pattern'] = "[0-9]{4}-[0-9]{1,2}"
        if 'placeholder' not in attrs:
            attrs['placeholder'] = 'yyyy-mm'

        super().__init__(attrs)

    def format_value(self, value):
        from cdh.core.fields.month_fields import Month

        if value == "" or value is None:
            return None
        if isinstance(value, date) or isinstance(value, Month):
            return value.strftime("%Y-%m")
        return value


class SplitMonthInput(BootstrapMultiWidget):

    def __init__(self, attrs=None):
        month_attrs = attrs if attrs else {}

        year_attrs = attrs if attrs else {}
        year_attrs['placeholder'] = _('core:fields:month:year_placeholder')
        if hasattr(year_attrs, 'year_min'):
            year_attrs['min'] = year_attrs.get('year_min')
        if hasattr(year_attrs, 'year_max'):
            year_attrs['max'] = year_attrs.get('year_max')

        widgets = {
            'month': BootstrapSelect(
                attrs=month_attrs,
                choices=(
                    ('', _('core:fields:month:month_placeholder')),
                    (1, _('core:fields:month:january')),
                    (2, _('core:fields:month:february')),
                    (3, _('core:fields:month:march')),
                    (4, _('core:fields:month:april')),
                    (5, _('core:fields:month:may')),
                    (6, _('core:fields:month:june')),
                    (7, _('core:fields:month:july')),
                    (8, _('core:fields:month:august')),
                    (9, _('core:fields:month:september')),
                    (10, _('core:fields:month:october')),
                    (11, _('core:fields:month:november')),
                    (12, _('core:fields:month:december')),
                ),
            ),
            'year': NumberInput(
                attrs=year_attrs,
            ),
        }
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            try:
                return [int(value.month), int(value.year)]
            except ValueError:
                pass

        return [None, None]


class BootstrapMonthField(forms.DateField):
    widget = MonthInput

    def __init__(self, year_min=1970, year_max=9999, **kwargs):
        super().__init__(**kwargs)

        # We can only do this stuff if we are sure what widget we are using
        if isinstance(self.widget, MonthInput):
            # This could be done in widget_attrs, but the other widget cannot
            # be done there, so I prefer to keep them together
            self.widget.attrs['min'] = f"{year_min}-01"
            self.widget.attrs['max'] = f"{year_max}-12"
        if isinstance(self.widget, SplitMonthInput):
            # We have to manually set these attrs to the right widget,
            # as MultiWidget has not other way to set these
            month_widget, year_widget = self.widget.widgets
            year_widget.attrs['min'] = year_min
            year_widget.attrs['max'] = year_max

    def to_python(self, value):
        if value is None or value == "":
            return None

        # MonthInput returns a string
        if isinstance(value, str):
            try:
                year, month = value.split('-', maxsplit=1)

                year = int(year)
                month = int(month)
                # Validate the month is in a valid range
                if month > 12 or month < 1:
                    raise ValidationError(
                        self.error_messages["invalid"], code="invalid"
                    )
            # Catches both the int conversions, and the cases where splitting
            # doesn't work
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages["invalid"], code="invalid"
                )
        else:
            # SplitMonthInput returns a list of [month, year]
            month, year = value

            if month is None or year is None or month == "" or year == "":
                return None

            try:
                year = int(year)
                month = int(month)
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages["invalid"], code="invalid"
                )

        try:
            if month and year:
                # Local import to avoid circular imports
                from cdh.core.fields.month_fields import Month

                return Month(year, month)
        except ValueError:
            raise ValidationError(
                self.error_messages["invalid"], code="invalid"
            )

        raise ValidationError(self.error_messages["invalid"], code="invalid")


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

