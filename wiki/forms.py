from django import forms

class NewEntry(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
