from django.db import models

from uil.files.db import fields, BaseFile


# Create your models here.
class SingleFile(models.Model):

    nullable_file = fields.FileField(
        null=True,
        blank=True
    )

    required_file = fields.FileField()


class CustomFile(BaseFile):
    pass


class CustomSingleFile(models.Model):

    nullable_file = fields.FileField(
        to=CustomFile,
        null=True,
        blank=True
    )

    required_file = fields.FileField(
        to=CustomFile,
    )


class TrackedFile(models.Model):

    files = fields.TrackedFileField()


class TrackedCustomFile(models.Model):

    files = fields.TrackedFileField(
        to=CustomFile,
    )
