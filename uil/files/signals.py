from django.apps import apps
from django.db.models.signals import pre_delete

from uil.files.db import BaseFile


def delete_file_on_delete(sender, instance, **kwargs):
    """Deletes the file on disk when the corresponding File is deleted"""
    # save=False means we will only touch the file on disk, leaving the DB
    # object alone. (That will obviously be handled by the ORM, so we don't
    # want to delete it prematurely)
    # force=True means we will ALWAYS delete the file, even if the ORM still
    # sees some references to it
    instance.get_file_wrapper().delete(save=False, force=True)


for model in apps.get_models():
    if issubclass(model, BaseFile):
        pre_delete.connect(delete_file_on_delete, sender=model)
