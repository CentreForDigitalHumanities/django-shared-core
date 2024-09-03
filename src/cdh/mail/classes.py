import re
from abc import ABC, abstractmethod
from email.mime.base import MIMEBase
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Engine, Template
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template, render_to_string
from django.template.loader_tags import BlockNode, ExtendsNode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.utils.functional import keep_lazy_text
from django.utils.html import _strip_once

from .logger import logger
from .settings import CDH_EMAIL_THEME_SETTINGS, CDH_EMAIL_PLAIN_FALLBACK_TEMPLATE, CDH_EMAIL_HTML_FALLBACK_TEMPLATE, CDH_EMAIL_FAIL_SILENTLY


@keep_lazy_text
def _strip_tags(value) -> str:
    """Return the given HTML with all tags stripped, and leading/trailing
    whitespace stripped but with line breaks preserved.

    :meta private:
    """
    value = str(value)

    # Manually replace <br> tags; to preserve intended newlines _strip_once
    # just strips it but doesn't actually add a newline for rendering. Thus:
    # 'hello<br/>world' would become 'helloworld' instead of 'hello\nworld'. The
    # \n in the regex is to make sure we don't add _two_ newlines if someone
    # actually puts a newline after a <br>
    value = re.sub(r"<br ?/?>\n?", "\n", value)

    # Strip HTML tags
    # Note: in typical case this loop executes _strip_once once. Loop condition
    # is redundant, but helps to reduce number of executions of _strip_once.
    while "<" in value and ">" in value:
        new_value = _strip_once(value)
        if value.count("<") == new_value.count("<"):
            # _strip_once wasn't able to detect more tags.
            break
        value = new_value

    # Go over every line and strip
    # This is needed because the stripping above doesn't account for indenting
    # from the HTML structure
    ret = ""
    for line in value.split("\n"):
        ret += line.strip()
        # Add back the newline we split on
        ret += '\n'

    # Remove any remaining leading/trailing whitespace (often from tags)
    # before returning
    return ret.strip()


