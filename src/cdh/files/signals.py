from django.apps import apps
from django.db.models.signals import pre_delete, post_delete

from cdh.files.db import BaseFile

import logging
logger = logging.getLogger(__name__)


def delete_file_on_delete(sender, instance, **kwargs):
    """Deletes the file on disk when the corresponding File is deleted"""
    # save=False means we will only touch the file on disk, leaving the DB
    # object alone. (That will obviously be handled by the ORM, so we don't
    # want to delete it prematurely)
    logger.debug(f"Signals: pre_delete called for {sender.__name__}; deleting file for {instance}")
    instance.get_file_wrapper().delete(save=False)


for model in apps.get_models():
    if issubclass(model, BaseFile):
        post_delete.connect(delete_file_on_delete, sender=model)
