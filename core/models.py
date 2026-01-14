"""
Modelos base do sistema - Dados Mestres (Setores, Funções, Tipos de Contrato, Proventos/Descontos)
"""
from django.db import models
from django.core.validators import MinValueValidator


class TimeStampedModel(models.Model):
    """Modelo abstrato com campos de auditoria"""
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True


class Setor(TimeStampedModel):
    """Setores da empresa (Departamentos)"""
    nome = models.CharField('Nome', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    chefe = models.OneToOneField(
        'funcionarios.Funcionario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Chefe do Setor',
        related_name='setor_chefiado',
        help_text='Funcionário responsável por este setor'
    )
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
    def get_funcionarios_ativos(self):
        """Retorna todos os funcionários ativos do setor"""
        return self.funcionarios.filter(status='A')


class Funcao(TimeStampedModel):
    """Funções/Cargos da empresa"""
    nome = models.CharField('Nome', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    nivel_salarial_referencia = models.DecimalField(
        'Nível Salarial de Referência',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Valor de referência para a função'
    )
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Função'
        verbose_name_plural = 'Funções'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TipoContrato(TimeStampedModel):
    """Tipos de contrato (CLT, Estágio, PJ, etc.)"""
    nome = models.CharField('Nome', max_length=50, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Tipo de Contrato'
        verbose_name_plural = 'Tipos de Contrato'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ProventoDesconto(TimeStampedModel):
    """Tipos de proventos e descontos da folha de pagamento"""
    
    TIPO_CHOICES = [
        ('P', 'Provento'),
        ('D', 'Desconto'),
    ]
    
    IMPACTO_CHOICES = [
        ('F', 'Valor Fixo'),
        ('P', 'Percentual da Base'),
    ]
    
    nome = models.CharField('Nome', max_length=100, unique=True)
    codigo_referencia = models.CharField(
        'Código de Referência',
        max_length=20,
        unique=True,
        help_text='Código para integração com sistemas contábeis'
    )
    tipo = models.CharField('Tipo', max_length=1, choices=TIPO_CHOICES)
    impacto = models.CharField('Impacto', max_length=1, choices=IMPACTO_CHOICES)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Provento/Desconto'
        verbose_name_plural = 'Proventos/Descontos'
        ordering = ['tipo', 'nome']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"


class LancamentoFixoGeral(TimeStampedModel):
    """Lançamentos fixos gerais aplicados a todos os funcionários na folha"""
    
    provento_desconto = models.ForeignKey(
        ProventoDesconto,
        on_delete=models.PROTECT,
        verbose_name='Provento/Desconto'
    )
    valor = models.DecimalField(
        'Valor',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Preencher se o impacto for Valor Fixo'
    )
    percentual = models.DecimalField(
        'Percentual',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Preencher se o impacto for Percentual da Base'
    )
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField(
        'Data de Fim',
        null=True,
        blank=True,
        help_text='Deixar em branco para lançamento permanente'
    )
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Lançamento Fixo Geral'
        verbose_name_plural = 'Lançamentos Fixos Gerais'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"Geral - {self.provento_desconto.nome}"

    def clean(self):
        """Validações do lançamento"""
        from django.core.exceptions import ValidationError
        
        if self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError('Data de fim não pode ser anterior à data de início')
        
        # Valida que foi preenchido valor OU percentual
        if not self.valor and not self.percentual:
            raise ValidationError('Informe o valor fixo ou o percentual')
        
        if self.valor and self.percentual:
            raise ValidationError('Informe apenas valor fixo OU percentual, não ambos')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def esta_ativo(self):
        """Verifica se o lançamento está ativo"""
        from datetime import date
        hoje = date.today()
        if not self.ativo:
            return False
        if self.data_fim:
            return self.data_inicio <= hoje <= self.data_fim
        return self.data_inicio <= hoje
