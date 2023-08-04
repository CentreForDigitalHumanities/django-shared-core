from datetime import date, datetime

from django.conf import settings
from django.core import exceptions
from django.core.validators import BaseValidator
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from cdh.core.forms import BootstrapMonthField


@deconstructible
class MaxYearValidator(BaseValidator):
    message = _("Ensure the year is less than or equal to %(limit_value)s.")
    code = "max_value"

    def compare(self, a, b):
        return a > date(b, 12, 31)


@deconstructible
class MinYearValidator(BaseValidator):
    message = _("Ensure the year is greater than or equal to %(limit_value)s.")
    code = "min_value"

    def compare(self, a, b):
        return a < date(b, 1, 1)


class Month(date):
    """A custom date object that omits 'day' as a used param"""
    def __new__(cls, year: int, month: int):
        # We enforce that Month day objects always use '1' as the day of the
        # month
        return super().__new__(cls, year, month, 1)

    @classmethod
    def from_string(cls, string: str):
        year = int(string[:4])
        month = int(string[5:7])
        return cls(year, month)

    @classmethod
    def from_date(cls, date: date):
        return cls(date.year, date.month)

    def __str__(self):
        return self.strftime("%B %Y")


class MonthField(models.DateField):
    description = "A month of a year."

    default_error_messages = {
        'invalid_year': _("Year informed invalid. Enter at least 4 digits."),
    }
    
    def __init__(
            self,
            verbose_name=None,
            name=None,
            auto_now=False,
            auto_now_add=False,
            **kwargs
    ):
        super().__init__(
            verbose_name=verbose_name,
            name=name,
            auto_now=auto_now,
            auto_now_add=auto_now_add,
            **kwargs
        )

        self.year_min, self.year_max = None, None

        for validator in self.validators:
            if isinstance(validator, MinYearValidator):
                self.year_min = validator.limit_value
            if isinstance(validator, MaxYearValidator):
                self.year_max = validator.limit_value

    def get_internal_type(self):
        return "DateField"

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, datetime):
            if settings.USE_TZ and timezone.is_aware(value):
                default_timezone = timezone.get_default_timezone()
                value = timezone.make_naive(value, default_timezone)
            value = value.date()

        if isinstance(value, Month):
            month = value
        elif isinstance(value, date):
            month = Month.from_date(value)
            if len(str(month.year)) < 4:
                raise exceptions.ValidationError(
                    self.error_messages['invalid_year'],
                    code='invalid_year',
                    params={'value': value},
                )
        elif isinstance(value, str):
            month = Month.from_string(value)
        else:
            raise exceptions.ValidationError(
                self.error_messages['invalid_date'],
                code='invalid_date',
                params={
                    'value': value
                },
            )
        return month

    def get_db_prep_value(self, value, connection, prepared=False):
        """Converts the python value to a format the DB backend can
        understand.
        Overriden because, while the backend can deal with date objects,
        it's very very very stupid and cannot deal with our custom date object.
        """
        if not prepared:
            value = self.get_prep_value(value)
        if value is not None:
            # Set day to one to enforce the 'day should be 1' rule, if someone
            # were to go out of their way to ignore that rule when using Month
            value = date(value.year, value.month, 1)
        return connection.ops.adapt_datefield_value(value)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': BootstrapMonthField,
        }
        if self.year_min:
            defaults['year_min'] = self.year_min
        if self.year_max:
            defaults['year_max'] = self.year_max

        defaults.update(kwargs)
        return super(MonthField, self).formfield(**defaults)
