from django import forms
from commerce.models import Listing, Comment, Category

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = '__all__'

    starting_bid = forms.FloatField(required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        labels = {'text': 'Your comment'}