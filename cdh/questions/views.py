from django.views import generic, View
from django.urls import reverse


class BlueprintMixin():
    """Provide a blueprint to this view, instantiated from its object"""

    # Must be provided by subclass
    blueprint_class = None
    blueprint = None
    blueprint_pk_kwarg = "blueprint_pk"
    model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blueprint'] = self.get_blueprint()
        return context

    def get_blueprint(self,):
        if not self.blueprint:
            self.blueprint = self.blueprint_class(self.get_blueprint_object())
        return self.blueprint

    def get_blueprint_object(self):
        pk = self.kwargs.get(self.blueprint_pk_kwarg)
        model = self.blueprint_class.model
        if pk:
            object = model.objects.get(pk=pk)
        else:
            object = model()
        return object


class SingleQuestionMixin():

    question_pk_kwarg = "question_pk"
    question_class = None
    # self.question is the instantiated question
    question = None

    def get_question(self):
        if not self.question:
            cls = self.get_question_class()
            if cls.model:
                question_object = self.get_question_object()
                self.question = cls(instance=question_object)
            else:
                self.question = cls()
        return self.question

    def get_question_object(self):
        question_pk = self.kwargs.get(self.question_pk_kwarg)
        question_model = self.get_question_class().model
        if question_pk:
            object = question_model.objects.get(pk=question_pk)
        else:
            object = question_model()
        return object

    def get_question_class(self):
        "Placeholder for subclasses"
        return self.question_class

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = self.get_question()
        return context


class QuestionFromURLMixin(SingleQuestionMixin):
    """If you want to reuse a certain view for multiple questions, mix in
    this class and provide it with a question_dict to get the question class
    from a URL arg."""

    question_class_kwarg = "question"

    # The question dict consists of strings mapped to question classes.
    # It must be defined by a subclass or in URLconf.
    question_dict = None

    def get_question_class(self):
        question_kwarg = self.kwargs.get(self.question_class_kwarg)
        return self.question_dict[question_kwarg]

class QuestionDisplayView(generic.TemplateView):

    template_name = 'questions/question_detail.html'


class QuestionView(
        SingleQuestionMixin,
        generic.TemplateView,
):

    template_name = 'questions/question_detail.html'
    question = None
    question_class = None
    question_pk_kwarg = "question_pk"
    parent_pk_arg = 'pk'

    def _get_question_object(self, question):
        object_pk = self.kwargs.get(self.question_pk_kwarg)
        return question.model.objects.get(
            pk=object_pk,
        )

    def get_object(self):
        'Returns the object that the question is about.'
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            return self.question.model()
        return self.question.model.objects.get(pk=pk)

    def get_success_url(self):
        parent_pk = self.kwargs.get(self.parent_pk_arg)
        return reverse(
            'questions:blueprint_overview',
            kwargs={self.parent_pk_arg: parent_pk},
        )


class QuestionEditView(QuestionView,
                       generic.edit.UpdateView,
                       ):

    template_name = 'cdh.questions/question_detail.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_question_object()
        return super().post(request, *args, **kwargs)

    def get_form(self):
        return self.get_question()



class QuestionCreateView(QuestionView,
                         generic.edit.CreateView,
                         ):


    pk_url_kwarg = 'question_pk'
    template_name = 'questions/question_detail.html'

    def post(self, request, *args, **kwargs):

        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()
        kwargs.update({'prereg': self.get_prereg()})
        return kwargs


class QuestionDeleteView(QuestionView,
                         generic.edit.DeleteView):

    template_name = "questions/question_detail.html"


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
        #kwargs.update({'prereg': self.get_prereg()})
        return kwargs
