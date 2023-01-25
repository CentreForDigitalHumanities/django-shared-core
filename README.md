# CDH Django libraries

A collection of Django apps for CDH/DH-IT Django projects. Developed by the 
[ILS Labs](https://github.com/UiL-OTS-labs) and the 
[DH-IT Faculty Portal Development and Support Team](https://github.com/DH-IT-Portal-Development/django-shared-core)

Documentation provided here: https://dh-it-portal-development.github.io/django-shared-core/

## Currently targeting:
- Python 3.9
- Python 3.10
- Django 4.0

Tests are run using these versions; Some apps have lower requirements, but are 
not tested against these lower versions. check the app collection below for
specifics.

## App collection

### Core (``cdh.core``)

Base block for pure-Django projects, containing base templates, generic views,
extra form/model fields and other miscellaneous code.

Requires Django >= 4;

### Federated authentication (``cdh.federated_auth``)

Helper app to connect a Django application as a Service Provider to a Federated
Authentication realm. Currently only supports SAML.

Requires Django >= 2;

### Files (``cdh.files``)

An alternative to Django's built-in `FileField`, that manages a file's 
lifecycle, allows for copy-on-write sharing of files, is object-storage ready,
allows arbitrary metadata to be added and most-importantly makes sysadmins 
happy.

Soft requirement on ``cdh.core``, can work standalone if needed.
Required Django >= 4.

### Integration platform (``cdh.integration_platform``)

Ready-to-use API clients for the UU's integration platform.

Requires ``cdh.rest``;
Requires Django >= 3;

### Rest (``cdh.rest``)

Contains code for both server and client roles. Server code contains some mixins,
JWT authentication support and other helpfull snippits.

Client code contains a full Django-ORM inspired REST client, for easy
(de)serialization and transactions with REST APIs.

Requires Django >= 3;

### System messages (``cdh.systemmessages``)

Simple app to quickly add a 'system message' system to your app, useful for
temporary announcements. 

Requires Django >= 2;

### Vue (``cdh.vue``)

Helper app to (more) easily integrate small(-ish) Vue components in your Django
templates.

Requires Django >= 3;

# Included libraries
These libraries have been completely integrated into this codebase

## django-encrypted-model-fields 
Modified for better Django 2.2 support and some additional tweaks.

Source: https://gitlab.com/lansharkconsulting/django/django-encrypted-model-fields/

Licenced under the MIT licence, see `cdh/core/fields/LICENSE`.

## django-js-urls
Modified to better suit our usage

Source: https://github.com/impak-finance/django-js-urls

Licenced under the MIT license, see `cdh/core/js_urls/LICENSE`

## Select2 Bootstrap 5 Theme
Modified to always apply, minor fixes and better SCSS integration

Source: https://github.com/apalfrey/select2-bootstrap-5-theme

Licenced under the MIT license, see `scss/select2-bootstrap/LICENSE`

# Partly included libraries
These libraries are partly integrated into this codebase. 
This means that we still use the original package as a dependency, but parts of it have been copied and 
modified into this codebase as overrides. 

## vbuild
Partly overriden for integration into a larger Django infrastructure (the ``cdh.vue`` app)

Source: https://github.com/manatlan/vbuild

Licensed under the MIT license, see https://github.com/manatlan/vbuild/blob/master/LICENSE
