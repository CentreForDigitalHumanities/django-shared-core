# Django DH-IT Core library

These Django apps implement shared code for DH-IT Django projects. Developed in collaboration with the [UiL OTS Labs](https://github.com/UiL-OTS-labs)

## Currently targeting:
- Python 3.9
- Python 3.10 (experimental)
- Django 3.x
- Django 4.0 (experimental)

Older versions are not supported, please use a older release if needed

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

# Partly included libraries
These libraries are partly integrated into this codebase. 
This means that we still use the original package as a dependency, but parts of it have been copied and 
modified into this codebase as overrides. 

## vbuild
Partly overriden for integration into a larger Django infrastructure (the ``cdh.vue`` app)

Source: https://github.com/manatlan/vbuild

Licensed under the MIT license, see https://github.com/manatlan/vbuild/blob/master/LICENSE
