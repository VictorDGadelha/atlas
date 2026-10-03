from django.utils import timezone
from django import forms
from .models import Atividade, RegistroPeso, Refeicao


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
    
    def clean_data(self):
        data = self.cleaned_data['data']
        if data > timezone.localdate():
            raise forms.ValidationError('A data não pode estar no futuro.')
        return data
    
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
    
    def clean_calorias(self):
        calorias = self.cleaned_data['calorias']
        if calorias is not None and calorias > 10000:
            raise forms.ValidationError('Informe um valor de até 10.000 kcal.')
        return calorias

class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex.: Beber 2L de água'}
            ),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        if self.usuario and Atividade.objects.filter(
            usuario=self.usuario, ativa=True, nome__iexact=nome
        ).exists():
            raise forms.ValidationError('Você já tem uma atividade com esse nome.')
        return nome