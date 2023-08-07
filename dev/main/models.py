from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.safestring import mark_safe

from cdh.core.fields import MaxYearValidator, MinYearValidator, MonthField


class User(AbstractUser):
    pass


class MonthFieldTest(models.Model):

    split_month_field = MonthField(
        null=True,
        blank=True,
    )
    single_month_field = MonthField(
        validators=[
            MinYearValidator(2000),
            MaxYearValidator(2038),
        ],
        null=True,
        blank=True,
    )

    def __str__(self):
        return mark_safe(
            f"split: {self.split_month_field}<br/>single:{self.single_month_field}"
        )
