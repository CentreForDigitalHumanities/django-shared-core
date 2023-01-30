from collections import OrderedDict

from django import forms
from django.template import Context
from django.template.loader import get_template
from django.views import generic
from django.urls import reverse
from django import utils

class Question(forms.ModelForm):
    segment_template = None

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.question_data = kwargs.pop("question_data", {})
        super().__init__(*args, **kwargs)

    def _fields_to_segments(self, fields_list=None):

        if not fields_list:
            fields_list = self.Meta.fields

        segments = []
        for field in fields_list:
            segments.append(
                self._field_to_segment(field)
            )

        return segments

    def _field_to_segment(self, field):

        segment = Segment()
        segment.type = 'form_field'
        segment.field = self[field]
        if self.segment_template:
            segment.template_name = self.segment_template
        segment.context.update({
            'type': 'form_field',
            'field': self[field],
            'value': brify(self[field].value()) or "",
        })
        if hasattr(self, "instance"):
            value_display = getattr(self.instance, "get_" + field + "_display", None)
            if value_display:
                segment.context["value"] = value_display()

        return segment


def brify(s):
    if type(s) is not str:
        return s
    s = utils.html.escape(s)
    s = s.replace("\n", "<br />")
    return utils.safestring.mark_safe(s)


class DisplayQuestion():

    def __init__(self):
        pass


class Segment:

    default_template_name = 'cdh.questions/tags/question_segments.html'
    template_name = None

    def __init__(self, **kwargs):

        # This context gets changed to a Context object later
        self.context = {'segment': self}
        self.context.update(**kwargs)

    def get_template(self):
        if not self.template_name:
            self.template_name = self.default_template_name
        self.template = get_template(self.template_name)
        return self.template

    def render(self):
        template = self.get_template()
        return template.render(self.context)


class BlueprintQuestion(Question):
    """Question class that accepts a blueprint keyword argument"""

    def __init__(self, *args, **kwargs):
        self.blueprint = kwargs.pop("blueprint", None)
        return super().__init__(*args, **kwargs)


class SubheaderSegment(Segment):

    type = 'subheader'
