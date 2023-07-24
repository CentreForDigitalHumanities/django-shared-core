Migrating
=========

Starting from version 3.0, this file tracks any changes one needs to
make to update to the listed version. Please note that this does not
include all new features of a given release.

There are three kinds of changes: - Required: stuff won’t work
(correctly) if you don’t do this - Recommended: stuff won’t work in a
future version if you don’t do this - Optional: changes that are not
(and wil not be) necessary, but is recommended to use anyway

3.1
---

When upgrading to this version, it's recommended to remove the old version of
the library first.

As 3.1 is a minor release, no code breaking changes are expected. (If they are
there, it's a regression and an issue should be opened).

However, there are some non-code breaking changes and deprecations.

Required
~~~~~~~~

Packaging
^^^^^^^^^

DSC < 3.1 uses a deprecated packaging setup, which is replaced with a modern,
spec compliant setup. During this change, the dependency handling was overhauled
to use 'optional dependencies' to reduce the amount of dependencies needed to
your app's needs.

As a result, your dependency spec has to be updated to ensure the proper
dependencies are installed. To recreate old behaviour, use the following line:

``cdh-django-core[all] @ git+https://github.com/DH-IT-Portal-Development/django-shared-core.git@<version>``

Replacing ``<version>`` with the latest DSC release tag. (e.g. ``v3.1.0``).

Optionally, you can only select the dependencies needed for your app by
specifying which apps of this library you actually use. For example:

``cdh-django-core[core,files,rest] @ git+https://github.com/DH-IT-Portal-Development/django-shared-core.git@[version]``

The values you can specify correspond to the app names (sans ``cdh.``) of
the apps you use.

Three special values are also present:

- ``docs``: dependencies you need to create the docs only.
- ``all``: all dependencies for all apps
- ``dev``: dependencies you need to develop the library, plus all in ``all``
  and ``docs``

SCSS
^^^^

Previously, the SCSS files used for the UU Bootstrap version shipped with the
library were also present in the build package. This is no longer the case.
Using those files was never officially supported, thus this change does not
warrant a major update.

If your application was relying on those files for its own SCSS, you should
supply these files yourself. The UU Bootstrap project will provide most of
these in the future in some way, this doc should be updated before 3.1
actually releases with more details. Poke Ty if this was not the case.

3.0
---

Required
~~~~~~~~

Namespace change
^^^^^^^^^^^^^^^^

3.0 moves all apps from the ``uil`` namespace to the ``cdh`` namespace.
It should be enough just to replace all ``uil.*`` imports to ``cdh.*``.

Please remember to update the ``MIDDLEWARE`` and ``INSTALLED_APPS``
settings and the url config imports as well.

REST Client
^^^^^^^^^^^

``uil.rest_client`` has been replaced in favor of ``cdh.rest``, which
also includes code for REST servers.

In practice, migrating should be as simple as replacing
``uil.rest_client`` imports with ``cdh.rest.client``. (The base package
does not import anything.)

REST Serializers
^^^^^^^^^^^^^^^^

``uil.core.rest.serializers`` has been moved to
``cdh.rest.server.serializers``.

Bootstrap update
^^^^^^^^^^^^^^^^

We now use a completely new CSS stack, based upon Bootstrap 5. This
brings several breaking changes. Please see `the migration
documentation <https://dh-it-portal-development.github.io/bootstrap-theme/migrating/>`__.

In addition, table based forms now need the ``.table`` class to be
applied to the ``<table>``

Recommended
~~~~~~~~~~~

Switch to new mailing code
^^^^^^^^^^^^^^^^^^^^^^^^^^

``cdh.core.utils.mail_utils`` has been deprecated, switch to
``cdh.core.mail`` instead. Either use the utils functions, which have a
similar API to the old methods, or use the new class based method, which
offer more customization options.

See the docstrings of both for more information.

App-specific base template
^^^^^^^^^^^^^^^^^^^^^^^^^^

For both future compatibility and more customization options, it’s
recommended to create your own app-specific base template by extending one of
two base templates included in the library.

Due to the deprecation of (most) ``include_if_exists`` subtemplates, this will
become mandatory in version 4.0. (See sub-templates below)

Minimal template
''''''''''''''''

A new base template ``base/minimal.html`` sets up ``<head>`` and empty
blocks for ``uu-header``, ``uu-navbar``, ``uu-content`` and
``uu-footer``.

This template allows for full customization of a ``UU layout`` page, but
provides no layout of it’s own. so it’s best to consult `the UU layout
documentation <https://dh-it-portal-development.github.io/bootstrap-theme/uu-layout/>`__.

Use this template if you’re going to implement your own header **and**
footer.

Please note that this template has no Django Messages support out of the
box, so you’ll need to add this on your own to ``uu-content``. You can
use the ``{% display_messages messages %}`` template tag to do so (load
using ``{% load messages %}``.

‘Base’ template
'''''''''''''''

The existing ``base/base.html`` has been re-implemented on top of
``base/minimal.html``. Generally it’s recommended to use this as your
base template unless you want to modify more than one of the four base
blocks.

Sub-templates
'''''''''''''

Several ``include_if_exists`` sub-templates are deprecated and will be
removed in version 4.0. Instead, your app-specific template should
extend the (new) corresponding content blocks:

-  ``base/site_title.html`` -> ``header_title``
-  ``base/site_html_head.html`` -> ``html_head``\ [1]
-  ``base/site_header.html`` -> ``site_header`` (``base.html`` only)
-  ``base/login_header.html`` -> ``login_header`` (``base.html`` only)

[1] This block is widely used to add page specific JS/CSS. Thus, you’ll
need to add ``{{ block.super }}`` on those pages to preserve the content
of the original block.

Alternatively, you can load in global app-specific CSS and JS files by
using ``add_js_file`` and ``add_css_file`` from
``cdh.core.file_loading``. (Recommended usage is adding these calls to
the ``ready`` method of your Django App Config ``apps.py``)

Mailing
^^^^^^^

The methods in ``cdh.core.utils.mail_utils`` are deprecated and will be
removed in a future version. Its replacement is ``cdh.core.mail``, see
the documentation in those files for specific implementation details. In
general, you can use the util functions for simple cases, or switch to
the ``Email`` classes for more functionality.

Plain text templates can be used without modification. HTML emails will
need to extend the mail template, and use the content block to fill the
template.

This new implementation does not require both plain and HTML templates,
and will automatically generate the missing one. However, keep in mind
that hyperlinks are stripped to plain text when generating a plain text
version. (Thus: if you have links, also have the full link as text
somewhere. Or use both plain and html templates.)

Optional
~~~~~~~~

Custom SCSS setup
^^^^^^^^^^^^^^^^^

The new bootstrap theme is built using SCSS. For ease of use, this library
supplies a pre-built version that is enabled by default.

If you require overrides which cannot be done using the CSS vars, you can create
your own SCSS setup. The easiest way to get started is probably to copy both
``package.json`` and the ``scss`` folder to your project.

Then, change the build commands to output the generated CSS into one of your
Django app's ``static/cdh.core`` folder. (Note: you might need to play around
with your app loading order to make sure your local version overrides the
provided ones)

``INSTALLED_APPS`` import order
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

3.0 introduces some overrides for Django Admin and Django Impersonate
templates.

To ensure proper overriding of said templates, it’s recommended to move
all ``cdh.*`` apps to the top of ``INSTALLED_APPS``.

‘Status’ indicator
^^^^^^^^^^^^^^^^^^

The updated base template will add warnings to the header if you’re

-  Running in debug mode (Local Development Server)
-  Impersonating a user (Impersonating user - {user})
-  Running on an acceptation server (Acceptation Server)

The first two work out of the box, but for the acceptation warning to
work you’ll need to:

-  Add ``'cdh.core.context_processors.acceptation'`` to the
   ``context_processors`` settings in ``TEMPLATES``
-  Create a new ``ACCEPTATION`` boolean setting (recommended to place
   next to ``DEBUG``)
