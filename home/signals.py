from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver 
from commerce.models import Merchant
from network.models import Networker

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Merchant.objects.create(user=instance)
        Networker.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.merchant.save()
    instance.networker.save()