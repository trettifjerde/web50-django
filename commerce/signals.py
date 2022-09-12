import os
from django.db.models.signals import pre_save
from django.dispatch import receiver 
from commerce.models import Listing


@receiver(pre_save, sender=Listing)
def get_image(sender, instance, **kwargs):
    if instance.pk:
        old_image = Listing.objects.get(pk=instance.pk).image

        if instance.image.name == old_image.name:
            return

        if old_image.name:
            os.remove(old_image.path)

    if instance.image.name:
        instance.prep_image()
