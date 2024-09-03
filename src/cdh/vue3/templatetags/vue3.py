import datetime
import random
import string
import json
from functools import partial

from django import template
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

register = template.Library()


class VueJSONEncoder(DjangoJSONEncoder):
    def encode(self, obj):
        if hasattr(obj, "_wrapped"):
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
    return "on" + name[0].upper() + name[1:]


@register.simple_tag
def load_vue_libs():
    if settings.DEBUG:
        vue = static("cdh.vue3/vue/vue.global.js")
        vue_i18n = static("cdh.vue3/vue/vue-i18n.global.js")
    else:
        vue = static("cdh.vue3/vue/vue.global.prod.js")
        vue_i18n = static("cdh.vue3/vue/vue-i18n.global.prod.js")

    return format_html(
        """
<script src="{vue}"></script>
<script src="{vue_i18n}"></script>
    """,
        vue=vue,
        vue_i18n=vue_i18n,
    )


@register.tag
def vue(parser, token):
    args = token.split_contents()

    # because we install components in a div by default, there's an option
    # to specify an inline display style when required by adding the word
    # 'inline' in the tag argument list
    inline = False
    if "inline" in args:
        args.remove("inline")
        inline = True

    # in props we store (per prop) a fucntion that takes a context
    # and returns the prop value.
    # this is achieved by using partial() together with the prop_* functions
    # defined above.
    props = dict()

    component = args[1]
    for i in range(2, len(args)):
        if args[i][0] == ":":
            # prop binding
            if "=" in args[i]:
                (name, value) = args[i][1:].split("=", 1)
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

        elif args[i][0] == "@":
            (name, value) = args[i][1:].split("=", 1)
            # @event="thing", thing should be a javascript function
            props[event_prop(name)] = partial(prop_js, value[1:-1])
        else:
            (name, value) = args[i].split("=", 1)
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
                val = value(context)
                binding_defs.append('data["{}"] = {};'.format(prop, val))
            except Exception as e:
                print(e)
                raise RuntimeError(f'Failed binding proeprty "{prop}"')

        binding = mark_safe("\n".join(binding_defs))

        # add a random suffix to container id, to avoid collisions
        suffix = "".join(random.sample(string.ascii_lowercase, 5))
        container = "_".join(self.component.split(".") + [suffix])

        style = "display:inline" if self.inline else "width:100%"

        # Retrieve the CSP nonce if present
        nonce = ""
        if hasattr(context, "request") and hasattr(context.request, "csp_nonce"):
            nonce = context.request.csp_nonce

        return format_html(
            """
            <div id="{container}" style="{style}"></div>
            <script nonce="{nonce}">
            (function() {{
                if (typeof Vue !== "undefined") {{
                   var createApp = Vue.createApp;
                }}
                let data = {{}};
                {binding}
                const app = createApp({component}, data)
                
                if (typeof VueI18n !== "undefined") {{
                   const i18n = VueI18n.createI18n({{
                      legacy: false,
                      locale: '{language}', 
                      fallbackLocale: 'en',
                   }});
                   app.use(i18n);
                }}
                
                app.mount('#{container}');
            }})();
            </script>""",
            binding=binding,
            component=self.component,
            container=container,
            style=style,
            nonce=nonce,
            language=get_language(),
        )
