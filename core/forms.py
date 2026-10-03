from django import forms
from .models import RegistroPeso, Refeicao


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

class RefeicaoForm(forms.ModelForm):
    class Meta:
        model = Refeicao
        fields = ['data', 'tipo', 'descricao', 'calorias']
        widgets = {
            'data': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d',
            ),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ex.: arroz, feijão, frango grelhado e salada'}
            ),
            'calorias': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Opcional'}
            ),
        }    