from typing import Optional

from cdh.core.file_loading import add_js_file
from cdh.core.forms import TinyMCEWidget


class EmailContentEditWidget(TinyMCEWidget):
    """A custom widget to handle editing custom email templates using TinyMCE.

    At the moment this should only be used on the 'contents' template.

    Will add a 'preview email' button to the editor.
    """

    def __init__(
            self,
            preview_url,
            *args,
            sender_field: Optional[str] = None,
            banner_field: Optional[str] = None,
            footer_field: Optional[str] = None,
            **kwargs
    ):
        """
        :param preview_url: a resolved URL for the EmailPreviewView to use
        :param sender_field: (optional) the formfield describing the 'sender'
                             template
        :param banner_field: (optional) the formfield describing the 'banner'
                             template
        :param footer_field: (optional) the formfield describing the 'footer'
                             template
        """
        super().__init__(*args, **kwargs)

        self.preview_url = preview_url
        self.sender_field = sender_field
        self.banner_field = banner_field
        self.footer_field = footer_field

        self.toolbar += " | preview-mail"
        self.plugins.append('preview-mail')

        add_js_file('cdh.core/js/tinymce-preview-mail-plugin.js')

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)

        context['preview_url'] = self.preview_url
        context['sender_field'] = self.sender_field
        context['banner_field'] = self.banner_field
        context['footer_field'] = self.footer_field

        return context
