"""
Formulários do app Core
"""
from django import forms
from .models import LancamentoFixoGeral, ProventoDesconto, Setor, Funcao, TipoContrato
from datetime import date


class SetorForm(forms.ModelForm):
    """Form para criar/editar setores"""
    class Meta:
        model = Setor
        fields = ['nome', 'descricao', 'chefe', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: Financeiro, TI, Recursos Humanos',
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Descrição das responsabilidades do setor'
            }),
            'chefe': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }


class FuncaoForm(forms.ModelForm):
    """Form para criar/editar funções/cargos"""
    class Meta:
        model = Funcao
        fields = ['nome', 'descricao', 'nivel_salarial_referencia', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: Analista Financeiro, Desenvolvedor, Auxiliar Administrativo',
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Principais atribuições do cargo'
            }),
            'nivel_salarial_referencia': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'R$ 0,00',
                'step': '0.01',
                'min': '0'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }


class TipoContratoForm(forms.ModelForm):
    """Form para criar/editar tipos de contrato"""
    class Meta:
        model = TipoContrato
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: CLT - Mensalista, Estágio, PJ, Menor Aprendiz',
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Observações e regras deste regime de contratação'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }


class ProventoDescontoForm(forms.ModelForm):
    """Form para criar/editar proventos e descontos"""
    class Meta:
        model = ProventoDesconto
        fields = ['nome', 'codigo_referencia', 'tipo', 'impacto', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: Vale Transporte, Adicional Noturno, Bônus Meta',
                'required': True
            }),
            'codigo_referencia': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase',
                'placeholder': 'Ex: VT, ADIC_NOT, BONUS',
                'required': True
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'required': True
            }),
            'impacto': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Base legal ou justificativa para este item'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }


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