class BaseEmail(ABC):
    """Base class for all email classes.

    These params mostly correspond to Django's Message, so read those docs
    for more details

    About render/template contexts:
    When not supplied with both an HTML and a plain text email, the missing one
    will be automatically generated. However, it will not use render contexts
    of the other variant. For example, if you leave the plain text version to
    be automatically generated, the plain text version will use plain_context
    and not html_context.

    About theme settings:
    The HTML template has some styling configuration to tweak the appearance of
    the email. You can specify any changes on this class, but in most cases it's
    better to apply app-wide changes using the CDH_EMAIL_THEME_SETTINGS config
    value in settings.py

    About fallback templates:
    These templates are used when generating a missing variant. For example,
    if you supply a plain text template only, html_fallback_template will
    be used as the base template for the generated HTML version.
    When your app uses a custom base template, it's best to set this template
    globally using the settings.py settings. It's provided on the class only
    if your app uses multiple base templates.

    HTML base templates MUST have a block called 'content' and are encouraged to
    have 'sender', 'banner' and 'footer' blocks.
    Plain base templates use template vars instead of blocks, but the same
    requirements apply on those vars as well.
    """

    def __init__(
            self,
            to: Union[str, List[str]],
            subject: str,
            language: str = 'nl',
            from_email: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
            attachments: Optional[List[Union[MIMEBase, Tuple[str, str,
                                                             str]]]] = None,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None,
            reply_to: Optional[str] = None,

            context: Optional[Dict] = None,
            plain_context: Optional[Dict] = None,
            html_context: Optional[Dict] = None,

            theme_settings: Optional[Dict] = None,

            html_fallback_template: str = CDH_EMAIL_HTML_FALLBACK_TEMPLATE,
            plain_fallback_template: str = CDH_EMAIL_PLAIN_FALLBACK_TEMPLATE,

            fail_silently: Union[bool, None] = None,
    ):
        """
        :param to: a list of recipients, can be plain email or formatted ("John
                   Doe <j.doe@example.org>")
        :type to: list of str
        :param str subject: the email subject
        :param str language: the language used during rendering the email. Uses
                             Django's i18n framework
        :param from_email: the From: email address. Uses settings.EMAIL_FROM if
                           omitted
        :type from_email: str or None
        :param headers: any additional SMTP headers to be used
        :type headers: dict or None
        :param attachments: a list of email attachments to be sent along.
        :type attachments: list of MimeBase or Tuple
        :param cc: a list of recipients to put as CC:
        :type cc: list of str or None
        :param bcc: a list of recipients to put ad BCC:
        :type bcc: list of str or None
        :param reply_to: an email to be set as REPLY_TO: (not set if left empty)
        :type reply_to: list of str or None

        :param dict context: any template context needed for both the templates
        :param dict html_context: any template context needed by the HTML template,
                                  will override values in context if both have them
        :param dict plain_context: any template context needed by the plain
                                   template, will override values in context if
                                   both have them.

        :param dict  theme_settings: a dict of overrides for the styling of the
                                     HTML email does not need to contain all
                                     values, only the ones you want to override.
        :param str html_fallback_template: the base template for HTML emails used
                                           for generating an HTML version of a
                                           plain text email
        :param str plain_fallback_template: the base template for plain text emails
                                            used for generating a plain text version
                                            of an HTML email

        :param bool fail_silently: whether errors during sending should be
                                   suppressed. If not provided, defaults to CDH_EMAIL_FAIL_SILENTLY
        """
        if not isinstance(to, list):
            to = [to]
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.subject = subject
        self.from_email = from_email or settings.EMAIL_FROM
        self.language = language
        self.headers = headers
        self.attachments = attachments or []

        self.context = context or {}
        self.plain_context = plain_context or {}
        self.html_context = html_context or {}

        self.fail_silently = fail_silently
        if fail_silently is None:
            self.fail_silently = CDH_EMAIL_FAIL_SILENTLY

        self.theme_settings = CDH_EMAIL_THEME_SETTINGS.copy()
        if theme_settings:
            self.apply_theme_settings(theme_settings)

        self.html_fallback_template = html_fallback_template
        self.plain_fallback_template = plain_fallback_template

    def apply_theme_settings(self, theme_settings: dict) -> None:
        """Applies theme settings

            :param dict theme_settings: a dict of overrides for the styling
                                        of the HTML email does not need to
                                        contain all values, only the ones you
                                        want to override.
        """
        self.theme_settings.update(theme_settings)

    def attach(self, filename, content=None, mimetype=None) -> None:
        """Attach a new attachment to this email

        :param filename: either a string of the filename, or a MIMEBase object
                         representing the entire file
        :type filename: str or MIMEBase
        :param content: If filename is a string, the contents of the file.
                        Ignored otherwise
        :type content: str or None
        :param mimetype: If filename is a string, the mimetype of the file.
                         Ignored otherwise
        :type mimetype: str or None
        """
        if isinstance(filename, MIMEBase):
            self.attachments.append(filename)
        else:
            self.attachments.append((filename, content, mimetype))

    def send(self, connection=None, fail_silently=None) -> int:
        """Sends the email

        If sending multiple emails in a row, it's recommended to create a
        connection yourself and use them on all emails for performance reasons.

        :param connection: a Django email backend to send the mail with. If
                           omitted, the default backend will be used
        :param bool fail_silently: whether errors during sending should be
                                   suppressed
        :return: number of emails sent
        :rtype: int
        """
        try:
            if fail_silently is None:
                fail_silently = self.fail_silently

            old_lang = translation.get_language()
            translation.activate(self.language)

            email = EmailMultiAlternatives(
                to=self.to,
                subject=self.subject,
                from_email=self.from_email,
                reply_to=self.reply_to,
                cc=self.cc,
                bcc=self.bcc,
                body=self._get_plain_body(),
                connection=connection,
                attachments=self.attachments,
                headers=self.headers,
            )

            if html_body := self._get_html_body():
                email.attach_alternative(
                    html_body,
                    'text/html'
                )

            translation.activate(old_lang)

            return email.send(fail_silently)

        except Exception as e:
            if not fail_silently:
                logger.error("Error during mail compose", exc_info=True)
                raise e
            # Log the error as critical if we're failing silently, to trigger some alarms
            logger.critical("Error during mail compose", exc_info=True)


    def _get_plain_context(self) -> dict:
        context = self.context.copy()
        context.update(self.plain_context)

        return context

    @abstractmethod
    def _get_html_context(self) -> dict:
        """Overrides must add the following keys:
        has_sender, has_banner and has_footer
        """
        context = self.context.copy()
        context.update(self.html_context)
        context['theme'] = self.theme_settings

        return context

    @abstractmethod
    def _get_plain_body(self) -> str:
        pass

    @abstractmethod
    def _get_html_body(self) -> str:
        pass


