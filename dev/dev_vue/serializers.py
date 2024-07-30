from cdh.vue3.components.uu_list import (
    DDVActionDividerField,
    DDVLinkField,
    DDVActionsField,
)
from cdh.rest.server.serializers import ModelDisplaySerializer
from dev_vue.models import ExampleData


class ExampleDataSerializer(ModelDisplaySerializer):
    """This is the demo/test serializer for UU-List"""

    edit_button = DDVLinkField(
        text="Edit",
        link="dev_vue:dummy",
        link_attr="pk",
        check=lambda o: o.status == ExampleData.StatusOptions.OPEN,
    )
    actions = DDVActionsField(
        [
            DDVLinkField(
                text="Edit",
                link="dev_vue:dummy",
                link_attr="pk",
                check=lambda o: o.status == ExampleData.StatusOptions.OPEN,
            ),
            DDVLinkField(
                text="Review",
                link="dev_vue:list",
                check=lambda o: o.status == ExampleData.StatusOptions.IN_REVIEW,
            ),
            DDVLinkField(
                text="Assign",
                link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                new_tab=True,
                check=lambda o: o.status == ExampleData.StatusOptions.IN_REVIEW,
            ),
            DDVLinkField(
                text="Print",
                link="dev_vue:list",
            ),
            DDVActionDividerField(
                check=lambda o: o.status == ExampleData.StatusOptions.OPEN,
            ),
            DDVLinkField(
                text="Delete",
                link="dev_vue:list",
                classes="text-danger fw-bold",
                check=lambda o: o.status == ExampleData.StatusOptions.OPEN,
            ),
        ]
    )

    class Meta:
        model = ExampleData
        fields = "__all__"
