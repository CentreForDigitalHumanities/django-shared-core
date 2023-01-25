from django import template
from django.apps import apps
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def get_verbose_field_name(app_label, model_name, field_name, value=None):
    """
    Returns verbose_name for a field.
    """
    verbose_name = apps.get_model(app_label, model_name)._meta.get_field(field_name).verbose_name
    if value is not None:
        verbose_name %= value
    return mark_safe(verbose_name)


@register.simple_tag
def get_field_name(app_label, model_name, field_name, value=None):
    """
    Returns name for a field.
    """
    verbose_name = apps.get_model(app_label, model_name)._meta.get_field(field_name).name
    if value is not None:
        verbose_name %= value
    return mark_safe(verbose_name)
