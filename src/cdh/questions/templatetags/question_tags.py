from django import template
from django.forms.widgets import TextInput

register = template.Library()

@register.inclusion_tag('cdh.questions/tags/display_question_tag.html')
def display_question(question, **kwargs):

    tag_context = {
        'test': 123,
        'question': question,
        'title': question.title,
        'segments': question.get_segments(),
    }

    tag_context.update(kwargs)

    return tag_context

@register.inclusion_tag('cdh.questions/tags/display_question_tag.html')
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
    if "field" in segment.context:
        field = segment.context['field'].field
        if type(field.widget) == TextInput:
            field.widget.attrs['class'] = "form-control"
    return segment.render()


@register.inclusion_tag('cdh.questions/tags/display_question_smole.html')
def display_question_small(question, **kwargs):

    tag_context = display_question_mockup(question, **kwargs)

    tag_context.update(kwargs)

    tag_context['editing'] = False

    return tag_context


@register.inclusion_tag('cdh.questions/tags/display_loq.html')
def display_loq(question, **kwargs):

    tag_context = {
        "loq": question.get_queryset(),
        "source_question": question,
        "create_url": question.get_create_url(),
    }
    tag_context.update(**kwargs)

    return tag_context
