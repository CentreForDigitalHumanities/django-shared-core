import time

from django.urls import reverse_lazy
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter

from cdh.vue3.components.uu_list import (
    DDVActions,
    DDVButton,
    DDVDate,
    DDVString,
    DDVListView,
    UUListAPIView,
)

from .models import ExampleData
from .serializers import ExampleDataSerializer

#
# DDV UU-List example
# This contains all Python code needed for the DDV UU-List,
# except the serializer 'ExampleDataSerializer' imported above
#


class ExampleDataFilterSet(filters.FilterSet):
    """This is a Django-filters filterset.

    This class is used to create GET-parameter based filter fields, which
    will be read by the API view to enable advanced filtering. You don't need
    to do anything special related to filters aside from this class.

    These filters will be transformed to QS filters under the hood.
    If a filter was not set in the request, the filter will be no-op

    See Django-filters docs for detailed docs.
    """

    # This is a filter acting on the created field of ExampleData
    # The resulting QS filter would be 'created__lte={value}'
    created_before = filters.DateFilter(
        label="Created before",
        field_name="created",
        lookup_expr="lte",
    )
    # This is a filter acting on the created field of ExampleData
    # The resulting QS filter would be 'created__gte={value}'
    created_after = filters.DateFilter(
        label="Created after",
        field_name="created",
        lookup_expr="gte",
    )

    # Will filter the status filter on a set of N given choices
    # The resulting QS filter would be `status__in=[...]`
    status = filters.MultipleChoiceFilter(
        label="Status",
        field_name="status",
        choices=ExampleData.StatusOptions.choices,
    )

    # Will filter the status filter on a given choice
    # The resulting QS filter would be `project_type={value}`
    project_type = filters.ChoiceFilter(
        label="Type",
        field_name="project_type",
        choices=ExampleData.TypeOptions.choices,
    )

    class Meta:
        model = ExampleData
        fields = ["status", "project_type"]


class ExampleDataListView(UUListAPIView):
    """
    See the base class(es) for information on what these fields are
    """

    queryset = ExampleData.objects.all()
    serializer_class = ExampleDataSerializer
    filter_backends = [OrderingFilter, SearchFilter, filters.DjangoFilterBackend]
    filterset_class = ExampleDataFilterSet
    search_fields = ["project_name", "project_owner", "reference_number"]
    ordering_fields = [
        "id",
        "reference_number",
        "project_name",
        "project_owner",
        "created",
    ]
    ordering = ["project_name"]


class ListView(DDVListView):
    template_name = "dev_vue/list.html"
    model = ExampleData
    data_uri = reverse_lazy("dev_vue:data")
    data_view = ExampleDataListView
    initial_filter_values = {"project_type": ExampleData.TypeOptions.EXTERNAL}
    columns = [
        DDVString(
            field="project_name",
            label="Project",
        ),
        DDVString(
            field="reference_number",
            label="Ref.Num",
            css_classes="fw-bold text-danger",
        ),
        DDVString(
            field="project_owner",
            label="Project Owner",
        ),
        DDVString(
            field="get_status_display",
            label="Status",
        ),
        DDVDate(
            field="created",
            label="Created on",
        ),
        DDVButton(
            field="edit_button",
            label="",
            size="small",
        ),
        DDVActions(
            field="actions",
            label="",
        ),
    ]


class ExampleCustomListView(ListView):
    template_name = "dev_vue/example-custom-list.html"
