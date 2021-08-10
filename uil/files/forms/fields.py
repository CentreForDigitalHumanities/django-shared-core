from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist, \
    ValidationError
from django.forms import Field
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .widgets import SimpleFileInput
from ..utils import get_storage


class FileField(Field):
    """Form field for the uil.files.db.FileField"""
    class Data:
        """Inline object to keep info neat and tidy during templating"""
        def __init__(self, filename=None, uuid=None, pk=None):
            self.filename = filename
            self.pk = pk
            self.uuid = uuid
            self.existing = False

        def __repr__(self):
            """Custom repr for easier debugging. (Mostly to see it's values
            in the debug toolbar)
            """
            return f"<FileField.Data: pk={self.pk}; filename={self.filename}; " \
                   f"uuid={self.uuid}; existing={self.existing}>"

    widget = SimpleFileInput
    default_error_messages = {
        'invalid': _("No file was submitted. Check the encoding type on the form."),
        'missing': _("No file was submitted."),
        'empty': _("The submitted file is empty."),
        'max_length': _(
            'Ensure this filename has at most %(max)d character (it has %(length)d).',
            'Ensure this filename has at most %(max)d characters (it has %(length)d).',
            'max'),
        'contradiction': _('Please either submit a file or check the clear checkbox, not both.')
    }

    def __init__(self, queryset, *, max_length=None, allow_empty_file=False,
                 **kwargs):
        self.queryset = queryset
        self.max_length = max_length
        self.allow_empty_file = allow_empty_file
        if 'limit_choices_to' in kwargs:
            del kwargs['limit_choices_to']
        super().__init__(**kwargs)

    @cached_property
    def storage(self):
        return get_storage()

    def to_python(self, data):
        # Handle no incoming data
        if not data:
            if self.required:
                raise ValidationError(self.error_messages['missing'], code='missing')
            else:
                return data

        file, uuid, changed = data

        # If we don't have a file or an UUID, we say we didn't get any data
        if uuid in self.empty_values and file in self.empty_values:
            return None

        # If nothing changed, stop processing
        if not changed:
            return data

        # UploadedFile objects should have name and size attributes.
        try:
            file_name = file.name
            file_size = file.size
        except AttributeError:
            raise ValidationError(self.error_messages['invalid'], code='invalid')

        if self.max_length is not None and len(file_name) > self.max_length:
            params = {'max': self.max_length, 'length': len(file_name)}
            raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)
        if not file_name:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        if not self.allow_empty_file and not file_size:
            raise ValidationError(self.error_messages['empty'], code='empty')

        return data

    def clean(self, data, initial=None):
        file, uuid, changed = data
        # Changed = True and file is None means the field value should be
        # cleared; further validation is not needed.
        if file is None and changed:
            if not self.required:
                return None
            # If the field is required, clearing is not possible (the widget
            # shouldn't return False data in that case anyway). False is not
            # in self.empty_value; if a False value makes it this far
            # it should be validated from here on out as None (so it will be
            # caught by the required check).
            data = None
        if not file and initial:
            return initial
        return super().clean(data)

    def prepare_value(self, value):
        ret = self.Data()
        if self.queryset:
            try:
                # If value is a data-tuple from get_value_from_datadict,
                # try to use the UUID of that tuple to retrieve our model
                if isinstance(value, tuple):
                    # Check if we actaully have a UUID
                    if value[1]:
                        model = self.queryset.get(uuid=value[1])
                    else:
                        # If not, return the empty Data()
                        return ret
                else:
                    # Otherwise, we assume we got a PK from the form
                    model = self.queryset.get(pk=value)
                # Fill in our data class
                ret.filename = model.original_filename
                ret.pk = model.pk
                ret.uuid = model.uuid
                ret.existing = True
            except ObjectDoesNotExist:
                pass
            except AttributeError:
                raise ImproperlyConfigured("This field somehow didn't get a "
                                           "File-derived model?")
        return ret

    def bound_data(self, data, initial):
        if data in (None, FILE_INPUT_CONTRADICTION):
            return initial
        return data

    def has_changed(self, initial, data):
        return not self.disabled and data is not None
