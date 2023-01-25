"""
A Django Management Command to rename existing Django Applications.

See https://github.com/odwyersoftware/django-rename-app
"""

import logging

from django.core.management.base import BaseCommand

from cdh.core.mail.classes import CTETagPackage, CTEVarDef, BaseCustomTemplateEmail, \
    TemplateEmail

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):

        template = "I like trains<br/>Really, I do"

        msg = BaseCustomTemplateEmail(
            to="example@example.org",
            from_email="example@example.org",
            subject="Test",
            # banner="I like trains",
            # sender_str="Testing 123",
            # footer="<strong>HULK IS STRONG</strong>",
            # html_template="cdh.core/tst_mail.html",
            # plain_template="cdh.core/test_mail.txt"
            contents=template,
            user_variable_defs=[
                CTEVarDef('chicken', 'prints "chicken"', "chicken")
            ],
            template_tag_defs=[
                CTETagPackage(
                    'i18n',
                    [
                        ('trans', ["'text'"], "Translate a given text")
                    ]
                )
            ],
            # footer="<strong>BAM</strong>",
            # banner="<i>Hellow World</i>",
            # sender="God"
            theme_settings={
                'footer_stripe_color': "#AE9D22",
            }
        )
        print(msg.help_text)
        # msg.send()
