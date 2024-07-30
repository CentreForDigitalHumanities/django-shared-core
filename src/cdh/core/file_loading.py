from deprecated.sphinx import deprecated
from django.templatetags.static import static

js = set()
css = set()


@deprecated(
    version='3.1',
    reason="Fundamentally flawed. Please explore your own alternatives"
)
def add_js_file(file, reverse=True):
    """Registers a JS File to be loaded. Mostly intended for apps in the
    shared core to dynamically insert their files into the base template"""
    if reverse:
        file = static(file)

    js.add(file)


@deprecated(
    version='3.1',
    reason="Fundamentally flawed. Please explore your own alternatives"
)
def add_css_file(file, reverse=True):
    """Registers a CSS File to be loaded on this page. Mostly intended for apps
    in the shared core to dynamically insert their files into the base
    template"""
    if reverse:
        file = static(file)

    css.add(file)

