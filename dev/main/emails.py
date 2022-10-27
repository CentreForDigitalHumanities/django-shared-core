from django.utils.translation import gettext as _

from cdh.core.mail import BaseCustomTemplateEmail, CTEVarDef


class ExampleCustomTemplateEmail(BaseCustomTemplateEmail):
    user_variable_defs = [
        CTEVarDef('name', _("example_email.vars.name"), "John Doe"),
        CTEVarDef('date', _("example_email.vars.date"), "1970-01-01"),
        # Chosen by fair dice roll, guaranteed to be random
        CTEVarDef('random_number', _("example_email.vars.random_number"), "4"),
    ]