class TemplateEmail(BaseEmail):
    """Regular Django template files based emails

    One of the two templates is required. If one is missing, it will be
    generated from the other.
    """

    def __init__(
            self,
            *args,
            html_template: Optional[str] = None,
            plain_template: Optional[str] = None,
            **kwargs
    ):

        """

        :param str html_template: the HTML template to send
        :param str plain_template: the plain text template to send

        :param to: a list of recipients, can be plain email or formatted ("John
                   Doe <j.doe@example.org>")
        :type to: list of str
        :param str subject: the email subject
        :param str language: the language used during rendering the email. Uses
                             Django's i18n framework
        :param from_email: the From: email address. Uses settings.EMAIL_FROM if
                           omitted
        :type from_email: str or None
        :param headers: any additional SMTP headers to be used
        :type headers: dict or None
        :param attachments: a list of email attachments to be sent along.
        :type attachments: list of MimeBase or Tuple
        :param cc: a list of recipients to put as CC:
        :type cc: list of str or None
        :param bcc: a list of recipients to put ad BCC:
        :type bcc: list of str or None
        :param reply_to: an email to be set as REPLY_TO: (not set if left empty)
        :type reply_to: list of str or None

        :param dict context: any template context needed for both the templates
        :param dict html_context: any template context needed by the HTML template,
                                  will override values in context if both have them
        :param dict plain_context: any template context needed by the plain
                                   template, will override values in context if
                                   both have them.

        :param dict  theme_settings: a dict of overrides for the styling of the
                                     HTML email does not need to contain all
                                     values, only the ones you want to override.
        :param str html_fallback_template: the base template for HTML emails used
                                           for generating an HTML version of a
                                           plain text email
        :param str plain_fallback_template: the base template for plain text emails
                                            used for generating a plain text version
                                            of an HTML email
        :param bool fail_silently: whether errors during sending should be
                                   suppressed. If not provided, defaults to CDH_EMAIL_FAIL_SILENTLY
        """
        super().__init__(*args, **kwargs)
        if html_template is None and plain_template is None:
            raise ValueError("No email templates supplied!")

        self.html_template = html_template
        self.plain_template = plain_template

        self._html_blocks = None

    def _get_html_blocks(self) -> Dict[str, BlockNode]:
        """Helper method to extract the individual content block nodes from the
        supplied HTML template"""
        if self._html_blocks or not self._has_html_body():
            return self._html_blocks

        self._html_blocks = {
            'sender':  None,
            'banner':  None,
            'content': None,
            'footer':  None,
        }
        try:
            html_template = get_template(self.html_template)
        except TemplateDoesNotExist as e:
            logger.error(f"Could not find HTML template ({self.html_template}) for email. Skipping block extraction.")

            if not self.fail_silently:
                raise e

            return self._html_blocks

        self._html_blocks.update(self._resolve_html_blocks(html_template.template))

        return self._html_blocks

    def _resolve_html_blocks(self, template: Template):
        """"
        Recursively resolve all blocks in a template and its parents, excluding the top-level template.
        """
        blocks = {}

        for node in template.nodelist:
            # Append the block to the dict if the node has (resolved) blocks
            if hasattr(node, 'blocks'):
                blocks.update(node.blocks)

            # If we encounter an ExtendsNode, we need to resolve the parent and add its blocks
            # Note: as the 'root' template is not an ExtendsNode, it will be skipped. This is by design, as
            # the blocks we're interested in are empty in the root template. (And thus need to be ignored)
            if isinstance(node, ExtendsNode):
                try:
                    context = Context({})
                    context.template = template
                    blocks.update(self._resolve_html_blocks(node.get_parent(context)))
                except Exception as e:
                    logger.error("Error resolving parent email template", exc_info=True)

                    if not self.fail_silently:
                        raise e

        return blocks

    def _get_html_context(self) -> dict:
        context = super()._get_html_context()

        if blocks := self._get_html_blocks():
            context['has_sender'] = blocks['sender'] is not None
            context['has_banner'] = blocks['banner'] is not None
            context['has_footer'] = blocks['footer'] is not None

        return context

    def _get_plain_body(self) -> Optional[str]:
        if self.plain_template:
            return render_to_string(
                self.plain_template,
                self._get_plain_context()
            )

        # If we don't have a Plain template, we're going to build our own!
        if self._has_html_body():
            try:
                # Build a render context Django can use
                render_context = Context(self._get_plain_context())
                # Needed because Django's render requires these for metadata
                render_context.template = get_template(self.html_template)
                render_context.template.engine = Engine.get_default()

                # Render the content blocks individually and strip the HTML tags
                # from them
                blocks = {
                    name: "\n"+_strip_tags(
                        node.render(
                            render_context
                        )
                    )
                    for name, node in self._get_html_blocks().items() if node
                }

                return render_to_string(
                    self.plain_fallback_template,
                    blocks
                ).strip()
            except Exception as e:
                logger.error("Error during plain text email generation", exc_info=True)

                if not self.fail_silently:
                    raise e

                return None

        return None

    def _has_html_body(self) -> bool:
        return self.html_template is not None

    def _get_html_body(self) -> Union[str, None]:
        context = self._get_html_context()
        if self._has_html_body():
            return render_to_string(
                self.html_template,
                context
            )

        try:
            # If we don't have an HTML template, we're going to build our own!
            # And paste in the plain content
            engine = Engine.get_default()
            template = engine.from_string(
                "{% extends '" + self.html_fallback_template + "' %}"
                "{% block content %}{{ plain_content|linebreaks }}{% endblock %}"
            )

            context['plain_content'] = self._get_plain_body()
        except Exception as e:
            logger.error("Error during HTML email generation", exc_info=True)

            if not self.fail_silently:
                raise e

            return None

        return template.render(Context(context))


