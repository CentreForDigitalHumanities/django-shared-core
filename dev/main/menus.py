from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

Menu.add_item("home", MenuItem(_('main:menu:home'),
                               reverse('main:home'),
                               exact_url=True
                               ))

Menu.add_item("main", MenuItem(_('main:menu:core'),
                               "#",
                               exact_url=True,
                               children=[
                                   MenuItem(
                                       _('main:menu:core:base'),
                                       reverse('main:styles'),
                                       exact_url=True,
                                   ),
                                   MenuItem(
                                       _('main:menu:core:form'),
                                       reverse('main:styles_form'),
                                       exact_url=True,
                                   ),
                                   MenuItem(
                                       _('main:menu:core:custom_form'),
                                       reverse('main:custom_styles_form'),
                                       exact_url=True,
                                   ),
                                   MenuItem(
                                       _('main:menu:core:jquery_form'),
                                       reverse('main:styles_form_jquery'),
                                       exact_url=True,
                                   ),
                                   MenuItem(
                                       _('main:menu:core:custom_email_form'),
                                       reverse('main:custom_email_form'),
                                       exact_url=True,
                                   ),
                                   MenuItem(
                                       _('main:menu:core:month_field'),
                                       reverse('main:month_field_test'),
                                       exact_url=True,
                                   ),
                               ]
                               ))

Menu.add_item("footer", MenuItem(_('main:footer:login'),
                                 reverse('main:login'),
                                 check=lambda x: not x.user.is_authenticated
                                 ))

Menu.add_item("footer", MenuItem(_('main:footer:logout'),
                                 reverse('main:logout'),
                                 check=lambda x: x.user.is_authenticated
                                 ))
