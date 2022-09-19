from django.http import HttpResponse
from django.views import generic


class BaseEmailPreviewView(generic.View):
    """Base view for viewing previews of custom emails

    :param email_class: the specific class to render
    """
    email_class = None

    def post(self, request):
        kwargs = {
            'to':       'example@example.org',
            'subject':  'Test Email',
            'contents': request.POST.get('contents', None),
            'sender':   request.POST.get('sender', None),
            'banner':   request.POST.get('banner', None),
            'footer':   request.POST.get('footer', None),
            'context':  self.get_preview_context(),
        }

        msg = self.email_class(**kwargs)

        return HttpResponse(msg.render_preview())

    def get_preview_context(self):
        """A method to provide any additional context to the preview email.

        Most of this _should_ be handled by the email class itself, but this
        method can be used if you want some dynamic defaults. Any defaults
        specified in the Email class will be overwritten by data supplied here.
        """
        return {}
