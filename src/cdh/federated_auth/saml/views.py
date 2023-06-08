from typing import Optional, Tuple

from django.shortcuts import render
from django.conf import settings

CONTACT_PERSON = 'contact_person'
CONTACT_TYPE = 'contact_type'
CONTACT_TYPE_TECHNICAL = 'contact_type'

GIVEN_NAME = 'given_name'
SURNAME = 'sur_name'
EMAIL = 'email_address'


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
                if CONTACT_TYPE in contact_person \
                   and contact_person[CONTACT_TYPE] == CONTACT_TYPE_TECHNICAL:
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
        'exception': exception,
        'contact_name': contact_name,
        'contact_email': contact_email,
    }
    return render(
        request,
        'djangosaml2/login_error.html',
        context=context,
        status=status
    )
