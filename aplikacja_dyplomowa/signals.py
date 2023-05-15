from .models import Files

import os

from django.dispatch import receiver

from django.db.models.signals import pre_delete


@receiver(pre_delete, sender=Files)
def auto_delete_file_on_model_delete(sender, instance, **kwargs):

    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
