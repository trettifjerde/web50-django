from django import forms
from commerce.models import Listing, Comment, Category

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']

    starting_bid = forms.IntegerField(min_value=0, max_value=9999999)
        
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your comment'}), label='')