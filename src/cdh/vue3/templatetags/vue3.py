import datetime
import random
import string
import json
from functools import partial

from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


class VueJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if hasattr(obj, '_wrapped'):
            return super().encode(obj._wrapped)
        return super().encode(obj)

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)


def prop_const(const, context):
    return json.dumps(const, cls=VueJSONEncoder)


def prop_variable(expr, context):
    var = template.Variable(expr)
    return json.dumps(var.resolve(context), cls=VueJSONEncoder)


def prop_js(code, context):
    return code


def event_prop(name):
    return 'on' + name[0].upper() + name[1:]


@register.tag
def vue(parser, token):
    args = token.split_contents()

    # because we install components in a div by default, there's an option
    # to specify an inline display style when required by adding the word
    # 'inline' in the tag argument list
    inline = False
    if 'inline' in args:
        args.remove('inline')
        inline = True

    # in props we store (per prop) a fucntion that takes a context
    # and returns the prop value.
    # this is achieved by using partial() together with the prop_* functions
    # defined above.
    props = dict()

    component = args[1]
    for i in range(2, len(args)):
        if args[i][0] == ':':
            # prop binding
            if '=' in args[i]:
                (name, value) = args[i][1:].split('=', 1)
                if value[0] in ['"', "'"]:
                    # :prop="thing", treat thing as a javascript value
                    props[name] = partial(prop_js, value[1:-1])
                else:
                    # :prop=thing, treat thing as a python value
                    props[name] = partial(prop_variable, value)
            else:
                name = args[i][1:]
                # :prop, is the same as :prop=prop (treat prop as a python value)
                props[name] = partial(prop_variable, name)

        elif args[i][0] == '@':
            (name, value) = args[i][1:].split('=', 1)
            # @event="thing", thing should be a javascript function
            props[event_prop(name)] = partial(prop_js, value[1:-1])
        else:
            (name, value) = args[i].split('=', 1)
            if value[0] in ['"', "'"]:
                props[name] = partial(prop_const, value[1:-1])

    return VueRenderer(component, props, inline)


class VueRenderer(template.Node):
    def __init__(self, component, props, inline):
        self.component = component
        self.props = props
        self.inline = inline

    def render(self, context):
        binding_defs = []
        for prop, value in self.props.items():
            try:
                binding_defs.append('data["{}"] = {};'.format(prop, value(context)))
            except Exception:
                raise RuntimeError(f'Failed binding proeprty "{prop}"')

        binding = mark_safe('\n'.join(binding_defs))

        # add a random suffix to container id, to avoid collisions
        suffix = ''.join(random.sample(string.ascii_lowercase, 5))
        container = '_'.join(self.component.split('.') + [suffix])

        style = 'display:inline' if self.inline else 'width:100%'

        # Retrieve the CSP nonce if present
        nonce = ''
        if hasattr(context, 'request') and hasattr(context.request,
                                                   'csp_nonce'):
            nonce = context.request.csp_nonce

        return format_html(
            '''
            <div id="{container}" style="{style}"></div>
            <script nonce="{nonce}">
            document.addEventListener('DOMContentLoaded', (function() {{
            let data = {{}};
            {binding}
                createApp({component}, data).mount('#{container}')
            }}));
            </script>''',
            binding=binding,
            component=self.component,
            container=container,
            style=style,
            nonce=nonce,
        )


@register.simple_tag
def vue_assets():
    # read manifest json (based on vite output)
    with open(settings.VUE_MANIFEST) as f:
        manifest = json.load(f)

    out = []
    static = settings.STATIC_URL + 'vue/'
    if hasattr(settings, 'VUE_URL'):
        static = settings.VUE_URL

    for name, asset in manifest.items():
        if asset.get('isEntry'):
            for css in asset['css']:
                out.append('<link rel="stylesheet" href="{}"/>'.format(
                           static + css))
            out.append('<script type="text/javascript" src="{}"></script>'.format(
                       static + asset['file']))

    return format_html('\n'.join(out))
