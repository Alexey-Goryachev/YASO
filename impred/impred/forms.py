from django import forms

from .models import Images, NetModels, Labels
from .utils import get_models, get_labels_4choice


class ImageForm(forms.ModelForm):
    imagepath = forms.ImageField(widget=forms.FileInput(attrs={'style': 'width: 100%;'}))
    listmodels = forms.ChoiceField(choices=get_models(), required=True, widget=forms.Select(attrs={'class': 'bold', 'id': 'id_models'}))

    class Meta:
        model = Images
        fields = ['listmodels', 'imagepath']


class PredictImageForm(forms.ModelForm):
    name = forms.CharField(min_length=3, max_length=30, required=True, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))
    real = forms.ChoiceField(required=True, widget=forms.Select(attrs={'id': 'id_labels', 'style': 'width: 100%;'}))

    def __init__(self, *args, **kwargs):
        super(PredictImageForm, self).__init__(*args, **kwargs)
        try:
            self.real = self.fields["real"]
            self.image = kwargs['instance']
            self.netmodel = self.image.netmodel
            self.real.choices = get_labels_4choice(self.netmodel.id)
            # print(f'>>> real.choices: {self.real.choices}')
            lab = self.image.real if self.image.real else self.image.predict.name
            self.real.widget.attrs.update({'value': lab})
            # print(f'>>> widget.attrs: {self.real.widget.attrs}')
        except:
            self.netmodel = None

    def clean_real(self):
        new_real = self.cleaned_data['real']
        if not new_real:
            raise forms.ValidationError('Real type - The field cannot be empty.')
        return new_real

    def clean_name(self):
        new_name = self.cleaned_data['name']
        if not new_name:
            raise forms.ValidationError('Name cannot be empty.')
        return new_name

    class Meta:
        model = Images
        fields = ['real', 'name']


class NetModelForm(forms.ModelForm):
    name = forms.CharField(min_length=3, max_length=30, required=True, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))
    description = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))
    modelpath = forms.FileField(widget=forms.FileInput(attrs={'style': 'width: 100%;'}))
    accuracy = forms.FloatField(min_value=0.0, max_value=1.0, required=True, widget=forms.NumberInput(attrs={'style': 'width: 100%;'}))
    categories = forms.IntegerField(min_value=1, required=True, widget=forms.NumberInput(attrs={'style': 'width: 100%;'}))
    version = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'style': 'width: 100%;'}))
    labels = forms.CharField(min_length=2, required=True, widget=forms.Textarea(attrs={'rows':3, 'cols':32, 'style': 'width: 100%;'}))

    class Meta:
        model = NetModels
        fields = ['name', 'description', 'version', 'categories', 'accuracy', 'modelpath']
        exclude = ['labels']


# class LabelForm(forms.ModelForm):
#     predict_id = forms.IntegerField(min_value=0, required=True, widget=forms.NumberInput())
#     name = forms.CharField(max_length=30, required=True, widget=forms.TextInput())
#     netmodel = NetModelForm()

#     class Meta:
#         model = Labels
#         fields = ['netmodel', 'predict_id', 'name']
