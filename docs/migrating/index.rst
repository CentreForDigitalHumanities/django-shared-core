Migrating
=========

Starting from version 3.0, this file tracks any changes one needs to
make to update to the listed version. Please note that this does not
include all new features of a given release.

There are three kinds of changes: - Required: stuff won’t work
(correctly) if you don’t do this - Recommended: stuff won’t work in a
future version if you don’t do this - Optional: changes that are not
(and wil not be) necessary, but is recommended to use anyway

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

If that’s not possible (e.g. not using Django 4), you can ask the portal
dev team to provide you some CSS to make table-based forms work again.

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
recommended to create your own base template by extending one of two
base templates included in the library.

Convention

This will become mandatory in version 4.0.

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
