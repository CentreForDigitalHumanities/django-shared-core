from django.views.generic import RedirectView, View
from django.http import HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.forms import modelformset_factory


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


class FormSetUpdateView(View):
    """ Generic update view that uses a formset. This allows you to edit
    multiple forms of the same type on the same page.

    Source: ETCL-portal https://github.com/UiL-OTS-labs/etcl (written by Ty
    Mees)
    """
    form = None
    _formset = None
    queryset = None
    succes_url = None
    extra = 0

    def get(self, request, *args, **kwargs):
        self._on_request()
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self._on_request()

        formset = self._formset(
            request.POST,
            request.FILES,
            queryset=self.objects,
        )

        self.pre_validation(formset)
        if formset.is_valid():
            self.save_form(formset)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name,
                          self.get_context_data(formset=formset))

    def pre_validation(self, formset):
        """This method can be overridden to manipulate the formset before
         validation
        """
        pass

    def save_form(self, formset):
        formset.save()

    def _on_request(self):
        self._formset = modelformset_factory(self.form._meta.model,
                                             form=self.form, extra=self.extra)
        self.objects = self.get_queryset()
        self.check_allowed()

    def get_queryset(self):
        if self.queryset is None:
            raise ImproperlyConfigured(
                "Either override get_queryset, or provide a queryset class variable")

        return self.queryset

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        if self.succes_url:
            return self.succes_url

        raise ImproperlyConfigured("Either override get_success_url or "
                                   "provide a success_url in FormSetUpdateView")

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self

        kwargs['objects'] = self.objects

        if 'formset' not in kwargs:
            kwargs['formset'] = self._formset(queryset=self.objects)

        return kwargs
