from django import forms

from .models import Images

class ImageForm(forms.ModelForm):
    imagepath = forms.ImageField(widget=forms.FileInput())

    class Meta:
        model = Images
        fields = ['imagepath']
