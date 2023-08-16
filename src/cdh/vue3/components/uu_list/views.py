from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language
from django.views import generic
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from .paginator import StandardResultsSetPagination


class UUListAPIView(generics.ListAPIView):
    """This is the API view, used by UU-List to retrieve its data

    This class can be used by both the default DDV UU-List, and a custom UU-List
    implementation.
    """

    # These filter backends determine what functionality is available
    # The DDVListView and UUListView classes will automagically enable the
    # frontend features depending on what filter types are enabled.
    # There three are the only ones supported, but any (or all) may be omitted
    # Note: there are two similarly named mechanisms at play here; In the docs
    # we mostly use 'filters' to refer to django-filters; but this var refers
    # to DRF's filter system. (And we enable django-filters here)
    # OrderingFilter: enables sorting support
    # SearchFilter: Enables the search bar
    # filters.DjangoFilterBackend: enables advanced filters using django-filters
    filter_backends = [OrderingFilter, SearchFilter, filters.DjangoFilterBackend]
    # The Django-filters filterset class to use. Can be left None if
    # django-filters is not enabled
    filterset_class = None
    # The fields on the QS that can be used to sort
    # Labels will be taken from the fields verbose_name, unless overriden in
    # UUListView/DDVListView
    ordering = ["id"]
    # Leave this alone unless you know what to do with it
    # This overrides to pagination class to one that produces the format
    # expected by UU-List
    pagination_class = StandardResultsSetPagination

    def get_paginated_response(self, data):
        data = super().get_paginated_response(data)
        data["ordering"] = self.ordering

        return Response(data)


class UUListView(generic.TemplateView):
    """A base class for _custom_ UU-List pages.

    This custom view generates the initial configuration used by all UU-List
    implementations.

    Your template can then initiate the component in the template using:
    {% vue UUList :config=uu_list_config %}

    Is extended by DDVListView, thus the variables here also apply to that
    class.

    This class has multiple methods that may be overriden to modify the
    automagical config generation.
    """

    # Page size options, should contain 25
    page_size_options = [10, 25, 50, 100]
    # The model viewed, should be exactly the same one as used in
    # UUListApiView's serializer
    # May also be set by overriding the get_model method
    model = None
    # The URL of the UUListApiView to retrieve actual data from
    # Note: you should use reverse_lazy!
    # May also be set by overriding the get_data_uri method
    data_uri = None
    # Should be a direct reference to the class that handles the url
    # set in `data_uri`. This is used to probe what capabilities that
    # class has enabled
    data_view = None
    # The name of the template context variable used to store the initial config
    # If you change this, make sure to modify your template accordingly
    context_config_var = "uu_list_config"
    # Determines the visual layout used; default is the newer design.
    # Alternatively, use 'sidebar' to use a UU-Sidebar based design.
    # Note: sidebar only makes sense if the django-filters backend and/or search
    # is enabled.
    container = "default"
    # This will set the initial value for any filter. Key should be the 'field'
    # name.
    # Multiple-choice filters need the value to be in list-form, others a plain
    # value
    # Single-choice filters without a defined initial value will use the
    # first option available.
    initial_filter_values = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.get_model() is None:
            raise ImproperlyConfigured(
                "UUListView classes must define the (root) model as "
                "<class>.model or override <class>.get_model()"
            )
        if self.get_data_uri() is None:
            raise ImproperlyConfigured(
                "UUListView classes must define the uri of the API view as "
                "<class>.data_uri. (Preferably using reverse_lazy) "
                "Alternatively, override <class>.get_data_uri()."
            )
        if self.get_data_view() is None:
            raise ImproperlyConfigured(
                "UUListView classes must define the used API view as "
                "<class>.data_view. "
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context[self.context_config_var] = {
            "dataUri": self.get_data_uri(),
            "filtersEnabled": self.get_filters_enabled(),
            "filters": self.get_filters(),
            "pageSize": self.get_page_size(),
            "pageSizeOptions": self.get_page_size_options(),
            "sortEnabled": self.get_sort_enabled(),
            "sortOptions": self.get_sort_options(),
            "searchEnabled": self.get_search_enabled(),
            "locale": self.get_locale(),
            "container": self.get_container(),
        }

        return context

    def get_locale(self):
        """Modify this method to return 'en'|'nl' if your app does not use
        those labels for the languages. (In other words, if your app uses
        'en-US' instead of 'en', etc).
        """
        return get_language()

    def get_model(self):
        return self.model

    def get_data_view(self):
        return self.data_view

    def get_data_uri(self):
        # Cast to string, as it's probably a lazy value and the vue tag
        # DOES NOT like lazy values.... Ugh
        return str(self.data_uri)

    def get_page_size(self):
        return self.get_data_view().pagination_class.page_size

    def get_page_size_options(self):
        return self.page_size_options

    def get_search_enabled(self):
        return SearchFilter in self.get_data_view().filter_backends

    def get_sort_enabled(self):
        return OrderingFilter in self.get_data_view().filter_backends

    def get_filters_enabled(self):
        return filters.DjangoFilterBackend in self.get_data_view().filter_backends

    def get_initial_filter_values(self):
        return self.initial_filter_values

    def get_filters(self):
        if not self.get_filters_enabled():
            return []

        from django_filters.rest_framework import (
            ChoiceFilter,
            MultipleChoiceFilter,
            DateFilter,
        )

        initial_filter_values = self.get_initial_filter_values()

        filter_map = {
            ChoiceFilter: "radio",
            MultipleChoiceFilter: "checkbox",
            DateFilter: "date",
        }
        filter_defs = []
        dataview_filters = self.get_data_view().filterset_class.get_filters().items()
        for field, filter_object in dataview_filters:
            if type(filter_object) not in filter_map:
                continue

            filter_def = {
                "field": field,
                "label": filter_object.label,
                "type": filter_map.get(type(filter_object)),
            }

            if filter_def["type"] in ["checkbox", "radio"]:
                filter_def["options"] = filter_object.extra["choices"]

            if field in initial_filter_values:
                filter_def["initial"] = initial_filter_values[field]

            filter_defs.append(filter_def)

        return filter_defs

    def get_sort_options(self):
        """Override this method if you want to customize the labels used for
        the sorting options.
        """
        if not self.get_sort_enabled():
            return []

        def get_field_name(field):
            return self.get_model()._meta.get_field(field).verbose_name

        options = []

        for field in self.get_data_view().ordering_fields:
            options.append({"field": field, "label": f"{get_field_name(field)} ↑"})
            options.append(
                {"field": f"-{field}", "label": f"{get_field_name(field)} ↓"}
            )

        return options

    def get_container(self):
        return self.container


class DDVListView(UUListView):
    """Extension of UUListView which will also add DDV configuration.

    The DDV, or Data-Defined Visualizer variant of UU-List is the default
    UU-List implementation of DSC, and allows for fully-backend defined usage
    of UU-List. (Read: no custom JS required).

    It uses a preset defined list of 'columns' to build a table. The order
    of 'self.columns' will also be the order of the columns in the table.

    See ./columns.py for information on what columns are available.

    Some columns need a custom serializer field to be used, which is documented
    on the relevant column classes.
    """

    columns = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.get_columns() is None:
            raise ImproperlyConfigured(
                "UUListView classes must define columns as "
                "<class>.columns or override <class>.get_columns"
            )

    def get_columns(self):
        return self.columns

    def get_columns_config(self):
        return [column.get_config() for column in self.get_columns()]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context[self.context_config_var]["columns"] = self.get_columns_config()

        return context
