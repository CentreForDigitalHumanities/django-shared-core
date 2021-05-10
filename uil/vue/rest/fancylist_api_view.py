from typing import Dict, List, Any, Optional, Tuple

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class FancyListApiView(GenericAPIView):
    """Implements an API List view to use for FancyList lists.

    Spits out data in the format used by the FancyList constructor method
    """
    class SortDefinition:
        """Defines a sort option for a field

        Field should be given as a string, in the format
        {attribute}(.{subattribute})*

        (read, just like you would access an attribute of an object in Python,
        but sans the object itself and as a string).

        For example:
        "subObject.title"

        :param {str} field: the field that is sortable
        :param {str} label: The text to display in the dropdown. Direction
               arrows are added automatically
        :param {"asc"|"desc"|None} default: If not None, this direction will be
               the sort applied upon load. If multiple defs are set as default,
               the first one encountered will be used
        :param {bool} asc: whether sorting ascendingly is supported
        :param {bool} desc: whether sorting descendingly is supported
        """
        def __init__(
                self,
                field: str,
                label: str,
                asc: bool = True,
                desc: bool = True,
        ):
            self.field = field
            self.label = label
            self.asc = asc
            self.desc = desc

        def serialize(self, default: Tuple[str, str]):
            _default = None
            if default and default[0] == self.field:
                _default = default[1]

            return {
                'label': self.label,
                'asc': self.asc,
                'desc': self.desc,
                'default': _default,
            }

    class FilterDefinition:
        """Defines a filter for a field.

        Options for a filter are automatically generated by Vue

        Field should be given as a string, in the format
        {attribute}(.{subattribute})*

        (read, just like you would access an attribute of an object in Python,
        but sans the object itself and as a string).

        For example:
        "subObject.created"

        :param {str} field: the field that is sortable
        :param {str} display_name: Text that should be displayed on the button
        """
        def __init__(self, field, display_name):
            self.field = field
            self.display_name = display_name

    show_controls = True
    searchable_fields = []
    sort_definitions = []
    filter_definitions = []
    context = {}
    num_items_options = [5, 10, 25, 50]
    default_items_per_page = 10
    default_sort = None

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'items': serializer.data,
            'showControls': self.get_show_controls(),
            'context': self.get_context(),
            'searchableFields': self.get_searchable_fields(),
            'filterDefinitions': self._get_filter_definitions(),
            'numItemsOptions': self.get_num_items_options(),
            'defaultItemsPerPage': self.get_default_items_per_page(),
            'sortDefinitions': self._get_sort_definitions(),
        })

    def get_show_controls(self) -> bool:
        """If False, all controls will be hidden. (Search, sort on, items per
        page and filters)
        """
        return self.show_controls

    def get_searchable_fields(self) -> List[str]:
        """Returns a list of path strings of fields that can be searched
        through.

        If an empty list is returned, all fields are searchable
        """
        return self.searchable_fields

    def get_sort_definitions(self) -> List['SortDefinition']:
        """Returns a list of sort definitions. See SortDefinition for more info.

        If an empty list is returned, the sort box will be hidden and the
        sort of the QuerySet is used.
        """
        return self.sort_definitions

    def _get_sort_definitions(self) -> Dict[str, Dict]:
        """Serializes get_sort_definitions"""
        # Cache value, as an override of get_default_sort can be heavy
        default_sort = self.get_default_sort()
        return {x.field: x.serialize(default_sort) for x in self.get_sort_definitions()}

    def get_context(self) -> Dict[str, Any]:
        """Returns any data accessible by all items in the Vue template"""
        return self.context

    def get_num_items_options(self) -> List[int]:
        """Returns the possible items per page options"""
        return self.num_items_options

    def get_default_items_per_page(self) -> int:
        """Returns the default number of items to be displayed on a page.

        Value must be an element in num_items_options
        """
        return self.default_items_per_page

    def get_default_sort(self) -> Tuple[str, str]:
        """Return the default sort. Should be a tuple of (field, direction).
        Where direction is either 'asc' or 'desc'.
        """
        return self.default_sort

    def get_filter_definitions(self) -> List['FilterDefinition']:
        """Returns a list of filter definitions. See FilterDefinition for more
        info.

        If an empty list is returned, filters will be disabled.
        """
        return self.filter_definitions

    def _get_filter_definitions(self) -> Dict[str, str]:
        """Serializes get_filter_definitions"""
        return {x.field: x.display_name for x in self.get_filter_definitions()}

