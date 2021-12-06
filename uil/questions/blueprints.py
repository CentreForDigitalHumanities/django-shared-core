class Blueprint:
    '''A blueprint is a method for validating complicated models
    with any number of submodels with interrelated requirements
    and dependencies'''


    # Starting values
    provided = []
    required = []

    def __init__(self):

        pass

    def __call__(self):

        pass

    def provide(self, provider):

        self.provided.append(provider)

    def require(self, requirement):

        self.requirements.append(requirement)

    def validate(self):

        pass

    def get_next_step(self):

        pass

class Requirement:

    def __init__(self, fun):

        self.function = fun

    def __call__(self, object):
        '''When a requirement gets called on an object, it does one of the
        following:

        a. Returns False if the object does not provide the requirement
        b. Returns an optionally empty list of new requirements if the current
        requirement has been satisfied'''

        return self.evaluate(object)

    def success_callback(self, blueprint):
        '''This function is called when the requirement function is successfully
        fulfilled. For example if fulfilling a requirement should create new
        requirements'''

        pass
