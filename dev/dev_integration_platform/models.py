from django.contrib.auth import get_user_model
from django.db import models


class Record(models.Model):

    main_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    users = models.ManyToManyField(
        get_user_model(),
        related_name='+',
    )
