from django.db.models.signals import pre_delete
from django.dispatch import receiver

from uil.files.db import File


@receiver(pre_delete, sender=File)
def delete_file_on_delete(sender, instance, **kwargs):
    """Deletes the file on disk when the corresponding File is deleted"""
    # save=False means we will only touch the file on disk, leaving the DB
    # object alone. (That will obviously be handled by the ORM, so we don't
    # want to delete it prematurely)
    # force=True means we will ALWAYS delete the file, even if the ORM still
    # sees some references to it
    instance.file_wrapper.delete(save=False, force=True)
