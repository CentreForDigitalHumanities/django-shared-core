from datetime import datetime

from django.db import models


class ExampleData(models.Model):
    class StatusOptions(models.TextChoices):
        OPEN = "O", "Open"
        IN_REVIEW = "R", "In review"
        CONCLUDED = "C", "Concluded"

    class TypeOptions(models.TextChoices):
        STANDARD = "S", "Standard"
        EXTERNAL = "E", "External"
        TOP_SECRET = "TS", "Top secret"
        # This is a reference to the movie 'The number 23'. Can highly
        # recommend that movie... if you are less than sober
        TOPSY_KRETTS = "TK", "Topsy Kretts"

    project_name = models.TextField()

    project_owner = models.TextField()

    reference_number = models.TextField()

    status = models.CharField(
        choices=StatusOptions.choices,
        default=StatusOptions.OPEN,
        max_length=2,
    )

    project_type = models.CharField(
        choices=TypeOptions.choices,
        default=TypeOptions.STANDARD,
        max_length=2,
    )

    created = models.DateTimeField(default=datetime.now)
