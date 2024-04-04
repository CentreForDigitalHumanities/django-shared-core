from typing import Optional, Tuple

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import RedirectURLMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.conf import settings
from django.contrib import auth
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from djangosaml2.views import (
    LogoutInitView as DjangoSaml2LogoutInitView,
    _get_subject_id,
)

CONTACT_PERSON = "contact_person"
CONTACT_TYPE = "contact_type"
CONTACT_TYPE_TECHNICAL = "contact_type"

GIVEN_NAME = "given_name"
SURNAME = "sur_name"
EMAIL = "email_address"


def _get_contact_dict() -> Optional[dict]:
    """Tries to find a contact info dict from the SAML_CONFIG in the settings

    If only one dict of contact details is defined, it will always return
    that set.
    If multiple dicts are defined, it will try to find the dict with
    'contact_type' set to 'technical'. If none matches, it will return the first
    dict in the list.
    """
    if CONTACT_PERSON in settings.SAML_CONFIG:
        contact_people = settings.SAML_CONFIG[CONTACT_PERSON]

        # If only one defined, use that
        if len(contact_people) == 1:
            return contact_people[0]
        # If more are defined, try to search for the technical contact
        if len(contact_people) >= 1:
            for contact_person in contact_people:
                # If we have a match, return it
                if (
                    CONTACT_TYPE in contact_person
                    and contact_person[CONTACT_TYPE] == CONTACT_TYPE_TECHNICAL
                ):
                    return contact_person

            # If no technical contact info was found, return the first as a
            # fallback
            return contact_people[0]

    return None


def _get_contact_info() -> Tuple[Optional[str], Optional[str]]:
    """Extracts the contact name and contact email from a contact_person set

    It will concat given_name and sur_name if possible. If none is provided, but
    an e-mail address was, it will use the e-mail address as the contact_name.
    """
    contact_name = None
    contact_email = None

    # If we could get info from settings
    # Note: uses walrus operator, google if not familiar ;)
    if contact_person := _get_contact_dict():

        if GIVEN_NAME in contact_person and contact_person[GIVEN_NAME]:
            contact_name = contact_person[GIVEN_NAME]

        if SURNAME in contact_person and contact_person[SURNAME]:
            # If given name is not set. Should not happen, but you never know
            if contact_name is None:
                contact_name = contact_person[SURNAME]
            else:
                contact_name = f"{contact_name} {contact_person[SURNAME]}"

        if EMAIL in contact_person and contact_person[EMAIL]:
            contact_email = contact_person[EMAIL]

        # If we only have an email, fill in the email as the name
        # This makes the template a bit simpler
        if contact_name is None and contact_email is not None:
            contact_name = contact_email

    return contact_name, contact_email


def login_error(request, exception=None, status=403, **kwargs):
    """Custom ACS error view, adding contact details to context for custom
    templates
    """
    contact_name, contact_email = _get_contact_info()

    context = {
        "exception": exception,
        "contact_name": contact_name,
        "contact_email": contact_email,
    }
    return render(
        request, "djangosaml2/login_error.html", context=context, status=status
    )


class LogoutInitView(
    RedirectURLMixin, TemplateResponseMixin, ContextMixin, DjangoSaml2LogoutInitView
):
    """Custom LogoutInitView to handle logout requests for non-SAML users.
    Basically merges Django's LogoutView with DjangoSaml2's LogoutInitView
    """

    next_page = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = "registration/logged_out.html"
    extra_context = None

    def get(self, request, *args, **kwargs):
        subject_id = _get_subject_id(request.saml_session)

        if subject_id is None:
            # No saml session present, doing local logout
            auth.logout(request)
            next_page = self.get_next_page()
            if next_page:
                # Redirect to this page until the session has been cleared.
                return HttpResponseRedirect(next_page)

            return self.render_to_response(self.get_context_data())

        # SAML session present, proceeding to do SSO logout
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = get_current_site(self.request)
        context.update(
            {
                "site": current_site,
                "site_name": current_site.name,
                "title": _("Logged out"),
                **(self.extra_context or {}),
            }
        )
        return context

    def get_next_page(self):
        if self.next_page is not None:
            next_page = resolve_url(self.next_page)
        elif settings.LOGOUT_REDIRECT_URL:
            next_page = resolve_url(settings.LOGOUT_REDIRECT_URL)
        else:
            next_page = self.next_page

        if (
            self.redirect_field_name in self.request.POST
            or self.redirect_field_name in self.request.GET
        ):
            next_page = self.request.POST.get(
                self.redirect_field_name, self.request.GET.get(self.redirect_field_name)
            )
            url_is_safe = url_has_allowed_host_and_scheme(
                url=next_page,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            # Security check -- Ensure the user-originating redirection URL is
            # safe.
            if not url_is_safe:
                next_page = self.request.path
        return next_page
