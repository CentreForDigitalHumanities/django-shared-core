from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem


Menu.add_item("main", MenuItem('Integration Platform',
                               reverse('dev_integration_platform:home'),
                               exact_url=True,
))
