from django import forms
from .models import NetworkPost

class PostForm(forms.ModelForm):
    class Meta:
        model = NetworkPost
        fields = ('text',)

    def __str__(self):
        return f'{self.fields}'