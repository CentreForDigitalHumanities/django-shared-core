"""SAML settings for Django settings.py

Import the contents of this module in your ``settings.py`` to easily setup SAML
for your Django app. This module contains all needed settings for a basic
SAML setup, you might need to change some settings for your app.

Basic usage:

.. code-block:: python

    try:
        from cdh.federated_auth.saml.settings import *

        SAML_CONFIG = create_saml_config(
            base_url='https://sp.example.org/',
            name='My awesome app',
            key_file=path.join(BASE_DIR, 'private.key'),
            cert_file=path.join(BASE_DIR, 'public.cert'),
            idp_metadata='https://idp.example.org/metadata/',
        )

        # Any overrides go here

    except:
        print('Could not load SAML settings')

This will set up a minimal DjangoSAML2 setup. Please refer to the source code
for all settings and to the docstring :meth:`create_saml_config` for more info.

.. warning::
   You will also need to add additional config elsewhere in your app, not
   described here. Please refer to the general CDH SAML setup guide for more
   info.
"""

from os import path
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin

import saml2
import saml2.saml

# The default attribute map for UU IdP, override for more attributes/other IdP's
SAML_ATTRIBUTE_MAPPING = {
    'uuShortID':  ('username',),
    'mail':     ('email',),
    'givenName': ('first_name',),
    'uuPrefixedSn':  ('last_name',),
}

SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_REDIRECT  # or saml2.BIND_HTTP_POST
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_REDIRECT # or saml2.BIND_HTTP_POST

# Set this to 'False' if your app needs to be paranoid. Generally not needed.
SAML_IGNORE_LOGOUT_ERRORS = True
SAML_SESSION_COOKIE_NAME = 'saml_session'

# This will override the default Django setting, but in more complicated auth
# setups you'll need to override this. Make sure Saml2Backend is below
# ModelBackend!
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',
)

# This view is used to display any errors during login assertion processing
# (In layman terms: when the user has logged into the IdP, during processing
# of the login details the IdP send back).
# Our custom view displays a somewhat friendly message with contact details.
# It's generally recommended to override the 'djangosaml2/login_error.html'
# template if you want to customize this page. Overriding the view should only
# be necessary if you need extra context data.
SAML_ACS_FAILURE_RESPONSE_FUNCTION = 'cdh.federated_auth.saml.views.login_error'


