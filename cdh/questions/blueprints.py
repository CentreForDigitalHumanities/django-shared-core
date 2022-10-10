
class Blueprint:
    '''A blueprint is a method for validating complicated models
    with any number of submodels with interrelated requirements
    and dependencies'''

    model = None
    starting_consumers = []
    errors = {}

    def __init__(self, blueprint_object):
        self.object = blueprint_object
        self.start()

    def start(self):
        return self.evaluate(self.starting_consumers)

    def evaluate(self, consumers):
        """
        Evaluate all given consumers and their output.

        This recursive function goes through the list
        of consumers and presents them with this blueprint
        object. The consumers look at the current state of
        the blueprint to see if it satisfies their needs.

        Consumers should return a list of new consumers to
        append to the end of the list. This list may be empty.

        While in this loop, consumers may modify
        blueprint state by adding errors and appending to
        desired_next.
        """
        # We've run out of consumers. Finally.
        if consumers == []:
            return True

        # Instantiate consumer with self
        current = consumers[0](self)

        # Run consumer logic, and add the list of consumers
        # it returns to the list of consumers to be run
        next_consumers = current.consume() + consumers[1:]

        return self.evaluate(consumers=next_consumers)


class BaseConsumer:

    def __init__(self, blueprint):
        self.blueprint = blueprint

    def consume(self):
        """Returns a list of new consumers depending on
        blueprint state."""
        return []


class BaseQuestionConsumer(BaseConsumer):

    question_class = None
    question_data = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instantiate()

    def get_django_errors(self):
        "Get Django form errors"
        return self.question.errors

    def get_question_data(self):
        "Placeholder to be overridden by subclass"
        return self.question_data

    def instantiate(self):
        """Create the self.question instance with the correct question object.
        Overwrite this function if the question does not use the default
        blueprint object."""
        self.question = self.question_class(
            instance=self.blueprint.object,
            question_data=self.get_question_data(),
        )
        return self.question

    @property
    def empty_fields(self, fields=None):
        question = self.question
        empty = []
        if not fields:
            fields = question.Meta.fields
        for key in fields:
            value = question[key].value()
            if value in ['', 'None', None]:
                empty.append(key)
        return empty

    @property
    def filled_in_fields(self, fields=None):
        question = self.question
        if not fields:
            fields = question.Meta.fields
        for empty_field in self.empty_fields:
            fields.remove(empty_field)
        return fields
            















