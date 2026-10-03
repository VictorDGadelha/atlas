from django import forms
from .models import RegistroPeso


class RegistroPesoForm(forms.ModelForm):
    class Meta:
        model = RegistroPeso
        fields = ['data', 'peso']
        widgets = {
            'data': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d',
            ),
            'peso': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Ex.: 72.5'}
            ),
        }

    def clean_peso(self):
        peso = self.cleaned_data['peso']
        if peso < 20 or peso > 500:
            raise forms.ValidationError('Informe um peso válido em kg.')
        return peso