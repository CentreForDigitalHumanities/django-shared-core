from django.views.generic import RedirectView


class RedirectActionView(RedirectView):

    def action(self, request):
        """
        Override this method to perform any action you want to do in this
        view
        """

    def get(self, request, *args, **kwargs):
        self.action(request)
        super(RedirectActionView, self).get(request, *args, **kwargs)
