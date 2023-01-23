from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views import generic

from cdh.integration_platform.digital_identity_api import Identity
from cdh.core.views import RedirectActionView
from .forms import DIATest, DIAUsersTest
from .models import Record


class IPHome(generic.TemplateView):
    template_name = 'dev_integration_platform/index.html'


class DIASimpleTestView(generic.FormView):
    template_name = 'dev_integration_platform/dia/simple.html'
    form_class = DIATest

    def form_valid(self, form):
        identity = None
        does_not_exist = False
        try:
            identity = Identity.client.get(**form.cleaned_data)
        except ObjectDoesNotExist:
            does_not_exist = True


        return self.render_to_response(
            self.get_context_data(
                form=form,
                identity=identity,
                does_not_exist=does_not_exist
            )
        )


class DIAUsersFormTestCreateView(RedirectActionView):

    def action(self, request):
        if Record.objects.count() == 0:
            Record.objects.create()

    def get_redirect_url(self, *args, **kwargs):
        return reverse('dev_integration_platform:dia_users', args=[
            Record.objects.first().pk
        ])


class DIAUsersFormTestView(generic.UpdateView):
    form_class = DIAUsersTest
    model = Record
    template_name = 'dev_integration_platform/dia/users.html'
