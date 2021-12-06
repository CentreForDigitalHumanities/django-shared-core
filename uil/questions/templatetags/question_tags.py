from django import template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('questions/tags/display_question_tag.html')
def display_question(question, **kwargs):

    tag_context = {'test': 123,
                   'question': question,
                   'title': question.title,
                   'segments': question.segments,
    }

    tag_context.update(kwargs)

    return tag_context

@register.inclusion_tag('questions/tags/display_question_tag.html')
def ask_question(question, **kwargs):

    tag_context = display_question(question, **kwargs)
    tag_context['editing'] = True
    return tag_context

@register.simple_tag(takes_context=True)
def render_segment(context, segment):
    """Because we want the function to know if it should display
    values or a form, we take context instead of arguments.

    We expect this to be run in a for loop with a "segment"
    loop variable"""

    segment.context.update(context.flatten())
    return segment.render()