class CTEVarDef:
    """Descriptor class for user-usable variables in a Custom Template Email

    This class serves two roles:
    - Provide information for help text generation
    - Provide a default value when rendering the preview
    """

    def __init__(
            self,
            name: str,
            help_text: str = None,
            preview_value=None,
            safe: bool = False,
            **kwargs
    ):
        """
        :param str name: The variable name
        :param help_text: a short description of what this var will output
                          (optional)
        :type help_text: str or None
        :param preview_value: a placeholder value that will be inserted when
                              rendering the preview (optional)
        :param safe: if the contents of the var should be marked safe.
        :type safe: bool
        :param kwargs: Any other parameter passed to the class. Not used in
                       default implementations, but can be used for custom ones
        :type kwargs: dict
        """
        self.name = name
        self.help_text = help_text
        self.preview_value = preview_value
        self.safe = safe
        self.kwargs = kwargs


class CTETagPackage:
    """Configuration class for loading template tag packages

    This class serves two roles:
    - Providing information for loading template tag packages in the template
    - Provide information for help text generation

    All packages need to be importable by the Django rendering engine
    """

    def __init__(
            self,
            package: str,
            tags: List[Tuple[
                str,
                Optional[list],
                Optional[str],
            ]]):
        """
        :param str package: the name of the package to load
        :param tags: a list of 3-tuples; The tuple should contain:
                     - The name of the usable tag inside the package
                     - A list of arguments that tag accepts
                     - A help string explaining what the tag does
        """
        self.package = package
        self.tags = tags


