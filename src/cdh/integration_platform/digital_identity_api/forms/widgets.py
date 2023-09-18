from django.forms import widgets

from cdh.core.file_loading import add_js_file


class SingleUserWidget(widgets.Input):
    input_type = 'hidden'
    template_name = "cdh.integration_platform/digital_identity_api/single_user_widget.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_js_file(
            'cdh.integration_platform/digital_identity_api/single_user_widget'
            '.js'
        )

    @property
    def is_hidden(self):
        return False

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context['widget']['display_value'] = None

        return context
