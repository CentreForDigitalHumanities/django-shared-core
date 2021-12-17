from django.views import generic
from django.urls import reverse



class BlueprintView(generic.DetailView):

    template_name = 'questions/blueprint_overview.html'

    # Must be provided by subclass
    blueprint = None
    model = None

    def __init__(self, *args, **kwargs):

        if not self.model:
            self.model = self.get_model()

        return super().__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['blueprint'] = self.blueprint


        primary_questions = [q(instance=self.object) for q in \
                             self.blueprint.primary_questions]
        context['primary_questions'] = primary_questions

        return context

    def get_submodels(self):

        qs = self.object.submodel_set.all().order_by('order')
        return qs

    def get_model(self):

        return self.blueprint.model





class QuestionDisplayView(generic.TemplateView):

    template_name = 'questions/question_detail.html'


class QuestionView(generic.TemplateView):

    template_name = 'questions/question_detail.html'
    question = None
    question_dict = None
    question_url_arg = 'question'
    parent_pk_arg = 'pk'

    def get(self, request, *args, **kwargs):

        self.get_question()
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):

        self.get_question()
        self.get_object()
        return super().post(request, *args, **kwargs)


    def get_question(self):

        if self.question_dict:
            question_arg = self.kwargs.get(self.question_url_arg, None)
            self.question = self.question_dict[question_arg]

        if not self.question:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(
                'No questions defined')

        self.form_class = self.question

        return self.question

    def get_object(self):
        'Returns the object that the question is about.'

        if not self.model:
            self.model = self.question.model

        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            return self.model()
        return self.model.objects.get(pk=pk)

    def get_success_url(self):

        parent_pk = self.kwargs.get(self.parent_pk_arg)
        return reverse('questions:blueprint_overview',
                                   kwargs={self.parent_pk_arg: parent_pk})




class QuestionEditView(QuestionView,
                       generic.edit.UpdateView,
                       ):

    pk_url_kwarg = 'question_pk'
    template_name = 'uil.questions/question_detail.html'



class QuestionCreateView(QuestionView,
                         generic.edit.CreateView,
                         ):


    pk_url_kwarg = 'question_pk'
    template_name = 'questions/question_detail.html'

    def post(self, request, *args, **kwargs):

        self.get_question()
        return super().post(request, *args, **kwargs)


    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()
        kwargs.update({'prereg': self.get_prereg()})
        return kwargs
