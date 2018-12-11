from django.views.generic import RedirectView


class RedirectActionView(RedirectView):
    """This base view extends generic.RedirectView by adding a new method
    that is called before getting the redirect url.

    To be used for redirectViews that handle an action during it's request,
    as an alternative to doing that stuff in get_redirect_url. (It's cleaner)
    """

    def action(self, request):
        """
        Override this method to perform any action you want to do in this
        view
        """

    def get(self, request, *args, **kwargs):
        self.action(request)
        return super(RedirectActionView, self).get(request, *args, **kwargs)
