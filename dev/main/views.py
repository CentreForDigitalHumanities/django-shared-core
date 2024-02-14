from django.urls import reverse
from django.views import generic
from django.contrib.messages import debug, info, success, warning, error

from cdh.core.mail import BaseEmailPreviewView
from cdh.core.views import RedirectActionView
from .emails import ExampleCustomTemplateEmail
from .forms import CustomEmailForm, CustomTemplateFormStylesForm, \
    FormStylesForm, \
    JqueryUIFormStylesForm, MonthFieldTestForm
from .models import MonthFieldTest


class HomeView(generic.TemplateView):
    template_name = 'main/index.html'


class StylesView(generic.TemplateView):
    template_name = 'main/styles.html'

    def get_context_data(self, **kwargs):
        debug(
            self.request,
            "This is a sample Django Messages debug message"
        )
        info(
            self.request,
            "This is a sample Django Messages info message"
        )
        success(
            self.request,
            "This is a sample Django Messages success message"
        )
        warning(
            self.request,
            "This is a sample Django Messages warning message"
        )
        error(
            self.request,
            "This is a sample Django Messages error message"
        )
        return super().get_context_data(**kwargs)


class CustomEmailFormView(generic.FormView):
    form_class = CustomEmailForm
    template_name = 'main/custom_email.html'

    def get_initial(self):
        initial = super().get_initial()

        initial['sender'] = "DH-IT Portal Development"
        initial['banner'] = "New test email!"
        initial['footer'] = "<em>This email is for testing purposes only, " \
                            "and will annoy you if you try to reply to it</em>"
        initial['contents'] = """<h2>Hello {{ name }}</h2>
<p>
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed urna risus, 
placerat sed ornare et, tempor nec nibh. Aenean dictum tincidunt dapibus. 
Aliquam sed efficitur lectus. Vestibulum ornare tellus volutpat, consequat 
lacus in, tempus dolor. In faucibus, neque nec laoreet rhoncus, nunc magna 
efficitur lectus, a sagittis ex lacus vel erat. Donec tempus finibus molestie. 
Nam vel eleifend sem. 
</p>
<p>
In malesuada at neque at placerat. Suspendisse nisi quam, vehicula eget 
sapien sit amet, volutpat pellentesque lacus. Aliquam vel tortor vel magna 
sagittis semper. Fusce non sagittis erat, a semper augue. Cras hendrerit mi 
in imperdiet pellentesque. Morbi dictum malesuada quam, nec tincidunt sem. 
Class aptent taciti sociosqu ad litora torquent per conubia nostra, 
per inceptos himenaeos. Mauris efficitur accumsan accumsan. Nunc ex erat, 
feugiat non viverra at, finibus vulputate leo. Mauris non quam imperdiet, 
ultrices eros non, sagittis augue. Proin ornare accumsan pretium. Phasellus 
id sodales ligula, et semper turpis. Nullam nec arcu sodales nisi vehicula 
pulvinar. Phasellus velit lacus, viverra vel suscipit a, dapibus in mi. 
Curabitur in turpis eleifend, sollicitudin nunc non, efficitur magna. 
</p>"""

        return initial


class CustomEmailPreviewView(BaseEmailPreviewView):
    email_class = ExampleCustomTemplateEmail


class FormsStylesView(generic.FormView):
    form_class = FormStylesForm
    template_name = 'main/styles_form.html'


class CustomTemplateFormsStylesView(generic.FormView):
    form_class = CustomTemplateFormStylesForm
    template_name = 'main/custom_styles_form.html'


class JqueryUIFormStylesView(generic.FormView):
    form_class = JqueryUIFormStylesForm
    template_name = 'main/jqueryui_styles_form.html'


class MonthFieldTestView(generic.UpdateView):
    model = MonthFieldTest
    form_class = MonthFieldTestForm
    template_name = 'main/month_field_test.html'

    def get_object(self, queryset=None):
        if MonthFieldTest.objects.count() == 0:
            MonthFieldTest.objects.create()

        return MonthFieldTest.objects.first()

    def get_success_url(self):
        return reverse('main:month_field_test')


class MonthFieldClearView(RedirectActionView):

    def action(self, request):
        MonthFieldTest.objects.first().delete()

    def get_redirect_url(self, *args, **kwargs):
        return reverse('main:month_field_test')
