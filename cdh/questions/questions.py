from collections import OrderedDict

from django import forms
from django.template import Context
from django.template.loader import get_template
from django.views import generic
from django.urls import reverse




class Question(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.segments = self.get_segments()

    def _fields_to_segments(self, fields_list=None):

        if not fields_list:
            fields_list = self.fields

        segments = []
        for field in self.fields:
            segments.append(
                self._field_to_segment(field)
            )

        return segments

    def _field_to_segment(self, field):

        segment = Segment()
        segment.type = 'form_field'
        segment.field = self[field]
        segment.context.update({
            'type': 'form_field',
            'field': self[field],
            })

        return segment

class EditableQuestion(forms.Form, Question):

    "Makes a Question editable as a Django form"

class DisplayQuestion():

    def __init__(self):
        pass


class Segment:

    def __init__(self, **kwargs):

        if hasattr(self, 'template_name'):
            self.template = get_template(self.template_name)
        else:
            self.template = get_template('cdh.questions/tags/question_segments.html')

        # This context gets changed to a Context object later
        self.context = {'segment': self}
        self.context.update(**kwargs)

    def render(self):

        return self.template.render(self.context)


class SubheaderSegment(Segment):

    type = 'subheader'
