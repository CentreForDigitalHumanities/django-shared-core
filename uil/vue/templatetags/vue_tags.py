from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from uil.vue.components import Vue
from uil.vue.utils import get_vue_templates

register = template.Library()


@register.simple_tag
def load_vue_component(root_component, nonce=''):
    comp = Vue.get_component(root_component)

    if nonce:
        nonce = f"nonce='{nonce}'"

    output = ""
    output += '<script src="{}" {}></script>\n'.format(
        reverse('uil.vue:vue-js', args=[root_component, ]),
        nonce
    )
    output += '<link href="{}" rel="stylesheet" />\n'.format(
        reverse('uil.vue:vue-css', args=[root_component, ])
    )

    for template_id, template in get_vue_templates(comp):
        output += '<script type="text/x-template" id="{}" {}>{}</script>\n'.format(
            template_id,
            nonce,
            template,
        )

    return mark_safe(output)
