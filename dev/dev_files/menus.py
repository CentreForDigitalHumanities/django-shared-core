from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

sub_menus = []

sub_menus.append(
    MenuItem(
        'Single file list',
        reverse('dev_files:single_list'),
        exact_url=True,
    )
)

sub_menus.append(
    MenuItem(
        'Custom single file list',
        reverse('dev_files:customsingle_list'),
        exact_url=True,
    )
)

Menu.add_item("main", MenuItem('Files',
                               '#',
                               exact_url=True,
                               children=sub_menus,
))
