from django import template

register = template.Library()


@register.inclusion_tag('base/messages.html')
def display_messages(messages, container=True,):
    """Adds the django messages, optionally in an .uu-container"""

    return {
        'messages': messages,
        'container': container,
    }

