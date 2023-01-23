from os import path
from pathlib import Path
from urllib.parse import urljoin

import saml2
import saml2.saml


SAML_ATTRIBUTE_MAPPING = {
    'uushortid':  ('username',),
    'mail':     ('email',),
    'givenName': ('first_name',),
    'uuprefixedsn':  ('last_name',),
}

# SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'username'

SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_REDIRECT
SAML_IGNORE_LOGOUT_ERRORS = True
SAML_SESSION_COOKIE_NAME = 'saml_session'

AUTHENTICATION_BACKENDS = (
    'django.contrib.federated_auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',
)

def create_saml_config(
        name: str,
        base_url: str,
        key_file: str,
        cert_file: str,
        idp_metadata: str,
        contact_given_name: str = "DH-IT",
        contact_sur_name: str = "",
        contact_email: str = "dh-it@uu.nl",
        required_attributes: list = None,
        entity_id: str = None,
        url_prefix: str = 'saml/',
        name_id_format: str = saml2.saml.NAMEID_FORMAT_PERSISTENT,
        attribute_map_dir: str = None,
        debug: bool = False,
        config_overrides: dict = None,
):
    if attribute_map_dir is None:
        attribute_map_dir = path.join(
            Path(__file__).parent.absolute(),
            'attribute-maps'
        )

    if required_attributes is None:
        required_attributes = ['firstname',
                                                'lastname',
                                                'sn',
                                                'mail']

    if config_overrides is None:
        config_overrides = {}

    base_saml_url = urljoin(base_url, url_prefix)
    print(base_saml_url, base_url, url_prefix)

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
                        # TODO: configurable?
                    ],
                    # url and binding to the single logout service view
                    # do not change the binding or service name
                    'single_logout_service':      [
                        # Disable next two lines for HTTP_REDIRECT for IDP's that only support HTTP_POST. Ex. Okta:
                        (logout_service_url,
                         SAML_DEFAULT_BINDING),
                        # TODO: configurable?
                        # ('http://localhost:8000/saml2/ls/post',
                        #  saml2.BINDING_HTTP_POST),
                    ],
                },

                'signing_algorithm':           saml2.xmldsig.SIG_RSA_SHA256,
                'digest_algorithm':            saml2.xmldsig.DIGEST_SHA256,

                # Mandates that the identity provider MUST authenticate the
                # presenter directly rather than rely on a previous security context.
                'force_authn':                 False,

                # Enable AllowCreate in NameIDPolicy.
                'name_id_format_allow_create': True, # TODO config

                # attributes that this project need to identify a user
                'required_attributes':         required_attributes,

                'want_response_signed':        True,
                'authn_requests_signed':       True,
                'logout_requests_signed':      True,
                # Indicates that Authentication Responses to this SP must
                # be signed. If set to True, the SP will not consume
                # any SAML Responses that are not signed.
                'want_assertions_signed':      True,

                'only_use_keys_in_metadata':   True,

                # When set to true, the SP will consume unsolicited SAML
                # Responses, i.e. SAML Responses for which it has not sent
                # a respective SAML Authentication Request.
                'allow_unsolicited':           True,
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
        'contact_person':      [
            {
                'given_name':    contact_given_name,
                'sur_name':      contact_sur_name,
                'company':       'Universiteit Utrecht',
                'email_address': contact_email,
                'contact_type':  'technical'
            },
        ],
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
