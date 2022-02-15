from django.db import models

from cdh.files.db import fields, BaseFile


# Create your models here.
class SingleFile(models.Model):

    nullable_file = fields.FileField(
        null=True,
        blank=True,
        url_pattern='dev_files:file_view',
    )

    required_file = fields.FileField(
        url_pattern='dev_files:field_limited_file_view',
    )


class CustomFile(BaseFile):
    pass


class CustomSingleFile(models.Model):

    nullable_file = fields.FileField(
        to=CustomFile,
        null=True,
        blank=True,
        url_pattern='dev_files:custom_file_view',
    )

    required_file = fields.FileField(
        to=CustomFile,
        url_pattern='dev_files:custom_file_view',
    )


class TrackedFile(models.Model):

    files = fields.TrackedFileField(
        url_pattern='dev_files:field_limited_tracked_file_view',
    )


class TrackedCustomFile(models.Model):

    files = fields.TrackedFileField(
        to=CustomFile,
        url_pattern='dev_files:custom_file_view',
    )
