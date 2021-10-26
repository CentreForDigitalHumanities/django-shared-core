from django.views import generic
from django.contrib.messages import debug, info, success, warning, error

from .forms import FormStylesForm, JqueryUIFormStylesForm


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


class FormsStylesView(generic.FormView):
    form_class = FormStylesForm
    template_name = 'main/styles_form.html'


class JqueryUIFormStylesView(generic.FormView):
    form_class = JqueryUIFormStylesForm
    template_name = 'main/jqueryui_styles_form.html'
