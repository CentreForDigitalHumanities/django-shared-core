import urllib.parse as parse
from functools import lru_cache
from typing import List, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection, send_mail
from django.template.loader import render_to_string
from django.utils import translation


def send_template_email(
        recipient_list: list,
        subject: str,
        template: str,
        template_context: dict,
        from_email: str = None,
        plain_context: dict = None,
        html_context: dict = None,
        language: str = 'nl',
) -> None:
    """
    Light wrapper for Django's send_mail function. The main addition: this
    function handles the template rendering for you. Just specify the template
    name (without extensions).

    Note: both a HTML and a plain text version of the template should exist!

    For example:
    app/test.html
    app/test.txt

    Function call: send_template_email(template='app/test', *args, **kwargs)

    html_context and plain_context can be used to override something in the
    regular template_context for either the html version of the plain text
    version. (Note: you can also add a key that does not exist in
    template_context)

    :param recipient_list: A list of recipients
    :param subject: Email subject
    :param template: Template name, without extension
    :param template_context: Any context variables for the templates
    :param from_email: FROM header. If absent, settings.FROM_EMAIL will be used
    :param html_context: Optional dict with context specifically for HTML
    :param plain_context: Optional dict with context specifically for plaintext
    :param language: Which language Django should use when creating the mail
    """
    if plain_context is None:
        plain_context = {}
    if html_context is None:
        html_context = {}

    # Override so that all emails will be parsed with the desired language
    old_lang = translation.get_language()
    translation.activate(language)

    # Create the context for both the plain text email
    plain_text_context = template_context.copy()
    plain_text_context.update(plain_context)

    # And now the same for the HTML version
    html_text_context = template_context.copy()
    html_text_context.update(html_context)

    plain_body = render_to_string(
        '{}.txt'.format(template),
        plain_text_context
    )
    html_body = render_to_string(
        '{}.html'.format(template),
        html_text_context
    )

    # revert to the original language
    translation.activate(old_lang)

    from_email = from_email or settings.EMAIL_FROM

    send_mail(
        subject,
        plain_body,
        from_email,
        recipient_list,
        html_message=html_body
    )


def send_personalised_mass_mail(datatuple: List[Tuple[str, dict, List[str]]],
                                template: str,
                                template_context: dict,
                                from_email: str = None,
                                plain_context: dict = None,
                                html_context: dict = None,
                                language: str = 'nl',
                                ) -> None:
    """
    Given a datatuple of (subject, personal_context, recipient_list),
    send each message to each recipient list.

    personal_context and template_context will be merged together to create
    a personalised email.

    html_context and plain_context can be used to override something in the
    regular template_context for either the html version of the plain text
    version. (Note: you can also add a key that does not exist in
    template_context)

    :param datatuple: A tuple of tuples: (subject, personal_context, recipient_list)
    :param template: Template name, without extension
    :param template_context: Any context variables for the templates
    :param from_email: FROM header. If absent, settings.FROM_EMAIL will be used
    :param html_context: Optional dict with context specifically for HTML
    :param plain_context: Optional dict with context specifically for plaintext
    :param language: Which language Django should use when creating the mail
    """
    if plain_context is None:
        plain_context = {}
    if html_context is None:
        html_context = {}

    messages = []
    from_email = from_email or settings.FROM_EMAIL
    connection = get_connection()

    # Override so that all emails will be parsed with the desired language set
    old_lang = translation.get_language()
    translation.activate(language)

    for subject, personal_context, recipient_list in datatuple:
        # Copy the personal context and extend it with the generic context
        context = personal_context.copy()
        context.update(template_context)

        # Copy our newly made context, and extend it with the plain_context
        plain_text_context = context.copy()
        plain_text_context.update(plain_context)

        # And now the same for the HTML version
        html_text_context = context.copy()
        html_text_context.update(html_context)

        plain_body = render_to_string(
            '{}.txt'.format(template),
            plain_text_context
        )
        html_body = render_to_string(
            '{}.html'.format(template),
            html_text_context
        )

        message = EmailMultiAlternatives(subject, plain_body, from_email,
                                         recipient_list, connection=connection)

        message.attach_alternative(html_body, 'text/html')

        messages.append(message)

    translation.activate(old_lang)

    connection.send_messages(messages)

