from django.db import models
from django.shortcuts import reverse 

class Project(models.Model):
    name = models.CharField(max_length=20)
    short_description = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    frontend = models.CharField(max_length=200, blank=True)
    backend = models.CharField(max_length=200, blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse(f'{self.name}:index')

class Pic(models.Model):
    desktop = models.ImageField(blank=True, upload_to='home/')
    mobile = models.ImageField(blank=True, upload_to='home/')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="pics")

    def __str__(self):
        return f'Picture #{self.id} for {self.project.name}'