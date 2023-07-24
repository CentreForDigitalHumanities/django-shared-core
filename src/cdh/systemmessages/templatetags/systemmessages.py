from django import template

from ..models import SystemMessage
from ...core.templatetags.cdh_filters import SetVarNode

register = template.Library()


@register.inclusion_tag('systemmessages/message_list.html')
def display_system_messages(container=True,):
    """Displays the system messages, optionally in an .uu-container"""

    messages = SystemMessage.objects.get_current_messages()

    return {
        'system_messages': messages,
        'container': container,
    }


@register.tag(name='load_system_messages')
def load_system_messages(parser, token):
    """Loads the system messages in as a variable. By default, they will be
    saved under 'system_messages'
    {% load_system_messages [as varname] %}
    """
    parts = token.split_contents()

    len_parts = len(parts)

    if (len_parts != 1 and len_parts != 3) or \
       (len_parts == 3 and parts[1] != 'as'):
        raise template.TemplateSyntaxError(
            "'load_system_messages' must either be called without arguments "
            "({% load_system_messages %}) or with 'as [variable]' ({% "
            "load_system_messages as [variable] %})."
        )

    var_name = 'system_messages'
    if len_parts == 3:
        var_name = parts[2]

    # Just re-use the same node we use for our 'set' tag, it does the job
    # just fine
    return SetVarNode(var_name, SystemMessage.objects.get_current_messages())

