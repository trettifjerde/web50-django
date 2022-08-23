import os
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from PIL import Image

DEFAULT_IMAGE = "network/default.png"

class Networker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", symmetrical=False, related_name='followers', blank=True)
    image = models.ImageField(upload_to="network/", default=DEFAULT_IMAGE)

    def __str__(self):
        return f'{self.user.username}'

    def save_image(self, img_file):
        img_name = f'{self.user.username}.png'

        if self.image.name == DEFAULT_IMAGE:
            self.image.save(img_name, img_file)

            img = Image.open(img_file)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.image.path)

        else:
            img = Image.open(img_file)
            img.thumbnail((300, 300))
            img.save(self.image.path)

    def delete_image(self):
        if self.image.name != DEFAULT_IMAGE:
            os.remove(self.image.path)
        self.image.delete()
        self.image.name = DEFAULT_IMAGE
        self.save()
    
    def is_default_image(self):
        return self.image.name == DEFAULT_IMAGE


class NetworkPost(models.Model):
    class Meta: 
        ordering = ['-created']
    networker = models.ForeignKey(Networker, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(Networker)

    def __str__(self):
        return f"{self.networker}: {self.text if len(self.text) < 15 else self.text[:15] + '...'} ( 0 likes)"

    def is_edited(self):
        return self.created != self.edited

    def serialize(self):
        return {
            'id': self.id,
            'networker': str(self.networker),
            'text': self.text,
            'likes': self.likes.count(),
            'created': self.created.strftime("%d/%m/%y %H:%M"),
            'edited': self.edited.strftime("%d/%m/%y %H:%M")
        }


