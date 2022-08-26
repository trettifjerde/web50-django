import os
from PIL import Image
from django import forms
from commerce.models import Listing, Comment, Category, LISTING_STORAGE
from web50.settings import MEDIA_ROOT

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        labels = {'text': 'Your comment'}