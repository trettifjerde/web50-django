import os
from io import BytesIO
from PIL import Image
from datetime import datetime
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models

DEFAULT_IMAGE = "network/default.png"

class Networker(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", symmetrical=False, related_name='followers', blank=True)
    image = models.ImageField(upload_to="network/", default=DEFAULT_IMAGE)

    def __str__(self):
        return f'{self.user.username}'

    def save_image(self, bytesio):

        img = Image.open(bytesio)
        img.thumbnail((300, 300))
        img_file = BytesIO()
        img.save(img_file, img.format)

        img_name = f'{datetime.now().timestamp()}.{img.format}'

        if (self.image.name != DEFAULT_IMAGE):
            os.remove(self.image.path)

        self.image.save(img_name, img_file)

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
    edited = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Networker)

    def __str__(self):
        return f"{self.networker}: {self.text if len(self.text) < 15 else self.text[:15] + '...'} ( 0 likes)"

    def is_edited(self):
        return self.created != self.edited

    def serialize(self, for_networker):
        return {
            'id': self.id,
            'networker': str(self.networker),
            'networkerId': self.networker.user.id,
            'text': self.text,
            'likes': self.likes.count(),
            'created': self.created.strftime("%d/%m/%y %H:%M"),
            'edited': self.edited.strftime("%d/%m/%y %H:%M"),
            'liked': for_networker in self.likes.all(),
            'avatar': self.networker.image.url,
            'self': for_networker == self.networker,
        }


