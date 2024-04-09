from typing import List, Optional, Tuple

from deprecated.sphinx import deprecated
from django.conf import settings
from django.core.mail import get_connection

from cdh.core.mail import TemplateEmail


@deprecated(
    version='3.2',
    reason="Replaced by cdh.mail"
)
def send_template_email(
        recipient_list: List[str],
        subject: str,
        template_context: dict,
        html_template: Optional[str] = None,
        plain_template: Optional[str] = None,
        from_email: Optional[str] = None,
        plain_context: Optional[dict] = None,
        html_context: Optional[dict] = None,
        language: str = 'nl',
) -> int:
    """
    Light wrapper for :class:`.TemplateEmail`.

    You need to provide at least one of the template variants (HTML or plain).
    Or both, if you want.

    :param recipient_list: list of recipients
    :type recipient_list: list of str
    :param str subject: Email subject
    :param str from_email: the FROM: value. Uses settings.FROM_EMAIL if omitted
    :param str html_template: the HTML template to render
    :param str plain_template: the plain template to render
    :param dict template_context: any context data needed for rendering the
                                  templates
    :param dict html_context: additional context data for the HTML template
    :param dict plain_context: additional context data for the plain template
    :param str language: the langauge code used during rendering
    :returns: the number of emails send
    :rtype: int
    :raises ValueError: if no template at all was supplied
    """
    if html_template is None and plain_template is None:
        raise ValueError("No template(s) specified")

    if plain_context is None:
        plain_context = {}
    if html_context is None:
        html_context = {}

    email = TemplateEmail(
        to=recipient_list,
        subject=subject,
        from_email=from_email,
        html_template=html_template,
        plain_template=plain_template,
        context=template_context,
        plain_context=plain_context,
        html_context=html_context,
        language=language
    )

    return email.send()


@deprecated(
    version='3.2',
    reason="Replaced by cdh.mail"
)
def send_mass_personalised_mass_mail(
        datatuple: List[Tuple[str, dict, List[str]]],
        template_context: dict,
        html_template: Optional[str] = None,
        plain_template: Optional[str] = None,
        from_email: str = None,
        plain_context: dict = None,
        html_context: dict = None,
        language: str = 'nl',
) -> int:
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
    :type datatuple: tuple[str, dict, list[str]]
    :param str from_email: the FROM: value. Uses settings.FROM_EMAIL if omitted
    :param str html_template: the HTML template to render
    :param str plain_template: the plain template to render
    :param dict template_context: any context data needed for rendering the
                                  templates
    :param dict html_context: additional context data for the HTML template
    :param dict plain_context: additional context data for the plain template
    :param str language: the langauge code used during rendering
    :returns: the number of emails send
    :rtype: int
    :raises ValueError: if no template at all was supplied
    """
    if html_template is None and plain_template is None:
        raise ValueError("No template(s) specified")

    if plain_context is None:
        plain_context = {}
    if html_context is None:
        html_context = {}

    sent = 0
    from_email = from_email or settings.FROM_EMAIL
    connection = get_connection()

    # We reuse the same object to improve rendering speed
    # e.g. to make sure we don't recreate templates constantly
    email = TemplateEmail(
        to=[],
        subject="",
        from_email=from_email,
        html_template=html_template,
        plain_template=plain_template,
        context=template_context,
        plain_context=plain_context,
        html_context=html_context,
        connection=connection,
        language=language
    )

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

        email.to = recipient_list
        email.subject = subject
        email.context = context
        email.html_context = html_text_context
        email.plain_context = plain_text_context

        sent += email.send()

    return sent


@deprecated(
    version='3.2',
    reason="Replaced by cdh.mail"
)
def send_mass_personalised_custom_mail(
        datatuple: List[Tuple[str, dict, List[str]]],
        email_class,
        template_context: dict,
        contents: str,
        sender: Optional[str] = None,
        banner: Optional[str] = None,
        footer: Optional[str] = None,
        from_email: str = None,
        plain_context: dict = None,
        html_context: dict = None,
        language: str = 'nl',
) -> int:
    """
    Given a datatuple of (subject, personal_context, recipient_list),
    send each message to each recipient list.

    This method takes advantage of :class:`.BaseCustomTemplateEmail` caching
    to make sure the custom templates are only built once, speeding up
    rendering.

    personal_context and template_context will be merged together to create
    a personalised email.

    html_context and plain_context can be used to override something in the
    regular template_context for either the html version of the plain text
    version. (Note: you can also add a key that does not exist in
    template_context)

    :param datatuple: A tuple of tuples: (subject, personal_context, recipient_list)
    :type datatuple: tuple[str, dict, list[str]]
    :param str from_email: the FROM: value. Uses settings.FROM_EMAIL if omitted
    :param email_class: the custom email class to use
    :type email_class: extension of :class:`.BaseCustomTemplateEmail`
    :param str contents: the template code for the contents block
    :param sender: the template code for the sender block
    :type sender: str or None
    :param banner: the template code for the banner block
    :type banner: str or None
    :param footer: the template code for the footer block
    :type footer: str or None
    :param dict template_context: any context data needed for rendering the
                                  templates
    :param dict html_context: additional context data for the HTML template
    :param dict plain_context: additional context data for the plain template
    :param str language: the langauge code used during rendering
    :returns: the number of emails send
    :rtype: int
    """
    if plain_context is None:
        plain_context = {}
    if html_context is None:
        html_context = {}

    sent = 0
    from_email = from_email or settings.FROM_EMAIL
    connection = get_connection()

    # We reuse the same object to improve rendering speed
    # e.g. to make sure we don't recreate templates constantly
    email = email_class(
        to=[],
        subject="",
        from_email=from_email,
        contents=contents,
        sender=sender,
        banner=banner,
        footer=footer,
        context=template_context,
        plain_context=plain_context,
        html_context=html_context,
        connection=connection,
        language=language
    )

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

        email.to = recipient_list
        email.subject = subject
        email.context = context
        email.html_context = html_text_context
        email.plain_context = plain_text_context

        sent += email.send()

    return sent