def create_saml_config(
        name: str,
        base_url: str,
        key_file: str,
        cert_file: str,
        idp_metadata: str,
        *,
        entity_id: Optional[str] = None,
        url_prefix: str = 'saml/',
        contact_person: Optional[List[dict]] = None,
        contact_given_name: str = "Humanities IT",
        contact_sur_name: str = "",
        contact_email: str = "dh-it@uu.nl",
        required_attributes: Optional[list] = None,
        optional_attributes: Optional[list] = None,
        name_id_format: str = saml2.saml.NAMEID_FORMAT_TRANSIENT,
        name_id_allow_create: bool = True,
        attribute_map_dir: Optional[str] = None,
        force_authn: bool = False,
        allow_unsolicited: bool = False,
        want_response_signed: bool = False,
        authn_requests_signed: bool = True,
        logout_requests_signed: bool = True,
        want_assertions_signed: bool = True,
        debug: bool = False,
        config_overrides: Optional[dict] = None,
):
    """A function to generate the `SAML_CONFIG` setting

    Keyword arguments are optional. Most arguments are named after the PySAML2
    config keys, it is recommended you consult the PySAML2 docs as well:
    https://pysaml2.readthedocs.io/en/latest/howto/config.html

    URL generation
    --------------

    This function generates a lot of URLs for you, so it's important your make
    sure your values for `base_url` and `url_prefix` is correct. For example:
    If your SP's metadata is located at 'https://sp.example.org/saml/metadata'
    'https://sp.example.org/' is your `base_url` and 'saml/' is your
    `url_prefix`.

    NameID
    ------

    The SAML protocol uses a NameID to identify users/sessions. The ID itself is
    often a (pseudo)random string or a hash. You have the option to use
    persistent or transient NameIDs, which can be set using the
    `name_id_format` keyword argument.

    When using persistent NameIDs, the IdP will (try to) use the same ID every
    time a particular user logs in. Transient IDs will be unique for every
    session, thus a user will receive a new one every time they log in.
    Persistent IDs are recommended when using the NameID as the primary
    identifier, transient is recommended otherwise. The pro's and cons of
    both approaches are out of scope for this docstring.

    Please note that not all IdPs guarantee that persistent ID's will never
    change, so please contact your IdP's contact to ask if they do before using
    it as the primary identifier.

    Example minimal usage:

    .. code-block:: python

      SAML_CONFIG = create_saml_config(
        base_url='https://sp.example.org/',
        name='My awesome app',
        key_file=path.join(BASE_DIR, 'private.key'),
        cert_file=path.join(BASE_DIR, 'public.cert'),
        idp_metadata='https://idp.example.org/metadata/',
      )

    Required params:
    ----------------

    :param name: Human-readable name of this SP (e.g. My Awesome App)
    :param base_url: The base URL of the SP, including protocol.
                     (e.g. https://sp.example.org/)
    :param key_file: The location of your private key of the SSL cert on the
                     filesystem.
    :param cert_file: The location of your SSL cert on the filesystem
    :param idp_metadata: The URL of the IDP's metadata
                         (e.g. https://idp.example.org/metadata/)

    Optional params:
    ----------------

    :param url_prefix: The URL prefix for all SAML views. Defaults to 'saml'.
                       It should be the same as the path that is used in the
                       urlpatterns when including the SAML urlpatterns.
                       See above for more information
    :param entity_id: The entity ID of the SP, by convention the URL of the SP's
                      metadata. If omitted, it will be autogenerated using
                      `base_url` and `url_prefix`.
    :param contact_person: A list of dicts, containing the contact information
                           for this SP. If not set, it will be generated using
                           `contact_given_name`, `contact_sur_name` and
                           `contact_email`. Please consult the PySAML2 docs for
                           the exact format
    :param contact_given_name: The first name of the technical contact (or
                               the department name). Ignored if
                               `contact_person` is set
    :param contact_sur_name: The surname of the technical contact (or empty).
                             Ignored if `contact_person` is set
    :param contact_email: The email of the technical contact. Ignored if
                          `contact_person` is set
    :param required_attributes: A list of attributes that are needed for
                                successful authentication in the SP. If not set,
                                defaults to: `givenName`, `uuprefixedsn`,
                                `uushortid`, `mail`
    :param optional_attributes: A list of attributes that the SP would like
                                to have. Not required and defaults to an
                                empty list
    :param name_id_format: NAMEID_FORMAT_PERSISTENT or NAMEID_FORMAT_TRANSIENT.
                           Defaults to transient.
    :param name_id_allow_create: Sets the default value for AllowCreate on
                                 login requests. Defaults to True.
                                 Only applicable to persistent NameID's. Note:
                                 best to leave this value alone if you are 
                                 unsure. 
    :param attribute_map_dir: The location of the PySAML2 SAML attribute files.
                              If omitted, the library-provided files are used.
    :param force_authn: If set to 'True', a user must always authenticate when
                        logging into your SP. When set to 'False', existing
                        sessions on the IdP may be used instead. (In other
                        words, if a user has just logged into a different SP,
                        the IdP may skip authentication and log the user in
                        directly). Defaults to False.
    :param allow_unsolicited: If the SP accepts login attempts it has not itself
                              initiated. Defaults to `False`. This happens if
                              a different SP initiates the login for this SP.
    :param want_response_signed: False, it errors on UU IdP's if True.
    :param authn_requests_signed: Defaults to True per UU requirements.
    :param logout_requests_signed: Whether logout requests need to be signed.
    :param want_assertions_signed: Defaults to True per UU requirements.
    :param debug: Enables detailed debug output if set to true.
    :param config_overrides: A dict that will be merged with the final output
                             before returning. Can be used to override some data
                             in the resulting SAML_CONFIG that cannot be changed
                             using any of the provided arguments.
                             Please consider opening an issue/a PR to add the
                             required argument first, it might benefit other
                             users as well!
    :return: The computed value of `SAML_CONFIG`
    """
    if attribute_map_dir is None:
        attribute_map_dir = path.join(
            Path(__file__).parent.absolute(),
            'attribute-maps'
        )

    if required_attributes is None:
        required_attributes = ['givenName', 'uuprefixedsn', 'uushortid', 'mail']

    if optional_attributes is None:
        required_attributes = []

    if contact_person is None:
        contact_person = [
            {
                'given_name':    contact_given_name,
                'sur_name':      contact_sur_name,
                'company':       'Universiteit Utrecht',
                'email_address': contact_email,
                'contact_type':  'technical'
            },
        ]

    if config_overrides is None:
        config_overrides = {}

    base_saml_url = urljoin(base_url, url_prefix)

    if entity_id is None:
        entity_id = urljoin(base_saml_url, 'metadata/')

    acs_url = urljoin(base_saml_url, 'acs/')
    logout_service_url = urljoin(base_saml_url, 'ls/')

    saml_config = {
        # full path to the xmlsec1 binary programm
        'xmlsec_binary':       '/usr/bin/xmlsec1',

        # your entity id, usually your subdomain plus the url to the metadata view
        'entityid':            entity_id,

        # directory with attribute mapping
        'attribute_map_dir': attribute_map_dir,

        # Permits to have attributes not configured in attribute-mappings
        # otherwise...without OID will be rejected
        'allow_unknown_attributes': True,

        # this block states what services we provide
        'service':             {
            # we are just a lonely SP
            'sp': {
                'name':                        name,
                'name_id_format':              name_id_format,
                'name_id_policy_format':       name_id_format,

                'endpoints':                   {
                    # url and binding to the assetion consumer service view
                    # do not change the binding or service name
                    'assertion_consumer_service': [
                        (acs_url, saml2.BINDING_HTTP_POST),
                    ],
                    # url and binding to the single logout service view
                    # do not change the binding or service name
                    'single_logout_service':      [
                        # Disable next two lines for HTTP_REDIRECT for IDP's that only support HTTP_POST. Ex. Okta:
                        (logout_service_url,
                         SAML_DEFAULT_BINDING),
                    ],
                },

                'signing_algorithm':           saml2.xmldsig.SIG_RSA_SHA256,
                'digest_algorithm':            saml2.xmldsig.DIGEST_SHA256,

                # Mandates that the identity provider MUST authenticate the
                # presenter directly rather than rely on a previous security context.
                'force_authn':                 force_authn,

                # Enable AllowCreate in NameIDPolicy.
                'name_id_format_allow_create': name_id_allow_create,

                # attributes that this project would like to have for a user
                'optional_attributes':         optional_attributes,
                # attributes that this project need to identify a user
                'required_attributes':         required_attributes,

                'want_response_signed':        want_response_signed,
                'authn_requests_signed':       authn_requests_signed,
                'logout_requests_signed':      logout_requests_signed,
                # Indicates that Authentication Responses to this SP must
                # be signed. If set to True, the SP will not consume
                # any SAML Responses that are not signed.
                'want_assertions_signed':      want_assertions_signed,

                'only_use_keys_in_metadata':   True,

                # When set to true, the SP will consume unsolicited SAML
                # Responses, i.e. SAML Responses for which it has not sent
                # a respective SAML Authentication Request.
                'allow_unsolicited':           allow_unsolicited,
            },
        },

        # where the remote metadata is stored, local, remote or mdq server.
        # One metadatastore or many ...
        'metadata': {
            'remote': [
                {
                    "url": idp_metadata
                },
            ],
        },

        # set to 1 to output debugging information
        'debug':               1 if debug else 0,

        # Signing
        'key_file':            key_file,  # private part
        'cert_file':           cert_file,  # public part

        'valid_for': 365 * 24,


        # Encryption
        'encryption_keypairs': [{
            'key_file':  key_file,  # private part
            'cert_file': cert_file,  # public part
        }],

        # own metadata settings
        'contact_person': contact_person,

        # you can set multilanguage information here
        'organization':        {
            'name':         [
                ('Utrecht University', 'en'),
                ('Universiteit Utrecht', 'nl'),
            ],
            'display_name': [
                ('Utrecht University', 'en'),
                ('Universiteit Utrecht', 'nl'),
            ],
            'url':          [
                ('http://www.uu.nl', 'nl'),
                ('http://www.uu.nl/en', 'en')
            ],
        },
    }

    saml_config.update(config_overrides)

    return saml_config
