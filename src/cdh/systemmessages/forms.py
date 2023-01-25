from django import forms

from cdh.core.forms import DateTimeInput, BootstrapSelect, TinyMCEWidget, \
    TemplatedModelForm

from .models import SystemMessage


class SystemMessageForm(TemplatedModelForm):
    """A Form apps can use to quickly setup creation/editing in their user
    interface, in addition to the Django Admin integration."""
    class Meta:
        model = SystemMessage
        fields = '__all__'
        widgets = {
            # We can't filter this out by omitting it from fields, so we hide
            # it instead
            'message': forms.HiddenInput,
            'message_en': TinyMCEWidget,
            'message_nl': TinyMCEWidget,
            'color': BootstrapSelect,
            'not_before': DateTimeInput,
            'not_after': DateTimeInput,
        }



