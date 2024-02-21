from django import forms

from .models import Images, NetModels, Labels

class ImageForm(forms.ModelForm):
    imagepath = forms.ImageField(widget=forms.FileInput())

    class Meta:
        model = Images
        fields = ['imagepath']


class NetModelForm(forms.ModelForm):
    name = forms.CharField(min_length=3, max_length=30, required=True, widget=forms.TextInput())
    description = forms.CharField(max_length=150, required=False, widget=forms.TextInput())
    modelpath = forms.FileField(widget=forms.FileInput())
    accuracy = forms.FloatField(min_value=0.0, max_value=1.0, required=True, widget=forms.NumberInput())
    categories = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput())
    labels = forms.CharField(min_length=2, required=True, widget=forms.Textarea(attrs={'rows':3, 'cols':32}))

    class Meta:
        model = NetModels
        fields = ['name', 'description', 'categories', 'accuracy', 'modelpath']
        exclude = ['labels']


class LabelForm(forms.ModelForm):
    predict_id = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput())
    name = forms.CharField(max_length=30, required=True, widget=forms.TextInput())
    netmodel = NetModelForm()

    class Meta:
        model = Labels
        fields = ['netmodel', 'predict_id', 'name']
