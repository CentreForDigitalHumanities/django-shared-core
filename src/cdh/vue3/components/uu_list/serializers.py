"""A collection of serializer fields needed for the proper operation of some
columns in the Data-Defined Visualizer variant of the UU-List.
"""
from typing import List, Optional, Union

from django.shortcuts import resolve_url
from rest_framework import serializers


class DDVLinkField(serializers.Field):
    """DDVLinkField is a custom DRF serializer, which will format its
    output for use in DDVLink, DDVButton and DDVAction DDV columns.

    When using this field for DDVLink or DDVButton, you can use this class as
    the serializer.
    DDVAction columns should use the DDVActionsField serializer instead.

    Note: classes is ignored when using DDVLink; use the column classes
    argument instead
    """

    def __init__(
        self,
        *,
        text: Union[str, callable],
        link: Union[str, callable],
        link_attr: Optional[str] = None,
        new_tab: bool = False,
        check: Optional[callable] = None,
        classes: Optional[str] = None,
        **kwargs,
    ):
        """Init

        'The object' will refer to 'the object currently being serialized'.

        :param text: The text on the action. Either a (trans)string or a
                     callable, which accepts the object as a param and returns
                     a string.
        :type text: str | callable
        :param link: The link the user should be navigated to when clicking
                     the action. Either a string (both full urls as django
                     named urls are supported) or a callable returning said
                     string.
        :type link: str | callable
        :param link_attr: If supplied, the attribute given will be retrieved
                          from the object and passed to the link resolver.
                          Use this to supply things like the 'pk' to django
                          named urls.
        :type link_attr: str
        :param check: If supplied, this callable will be used to check if
                      this action should be displayed for the current object.
                      The callable should accept one parameter, the object.
        :type check: callable
        :param classes: Any CSS classes to be applied to the action root-element
        :type classes: str
        :param kwargs: see DRF Field
        """
        self.text = text
        self.link = link
        self.link_attr = link_attr
        self.new_tab = new_tab
        self.check = check
        self.classes = classes
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        if self.check is not None:
            if not self.check(value):
                return None

        args = []
        if self.link_attr is not None:
            args.append(getattr(value, self.link_attr, None))

        text = self.text
        if callable(text):
            text = text(value)

        link = resolve_url(self.link, *args)
        return {
            "link": link,
            "text": text,
            "classes": self.classes,
            "new_tab": self.new_tab,
        }


class DDVActionDividerField(serializers.Field):
    """This is a simple class to add dividers between actions in
    DDVActionsField"""

    def __init__(self, check: Optional[callable] = None, **kwargs):
        """
        'The object' will refer to 'the object currently being serialized'.

        :param check: If supplied, this callable will be used to check if
                      this action should be displayed for the current object.
                      The callable should accept one parameter, the object.
        :type check: callable
        """
        self.check = check
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        if self.check is not None:
            if not self.check(value):
                return None

        return {
            "divider": True,
        }


class DDVActionsField(serializers.Field):
    """A custom serializer to use for the DDVActions column."""

    def __init__(
        self, actions: List[Union[DDVLinkField, DDVActionDividerField]], **kwargs
    ):
        """
        :param actions: a list of items to add to the actions dropdown. If no
                        actions are defined (after checks are run), the column
                        will automagically hide itself for this object.
        :type actions: DDVLinkField | DDVActionDividerField
        :param kwargs: see DRF Field
        """
        self.actions = actions
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        for action in self.actions:
            action.bind(field_name, parent)
        super().bind(field_name, parent)

    def to_representation(self, value):
        values = []

        for action in self.actions:
            if action_representation := action.to_representation(value):
                values.append(action_representation)

        if len(values) == 0:
            return None

        return values
