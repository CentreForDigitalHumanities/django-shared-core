class ModelFromKwargMixin():

    model_kwarg = 'model'
    model_translation_dict = {}

    def get(self, *args, **kwargs):

        self.model = self.get_model()
        return super().get(*args, **kwargs)


    def post(self, *args, **kwargs):

        self.model = self.get_model()
        return super().post(*args, **kwargs)

    def get_model(self):

        model_arg = self.kwargs.get(self.model_kwarg)
        return self.model_translation_dict[model_arg]

    def get_object(self):

        if not hasattr(self, 'model'):
            self.model = self.get_model()

        return super().get_object()
