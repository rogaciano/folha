"""
Forms do app Folha de Pagamento
"""
from django import forms
from .models import FolhaPagamento, ItemFolha
from core.models import ProventoDesconto
from funcionarios.models import Funcionario


class FolhaPagamentoForm(forms.ModelForm):
    """Form para criar/editar folha de pagamento"""
    
    class Meta:
        model = FolhaPagamento
        fields = ['mes', 'ano', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }


class GerarFolhaForm(forms.Form):
    """Form para geração de nova folha"""
    
    MESES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]
    
    mes = forms.ChoiceField(choices=MESES, label='Mês')
    ano = forms.IntegerField(min_value=2000, max_value=2100, label='Ano')


class ItemFolhaForm(forms.ModelForm):
    """Form para adicionar item manual à folha"""
    
    class Meta:
        model = ItemFolha
        fields = ['funcionario', 'provento_desconto', 'valor_lancado', 'justificativa']
        widgets = {
            'justificativa': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        folha = kwargs.pop('folha', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas funcionários ativos
        self.fields['funcionario'].queryset = Funcionario.objects.filter(status='A')
        
        # Filtra apenas proventos/descontos ativos
        self.fields['provento_desconto'].queryset = ProventoDesconto.objects.filter(ativo=True)


class EventoAdiantamentoForm(forms.Form):
    """Form para criação de evento de adiantamento massivo"""
    data_evento = forms.DateField(label='Data do Adiantamento')
    valor = forms.DecimalField(label='Valor por funcionário', max_digits=10, decimal_places=2, required=False)
    percentual = forms.DecimalField(label='Percentual do salário', max_digits=5, decimal_places=2, required=False)
    setor_id = forms.IntegerField(label='Setor (opcional)', required=False)
    funcao_id = forms.IntegerField(label='Função (opcional)', required=False)
    status = forms.ChoiceField(label='Status do funcionário', required=False, choices=[('A','Ativo'), ('F','Férias'), ('L','Licença')])

    def clean(self):
        cleaned = super().clean()
        valor = cleaned.get('valor')
        percentual = cleaned.get('percentual')
        if not valor and not percentual:
            raise forms.ValidationError('Informe valor ou percentual')
        if valor and percentual:
            raise forms.ValidationError('Informe apenas valor OU percentual')
        return cleaned


class EventoDecimoTerceiroForm(forms.Form):
    """Form para criação de evento de 13º salário"""
    data_evento = forms.DateField(label='Data do Evento')
    parcela = forms.ChoiceField(label='Parcela', choices=[(1, '1ª Parcela'), (2, '2ª Parcela')])
