from django.forms.widgets import FileInput
from django.utils.translation import gettext_lazy as _

from uil.core.file_loading import add_css_file, add_js_file


class SimpleFileInput(FileInput):
    clear_checkbox_label = _('Clear')
    initial_text = _('Currently')
    input_text = _('Change')
    template_name = 'uil.files/widgets/file.html'

    # We get these values as string from the HTTP packet
    CHANGED = '1'
    NOT_CHANGED = '0'

    # Strings used in the template
    strings = {
        'empty_file': _('Please select a file'),
        'remove': _('Clear'),
        'select_file': _('Select File'),
    }

    def __init__(self, attrs=None):
        """Update strings from attrs if present"""
        if attrs:
            self.strings.update(attrs.pop('strings', {}))

        add_js_file('uil.files/widgets.js')
        add_css_file('uil.files/widgets.css')

        super().__init__(attrs)

    def format_value(self, value):
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

        # If ID is not set, an empty string is returned. In which case we set
        # it to None, as it's a bit nicer to work with
        if not uuid:
            uuid = None

        return file, uuid, changed

    def value_omitted_from_data(self, data, files, name):
        changed = data.get(f"{name}_changed") == self.CHANGED
        # If we don't see ourselves in the files-dict OR the data dict
        # indicates nothing changed, act like we didn't get any data
        return name not in files or not changed

