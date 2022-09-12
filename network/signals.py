from django.db.models.signals import pre_save
from django.dispatch import receiver 
from network.models import NetworkPost
from datetime import datetime

@receiver(pre_save, sender=NetworkPost)
def edit_post(sender, instance, **kwargs):
    if instance.pk:
        post = NetworkPost.objects.get(pk=instance.pk)
        if post.text != instance.text:
            instance.edited = datetime.now()