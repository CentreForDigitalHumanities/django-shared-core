from django.urls import reverse
from menu import Menu, MenuItem


sub_menus = []

sub_menus.append(
    MenuItem(
        "UU-List",
        reverse("dev_vue:list"),
        exact_url=True,
    )
)

sub_menus.append(
    MenuItem(
        "Example custom UU-List",
        reverse("dev_vue:custom-list"),
        exact_url=True,
    )
)

Menu.add_item(
    "main",
    MenuItem(
        "Vue",
        "#",
        exact_url=True,
        children=sub_menus,
    ),
)
