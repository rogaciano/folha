"""
Formulários do app Core
"""
from django import forms
from .models import LancamentoFixoGeral, ProventoDesconto
from datetime import date


class LancamentoFixoGeralForm(forms.ModelForm):
    """Form para criar/editar lançamentos fixos gerais"""
    
    class Meta:
        model = LancamentoFixoGeral
        fields = ['provento_desconto', 'valor', 'percentual', 'data_inicio', 'data_fim', 'observacoes', 'ativo']
        widgets = {
            'provento_desconto': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'required': True
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Valor fixo',
                'step': '0.01',
                'min': '0'
            }),
            'percentual': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Percentual',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date',
                'required': True
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Observações sobre o lançamento'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define data_inicio como hoje se for novo registro
        if not self.instance.pk:
            self.initial['data_inicio'] = date.today()
            self.initial['ativo'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        valor = cleaned_data.get('valor')
        percentual = cleaned_data.get('percentual')
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        # Valida que foi preenchido valor OU percentual
        if not valor and not percentual:
            raise forms.ValidationError('Informe o valor fixo ou o percentual')
        
        if valor and percentual:
            raise forms.ValidationError('Informe apenas valor fixo OU percentual, não ambos')
        
        # Valida datas
        if data_fim and data_inicio and data_fim < data_inicio:
            raise forms.ValidationError('Data de fim não pode ser anterior à data de início')
        
        return cleaned_data
