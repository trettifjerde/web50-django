from django.contrib.auth.models import User
from django.db import models

class Networker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", symmetrical=False, related_name='followers')

    def __str__(self):
        return f'{self.user.username}'

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
            'likes': self.likes.objects.count(),
            'created': self.created.strftime("%d/%m/%y %H:%M"),
            'edited': self.edited.strftime("%d/%m/%y %H:%M")
        }


