from django.db import models
from django.db.models import Q
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _


class SystemMessageManager(models.Manager):

    def get_current_messages(self):
        """Returns a QS prefiltered to honor the not_before and not_after
        fields"""
        qs = self.get_queryset()

        qs = qs.filter(Q(not_before=None) | Q(not_before__lt=Now()))
        qs = qs.filter(Q(not_after=None) | Q(not_after__gt=Now()))

        return qs


class SystemMessage(models.Model):

    objects = SystemMessageManager()

    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"

    COLORS = (
        (PRIMARY, _('systemmessage.color.primary')),
        (SECONDARY, _('systemmessage.color.secondary')),
        (SUCCESS, _('systemmessage.color.success')),
        (DANGER, _('systemmessage.color.danger')),
        (WARNING, _('systemmessage.color.warning')),
        (INFO, _('systemmessage.color.info')),
        (LIGHT, _('systemmessage.color.light')),
        (DARK, _('systemmessage.color.dark')),
    )

    message = models.TextField(
        _('systemmessage.message'),
        help_text=_('systemmessage.message.help_text'),
    )
    color = models.CharField(
        _('systemmessage.color'),
        help_text=_('systemmessage.color.help_text'),
        max_length=15,
        choices=COLORS,
    )
    not_before = models.DateTimeField(
        _('systemmessage.not_before'),
        help_text=_('systemmessage.not_before.help_text'),
        null=True,
        blank=True,
    )
    not_after = models.DateTimeField(
        _('systemmessage.not_after'),
        help_text=_('systemmessage.not_after.help_text'),
        null=True,
        blank=True,
    )

    @property
    def css_class(self):
        return f"alert alert-{self.color}"
