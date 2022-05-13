from django.forms.widgets import CheckboxInput, FILE_INPUT_CONTRADICTION, \
    FileInput
from django.utils.translation import gettext_lazy as _


class SimpleFileInput(FileInput):
    clear_checkbox_label = _('Clear')
    initial_text = _('Currently')
    input_text = _('Change')
    template_name = 'cdh.files/widgets/file.html'

    CHANGED = '1'
    NOT_CHANGED = '0'

    strings = {
        'empty_file': _('Please select a file'),
        'remove': _('Clear'),
        'select_file': _('Select File'),
    }

    def __init__(self, attrs=None):
        """Update strings from attrs if present"""
        if attrs:
            self.strings.update(attrs.pop('strings', {}))
        super().__init__(attrs)

    def format_value(self, value):
        """
        Return the file object if it has a defined url attribute.
        """
        return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'strings': self.strings,
            'input_text': self.input_text,
            'initial_text': self.initial_text,
            'clear_checkbox_label': self.clear_checkbox_label,
        })
        return context

    def value_from_datadict(self, data, files, name):
        file = files.get(name)
        uuid = data.get(f"{name}_id")
        changed = data.get(f"{name}_changed") == self.CHANGED
        return file, uuid, changed

    def value_omitted_from_data(self, data, files, name):
        changed = data.get(f"{name}_changed") == self.CHANGED
        return name not in files or not changed

    def value_from_datadict_old(self, data, files, name):
        upload = super().value_from_datadict(data, files, name)
        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):

            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False

        return upload
