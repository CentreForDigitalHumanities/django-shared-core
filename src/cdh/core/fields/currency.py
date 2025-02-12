from django.db import models
from django import forms

from cdh.core.forms import BootstrapCurrencyField

class CurrencyField(models.CharField):

    def formfield(self, **kwargs):
        defaults = {
            "form_class": BootstrapCurrencyField,
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)

