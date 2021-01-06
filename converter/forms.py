from django import forms
from .models import Converter


class MessageForm(forms.Form):
    post = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    