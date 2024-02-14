from django.forms import widgets

from cdh.core.file_loading import add_js_file


class SingleUserWidget(widgets.Input):
    class Media:
        js = [
            'cdh.integration_platform/digital_identity_api/single_user_widget.js'
        ]
    input_type = 'hidden'
    template_name = "cdh.integration_platform/digital_identity_api/single_user_widget.html"

    @property
    def is_hidden(self):
        return False

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context['widget']['display_value'] = None

        return context
