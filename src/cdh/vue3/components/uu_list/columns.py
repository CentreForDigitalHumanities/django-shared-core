"""A collection of column definition classes used by the Data-Defined
Visualizer variant of the UU-List.
"""
from typing import Optional, Union

from django.utils.translation import get_language


class _DDVColumn:
    """Base class for all DDV columns, should not be used directly"""

    type: str = None

    def __init__(self, field: str, label: str, css_classes: Optional[str] = None):
        """
        :param field: The key of the field used in the serializer to pull
                      data from.If you are unsure, view the output of your
                      API view and copy the key.
        :param label: The text shown as the table header for this column
        :param css_classes: Any CSS classes to add to the item in the table cell
        """
        self.field = field
        self.label = label
        self.classes = css_classes

    def get_config(self):
        return {
            "type": self.type,
            "field": self.field,
            "label": self.label,
            "classes": self.classes,
        }


class DDVString(_DDVColumn):
    """Will simply display the contents of the given field as a string.

    Note: HTML will be escaped! If you really want HTML, use DDVHtml.
    Or, you know, use a custom UU-List implementation.
    """

    type = "string"


class DDVHtml(_DDVColumn):
    """Will display the contents of the given field without escaping HTML

    NOTE: THIS IS POTENTIALLY UNSAFE! ALWAYS SANITIZE USER INPUT YOURSELF
    Note 2: If you end up using this column a lot, it's probably better to
    create a custom UU-List implementation over using the default DDV
    implementation.
    """

    type = "html"


class DDVDate(_DDVColumn):
    """Will format a ISO 8601 formatted date(time) into a localized date(time).

    Use DRF's Date(Time)Field in your serializer. (THis will be automatically
    be the case if you use a ModelSerializer with the `fields` option)
    """

    type = "date"

    def __init__(
        self,
        field: str,
        label: str,
        css_classes: Optional[str] = None,
        format: Optional[Union[str, dict]] = None,
        # Default to NL, even for EN languages to be consistent in format
        language: Optional[str] = "nl",
    ):
        super().__init__(field, label, css_classes)
        self.format = format
        self.language = language

    def get_config(self):
        config = super().get_config()
        config["format"] = self.format

        # if locale is none, retrieve the current activated language
        language = self.language or get_language()

        config["language"] = language
        return config


class DDVLink(_DDVColumn):
    """Will display a simple link in the table.

    Use DDVLinkField in your serializer to populate the field that will be used

    Note: this will display only a link. If you need a link inside a larger
    text, use DDVHtml or create a custom UU-List implementation
    """

    type = "link"


class DDVActions(_DDVColumn):
    """Will display a list of actions inside a dropdown

    Use DDVActionsField in your serializer to populate the field that will be used
    """

    type = "actions"


class DDVButton(_DDVColumn):
    """Will display a button in the table.

    Use DDVLinkField in your serializer to populate the field that will be used
    """

    type = "button"

    def __init__(
        self,
        field: str,
        label: str,
        variant: Optional[str] = None,
        size: Optional[str] = None,
    ):
        """

        :param field: The key of the field used in the serializer to pull
                      data from.If you are unsure, view the output of your
                      API view and copy the key.
        :param label: The text shown as the table header for this column
        :param variant: The BS button variant to use. See UU-Bootstrap for
                        info on the options. Defaults to 'primary'.
        :param size: small, normal or large. Defaults to 'normal'
        """
        super().__init__(field, label)
        self.variant = variant
        self.size = size

    def get_config(self):
        config = {
            "type": self.type,
            "field": self.field,
            "label": self.label,
        }
        if self.variant:
            config["variant"] = self.variant
        if self.size:
            config["size"] = self.size

        return config
