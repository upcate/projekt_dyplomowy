from .models import Files, MainFiles

import os

from django.dispatch import receiver

from django.db.models.signals import pre_delete, pre_save


@receiver(pre_delete, sender=Files)
def auto_delete_file_on_model_delete(sender, instance, **kwargs):

    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(pre_delete, sender=MainFiles)
def auto_delete_file_on_model_delete(sender, instance, **kwargs):

    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
