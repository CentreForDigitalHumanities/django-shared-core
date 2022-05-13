from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist, \
    ValidationError
from django.forms import Field, ModelChoiceField
from django.forms.widgets import FILE_INPUT_CONTRADICTION, MultipleHiddenInput
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .widgets import SimpleFileInput, TrackedFileInput
from ..utils import get_storage
from ..db.wrappers import FileWrapper


class FileField(Field):
    """Form field for the cdh.files.db.FileField"""
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
        ret = None
        if self.queryset is not None:
            try:
                # If value is a data-tuple from get_value_from_datadict,
                # try to use the UUID of that tuple to retrieve our model
                if isinstance(value, tuple):
                    # Check if we actually have a UUID
                    if value[1]:
                        model = self.queryset.get(uuid=value[1])
                        return model.get_file_wrapper()
                    else:
                        # If not, return None
                        return ret
                else:
                    # Otherwise, we assume we got a PK from the form
                    model = self.queryset.get(pk=value)
                    return model.get_file_wrapper()
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


class TrackedFileField(ModelChoiceField):
    """A MultipleChoiceField whose choices are a model QuerySet."""
    widget = TrackedFileInput
    hidden_widget = MultipleHiddenInput
    default_error_messages = {
        'invalid_list': _('Enter a list of values.'),
        'invalid_choice': _('Select a valid choice. %(value)s is not one of the'
                            ' available choices.'),
        'invalid_pk_value': _('“%(pk)s” is not a valid value.')
    }

    def __init__(self, queryset, **kwargs):
        super().__init__(queryset, empty_label=None, **kwargs)

    def to_python(self, value):
        if not value:
            return []
        return list(self._check_values(value))

    def clean(self, value):
        value = self.prepare_value(value)
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')
        elif not self.required and not value:
            return self.queryset.none()
        if not isinstance(value, (list, tuple)):
            raise ValidationError(
                self.error_messages['invalid_list'],
                code='invalid_list',
            )
        qs = self._check_values(value)
        # Since this overrides the inherited ModelChoiceField.clean
        # we run custom validators here
        self.run_validators(value)
        return qs

    def _check_values(self, value):
        """
        Given a list of possible PK values, return a QuerySet of the
        corresponding objects. Raise a ValidationError if a given value is
        invalid (not a valid PK, not in the queryset, etc.)
        """
        key = self.to_field_name or 'pk'
        # deduplicate given values to avoid creating many querysets or
        # requiring the database backend deduplicate efficiently.
        try:
            value = frozenset(value)
        except TypeError:
            # list of lists isn't hashable, for example
            raise ValidationError(
                self.error_messages['invalid_list'],
                code='invalid_list',
            )
        for pk in value:
            try:
                self.queryset.filter(**{key: pk})
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages['invalid_pk_value'],
                    code='invalid_pk_value',
                    params={'pk': pk},
                )
        qs = self.queryset.filter(**{'%s__in' % key: value})
        pks = {str(getattr(o, key)) for o in qs}
        for val in value:
            if str(val) not in pks:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )
        return qs

    def prepare_value(self, value):
        if (hasattr(value, '__iter__') and
                not isinstance(value, str) and
                not hasattr(value, '_meta')):
            return [self._prepare_value(v) for v in value]
        return self._prepare_value(value)

    def _prepare_value(self, value):
        if isinstance(value, FileWrapper):
            return value

        if hasattr(value, '_meta'):
            if self.to_field_name:
                return value.serializable_value(self.to_field_name)
            else:
                return value.pk
        return super().prepare_value(value)

    def has_changed(self, initial, data):
        if self.disabled:
            return False
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = {str(value) for value in self.prepare_value(initial)}
        data_set = {str(value) for value in data}
        return data_set != initial_set