class BaseCustomTemplateEmail(BaseEmail):
    """Email class for sending HTML emails using user supplied HTML templates

    DO NOT USE THIS CLASS FOR 'HARDCODED' EMAILS. Use :class:`.TemplateEmail`
    instead.

    BE CAREFUL WHAT YOU EXPOSE TO THE USER. This method itself is safe, as
    everything is run in a sandbox. However, template tags can have (nasty)
    side effects outside the sandbox. Also, some vars might just expose more
    than you thought.

    Unlike TemplateEmail, this class should be extended and not be used
    directly. It uses class variables, which should not be set on an instance
    level.

    :param user_variable_defs: a list of user usable variables
    :type user_variable_defs: list of :class:`CTEVarDef`
    :param template_tag_packages: a list of template tag packages to load
    :type template_tag_packages: list of :class:`CTETagPackage`
    """
    user_variable_defs: List[CTEVarDef] = []
    template_tag_packages: List[CTETagPackage] = []

    def __init__(
            self,
            *args,
            contents: str,
            sender: Optional[str] = None,
            banner: Optional[str] = None,
            footer: Optional[str] = None,
            **kwargs
    ):
        """
        :param to: a list of recipients, can be plain email or formatted ("John
                   Doe <j.doe@example.org>")
        :type to: list of str
        :param str subject: the email subject
        :param str language: the language used during rendering the email. Uses
                             Django's i18n framework
        :param from_email: the From: email address. Uses settings.EMAIL_FROM if
                           omitted
        :type from_email: str or None
        :param headers: any additional SMTP headers to be used
        :type headers: dict or None
        :param attachments: a list of email attachments to be sent along.
        :type attachments: list of MimeBase or Tuple
        :param cc: a list of recipients to put as CC:
        :type cc: list of str or None
        :param bcc: a list of recipients to put ad BCC:
        :type bcc: list of str or None
        :param reply_to: an email to be set as REPLY_TO: (not set if left empty)
        :type reply_to: list of str or None

        :param dict context: any template context needed for both the templates
        :param dict html_context: any template context needed by the HTML template,
                                  will override values in context if both have them
        :param dict plain_context: any template context needed by the plain
                                   template, will override values in context if
                                   both have them.

        :param dict  theme_settings: a dict of overrides for the styling of the
                                     HTML email does not need to contain all
                                     values, only the ones you want to override.
        :param str html_fallback_template: the base template for HTML emails used
                                           for generating an HTML version of a
                                           plain text email
        :param str plain_fallback_template: the base template for plain text emails
                                            used for generating a plain text version
                                            of an HTML email
        """
        super().__init__(*args, **kwargs)
        self.contents = contents
        self.banner = banner
        self.sender = sender
        self.footer = footer

    @classmethod
    @keep_lazy_text
    def help_text(cls) -> str:
        """A (marked_safe) string describing which vars and tags can be used
        in this template. Intended to be used as a formfield help_text"""
        help_text = ""

        if cls.user_variable_defs:
            help_text += "<strong>"
            help_text += _('cdh.mail.custom.help_text.variables')
            help_text += "</strong><br/>"

            for var in cls.user_variable_defs:
                help_text += "<code>{{ " + var.name + " }}</code>"
                if var.help_text:
                    help_text += f": {var.help_text}"
                help_text += "<br/>"

        if cls.template_tag_packages:
            if cls.user_variable_defs:
                help_text += "<br/>"
            help_text += "<strong>"
            help_text += _('cdh.mail.custom.help_text.tags')
            help_text += "</strong><br/>"

            for package in cls.template_tag_packages:
                for tag in package.tags:
                    help_text += "<code>{% " + tag[0]

                    if tag[1]:
                        for arg in tag[1]:
                            help_text += f" {arg}"

                    help_text += " %}</code>"

                    if tag[2]:
                        help_text += f": {tag[2]}"
                    help_text += "<br/>"

        return mark_safe(help_text)

    @lru_cache
    def _get_template_from_string(self, string: str) -> Template:
        engine = Engine.get_default()
        return engine.from_string(string)

    @property
    def _has_sender(self) -> bool:
        return bool(self.sender)

    @property
    def _has_banner(self) -> bool:
        return bool(self.banner)

    @property
    def _has_footer(self) -> bool:
        return bool(self.footer)

    def render_preview(self):
        """Returns a rendered HTML document as would be sent as the HTML
        content.

        Uses the variable defaults as defined if nothing was supplied through
        the context param.
        """
        return self._get_html_body(True)

    def _get_html_context(self) -> dict:
        context = super()._get_html_context()

        context['has_sender'] = self._has_sender
        context['has_banner'] = self._has_banner
        context['has_footer'] = self._has_footer

        return context

    def _generate_template_block(self, name, contents) -> str:
        template = "{% block " + name + " %}"
        template += contents
        template += "{% endblock %}"

        return template

    def _generate_template_str(self) -> str:
        template = "{% extends '" + self.html_fallback_template + "' %}"

        for tag in self.template_tag_packages:
            template += "{% load " + tag.package + " %}"

        template += self._generate_template_block('content', self.contents)

        if self._has_sender:
            template += self._generate_template_block('sender', self.sender)
        if self._has_banner:
            template += self._generate_template_block('banner', self.banner)
        if self._has_footer:
            template += self._generate_template_block('footer', self.footer)

        return template

    def _get_html_body(self, preview=False) -> str:
        template = self._get_template_from_string(
            self._generate_template_str()
        )

        context = self._get_html_context()

        if preview:
            for var in self.user_variable_defs:
                # Only apply the default if we don't have any value in the
                # context already. Some previews are capable of adding some
                # more specifc context, and we don't want to overwrite those.
                if var.name not in context or not context[var.name]:
                    context[var.name] = var.preview_value

        # Mark any vars as safe if configured to do so
        for var in self.user_variable_defs:
            if var.name in context and var.safe:
                context[var.name] = mark_safe(context[var.name])

        try:
            return template.render(
                Context(context)
            )
        except Exception as e:
            logger.error("Error during HTML email generation", exc_info=True)

            if not self.fail_silently:
                raise e

            return ""

    def _get_plain_part(self, content: str) -> str:
        try:
            ret = self._get_template_from_string(content).render(
                Context(self._get_plain_context())
            )
            return "\n" + _strip_tags(ret)
        except Exception as e:
            logger.error("Error during plain-text-part email generation", exc_info=True)

            if not self.fail_silently:
                raise e

            return ""

    def _get_plain_body(self) -> str:
        context = {
            'content': self._get_plain_part(self.contents)
        }

        if self._has_sender:
            context['sender'] = self._get_plain_part(self.sender)
        if self._has_banner:
            context['banner'] = self._get_plain_part(self.banner)
        if self._has_footer:
            context['footer'] = self._get_plain_part(self.footer)

        try:
            return render_to_string(
                self.plain_fallback_template,
                context
            ).strip()
        except Exception as e:
            logger.error("Error during plain text email generation", exc_info=True)

            if not self.fail_silently:
                raise e

            return ""
