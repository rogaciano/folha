"""
Forms do app Funcionários
"""
from django import forms
from .models import Funcionario, Contrato, LancamentoFixo, Adiantamento, Ferias


class FuncionarioForm(forms.ModelForm):
    """Form para cadastro de funcionários"""
    
    class Meta:
        model = Funcionario
        fields = ['nome_completo', 'cpf', 'foto', 'data_nascimento', 'email', 'telefone', 
                 'endereco', 'chave_pix', 'data_admissao', 'funcao', 'setor', 'salario_base', 
                 'superior', 'status', 'participa_folha', 'observacoes']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_admissao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'endereco': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar os formatos de entrada para os campos de data
        self.fields['data_nascimento'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['data_admissao'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        
        # Evitar que um funcionário seja seu próprio superior
        if self.instance.pk:
            self.fields['superior'].queryset = Funcionario.objects.exclude(pk=self.instance.pk).filter(status='A')


class ContratoForm(forms.ModelForm):
    """Form para contratos"""
    
    class Meta:
        model = Contrato
        fields = ['tipo_contrato', 'data_inicio', 'data_fim', 
                 'carga_horaria', 'observacoes']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_inicio'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['data_fim'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']


class LancamentoFixoForm(forms.ModelForm):
    """Form para lançamentos fixos"""
    
    TIPO_VALOR_CHOICES = [
        ('F', 'Valor Fixo'),
        ('P', 'Percentual do Salário'),
    ]
    
    tipo_valor = forms.ChoiceField(
        choices=TIPO_VALOR_CHOICES,
        initial='F',
        label='Tipo de Valor',
        required=True,
        widget=forms.Select(attrs={'class': 'tipo-valor-select'})
    )
    
    class Meta:
        model = LancamentoFixo
        fields = ['provento_desconto', 'valor', 'percentual', 
                 'data_inicio', 'data_fim', 'observacoes']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_inicio'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['data_fim'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        
        # Filtrar apenas proventos/descontos ativos
        from core.models import ProventoDesconto
        self.fields['provento_desconto'].queryset = ProventoDesconto.objects.filter(ativo=True)
        
        # Definir o valor inicial do tipo_valor baseado na instância
        if self.instance.pk:
            if self.instance.valor:
                self.fields['tipo_valor'].initial = 'F'
            elif self.instance.percentual:
                self.fields['tipo_valor'].initial = 'P'
        
        # Reordenar os campos
        self.order_fields(['provento_desconto', 'tipo_valor', 'valor', 'percentual', 
                          'data_inicio', 'data_fim', 'observacoes'])
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_valor = cleaned_data.get('tipo_valor')
        valor = cleaned_data.get('valor')
        percentual = cleaned_data.get('percentual')
        
        # Validar que o campo correto foi preenchido
        if tipo_valor == 'F' and not valor:
            self.add_error('valor', 'Informe o valor fixo')
        
        if tipo_valor == 'P' and not percentual:
            self.add_error('percentual', 'Informe o percentual')
        
        return cleaned_data


class AdiantamentoForm(forms.ModelForm):
    """Form para adiantamentos"""
    
    class Meta:
        model = Adiantamento
        fields = ['funcionario', 'data_adiantamento', 'valor', 'observacoes']
        widgets = {
            'data_adiantamento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_adiantamento'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']


class AdiantamentoMassivoForm(forms.Form):
    """Form para lançamento de adiantamentos em massa"""
    
    TIPO_VALOR_CHOICES = [
        ('F', 'Valor Fixo'),
        ('P', 'Percentual do Salário'),
    ]
    
    folha_pagamento = forms.ModelChoiceField(
        queryset=None,
        required=True,
        label='Folha de Pagamento',
        help_text='Selecione a folha onde os lançamentos serão aplicados'
    )
    provento_desconto = forms.ModelChoiceField(
        queryset=None,
        required=True,
        label='Provento/Desconto',
        help_text='Tipo de lançamento a ser aplicado'
    )
    setor = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Setor',
        help_text='Filtrar por setor (opcional)'
    )
    funcao = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Função',
        help_text='Filtrar por função (opcional)'
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + Funcionario.STATUS_CHOICES,
        required=False,
        initial='A',
        label='Status do Funcionário'
    )
    tipo_valor = forms.ChoiceField(
        choices=TIPO_VALOR_CHOICES,
        initial='F',
        label='Tipo de Valor'
    )
    valor_fixo = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label='Valor Fixo',
        help_text='Valor fixo a ser aplicado a todos'
    )
    percentual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        label='Percentual',
        help_text='Percentual do salário base'
    )
    data_adiantamento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data do Adiantamento',
        required=False,
        help_text='Opcional - para registro histórico'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Setor, Funcao, ProventoDesconto
        from folha.models import FolhaPagamento
        
        self.fields['setor'].queryset = Setor.objects.filter(ativo=True)
        self.fields['funcao'].queryset = Funcao.objects.filter(ativo=True)
        self.fields['provento_desconto'].queryset = ProventoDesconto.objects.filter(ativo=True)
        
        # Folhas em rascunho, ordenadas pela mais recente
        folhas_abertas = FolhaPagamento.objects.filter(status='R').order_by('-ano', '-mes')
        self.fields['folha_pagamento'].queryset = folhas_abertas
        
        # Define a folha mais recente como inicial
        if folhas_abertas.exists():
            self.fields['folha_pagamento'].initial = folhas_abertas.first().pk
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_valor = cleaned_data.get('tipo_valor')
        valor_fixo = cleaned_data.get('valor_fixo')
        percentual = cleaned_data.get('percentual')
        
        if tipo_valor == 'F' and not valor_fixo:
            raise forms.ValidationError('Informe o valor fixo')
        
        if tipo_valor == 'P' and not percentual:
            raise forms.ValidationError('Informe o percentual')
        
        return cleaned_data


class FeriasForm(forms.ModelForm):
    """Form para férias"""
    
    class Meta:
        model = Ferias
        fields = ['funcionario', 'periodo_aquisitivo_inicio', 'periodo_aquisitivo_fim',
                 'data_inicio_gozo', 'data_fim_gozo', 'status', 'observacoes']
        widgets = {
            'periodo_aquisitivo_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'periodo_aquisitivo_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_inicio_gozo': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'data_fim_gozo': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['periodo_aquisitivo_inicio'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['periodo_aquisitivo_fim'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['data_inicio_gozo'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['data_fim_gozo'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
