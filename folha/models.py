"""
Modelos relacionados à Folha de Pagamento
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from core.models import TimeStampedModel, ProventoDesconto
from funcionarios.models import Funcionario, Contrato, LancamentoFixo, Adiantamento


class FolhaPagamento(TimeStampedModel):
    """Folha de pagamento mensal (Competência)"""
    
    STATUS_CHOICES = [
        ('R', 'Rascunho'),
        ('F', 'Fechada'),
        ('P', 'Paga'),
        ('C', 'Cancelada'),
    ]
    
    mes = models.IntegerField('Mês', validators=[MinValueValidator(1)])
    ano = models.IntegerField('Ano', validators=[MinValueValidator(2000)])
    data_fechamento = models.DateTimeField('Data de Fechamento', null=True, blank=True)
    status = models.CharField('Status', max_length=1, choices=STATUS_CHOICES, default='R')
    contratos_ativos = models.ManyToManyField(
        Contrato,
        verbose_name='Contratos Ativos',
        related_name='folhas',
        blank=True
    )
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Folha de Pagamento'
        verbose_name_plural = 'Folhas de Pagamento'
        ordering = ['-ano', '-mes']
        unique_together = ['mes', 'ano']

    def __str__(self):
        return f"Folha {self.mes:02d}/{self.ano} - {self.get_status_display()}"

    def clean(self):
        """Validações"""
        if not 1 <= self.mes <= 12:
            raise ValidationError({'mes': 'Mês deve estar entre 1 e 12'})
        
        # Verifica se já existe folha para o mesmo período
        folhas_existentes = FolhaPagamento.objects.filter(
            mes=self.mes,
            ano=self.ano
        ).exclude(pk=self.pk)
        
        if folhas_existentes.exists():
            raise ValidationError('Já existe uma folha de pagamento para este período')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def periodo_referencia(self):
        """Retorna o período de referência formatado"""
        return f"{self.mes:02d}/{self.ano}"

    @property
    def total_proventos(self):
        """Calcula o total de proventos da folha"""
        total = self.itens.filter(
            provento_desconto__tipo='P'
        ).aggregate(total=Sum('valor_lancado'))['total'] or Decimal('0.00')
        return total

    @property
    def total_descontos(self):
        """Calcula o total de descontos da folha"""
        total = self.itens.filter(
            provento_desconto__tipo='D'
        ).aggregate(total=Sum('valor_lancado'))['total'] or Decimal('0.00')
        return total

    @property
    def total_liquido(self):
        """Calcula o total líquido da folha"""
        return self.total_proventos - self.total_descontos

    def fechar_folha(self):
        """Fecha a folha de pagamento"""
        if self.status != 'R':
            raise ValidationError('Apenas folhas em rascunho podem ser fechadas')
        
        self.status = 'F'
        self.data_fechamento = timezone.now()
        self.save()

    def reabrir_folha(self):
        """Reabre a folha de pagamento para edição"""
        if self.status != 'F':
            raise ValidationError('Apenas folhas fechadas podem ser reabertas')
        
        self.status = 'R'
        self.data_fechamento = None
        self.save()

    def marcar_como_paga(self):
        """Marca a folha como paga"""
        if self.status != 'F':
            raise ValidationError('Apenas folhas fechadas podem ser marcadas como pagas')
        
        self.status = 'P'
        self.save()

    def get_eventos_pagamento(self):
        """Retorna todos os eventos de pagamento desta folha"""
        return self.eventos.all().order_by('data_evento')

    def get_total_eventos_pagos(self):
        """Retorna o total de eventos já pagos"""
        return self.eventos.filter(status='P').aggregate(
            total=Sum('valor_total')
        )['total'] or Decimal('0.00')

    def get_total_eventos_pendentes(self):
        """Retorna o total de eventos pendentes"""
        return self.eventos.exclude(status='P').aggregate(
            total=Sum('valor_total')
        )['total'] or Decimal('0.00')


class EventoPagamento(TimeStampedModel):
    """Eventos de pagamento dentro de uma competência (ex: adiantamento quinzenal, pagamento final)"""
    
    TIPO_EVENTO_CHOICES = [
        ('AD', 'Adiantamento Quinzenal'),
        ('PF', 'Pagamento Final'),
        ('13', '13º Salário'),
        ('FE', 'Férias'),
        ('RE', 'Rescisão'),
        ('OU', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('R', 'Rascunho'),
        ('F', 'Fechado'),
        ('P', 'Pago'),
        ('C', 'Cancelado'),
    ]
    
    folha_pagamento = models.ForeignKey(
        FolhaPagamento,
        on_delete=models.CASCADE,
        verbose_name='Folha de Pagamento',
        related_name='eventos'
    )
    tipo_evento = models.CharField(
        'Tipo de Evento',
        max_length=2,
        choices=TIPO_EVENTO_CHOICES,
        default='PF'
    )
    descricao = models.CharField(
        'Descrição',
        max_length=200,
        help_text='Ex: Adiantamento Quinzenal 15/01, Pagamento Final 30/01'
    )
    data_evento = models.DateField(
        'Data do Evento',
        help_text='Data prevista ou realizada do pagamento'
    )
    data_pagamento = models.DateField(
        'Data do Pagamento',
        null=True,
        blank=True,
        help_text='Data em que o pagamento foi efetivamente realizado'
    )
    status = models.CharField(
        'Status',
        max_length=1,
        choices=STATUS_CHOICES,
        default='R'
    )
    valor_total = models.DecimalField(
        'Valor Total do Evento',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Calculado automaticamente a partir dos itens'
    )
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Evento de Pagamento'
        verbose_name_plural = 'Eventos de Pagamento'
        ordering = ['folha_pagamento', 'data_evento']
        unique_together = ['folha_pagamento', 'descricao']

    def __str__(self):
        return f"{self.folha_pagamento.periodo_referencia} - {self.descricao} ({self.get_status_display()})"

    def clean(self):
        """Validações"""
        # Valida que a data do evento está dentro da competência
        if self.data_evento:
            if self.data_evento.month != self.folha_pagamento.mes or \
               self.data_evento.year != self.folha_pagamento.ano:
                raise ValidationError(
                    'A data do evento deve estar dentro da competência da folha de pagamento'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_proventos(self):
        """Calcula o total de proventos do evento"""
        total = self.itens.filter(
            provento_desconto__tipo='P'
        ).aggregate(total=Sum('valor_lancado'))['total'] or Decimal('0.00')
        return total

    @property
    def total_descontos(self):
        """Calcula o total de descontos do evento"""
        total = self.itens.filter(
            provento_desconto__tipo='D'
        ).aggregate(total=Sum('valor_lancado'))['total'] or Decimal('0.00')
        return total

    @property
    def total_liquido(self):
        """Calcula o total líquido do evento"""
        return self.total_proventos - self.total_descontos

    def calcular_valor_total(self):
        """Recalcula o valor total do evento"""
        self.valor_total = self.total_liquido
        self.save(update_fields=['valor_total'])

    def fechar_evento(self):
        """Fecha o evento de pagamento"""
        if self.status != 'R':
            raise ValidationError('Apenas eventos em rascunho podem ser fechados')
        
        self.status = 'F'
        self.calcular_valor_total()
        self.save()

    def marcar_como_pago(self, data_pagamento=None):
        """Marca o evento como pago"""
        if self.status not in ['F', 'R']:
            raise ValidationError('Apenas eventos fechados ou em rascunho podem ser marcados como pagos')
        
        self.status = 'P'
        self.data_pagamento = data_pagamento or timezone.now().date()
        self.save()

    def reabrir_evento(self):
        """Reabre o evento para edição"""
        if self.status != 'F':
            raise ValidationError('Apenas eventos fechados podem ser reabertos')
        
        self.status = 'R'
        self.save()


class ItemFolha(TimeStampedModel):
    """Itens individuais da folha de pagamento (linha por linha)"""
    
    evento_pagamento = models.ForeignKey(
        EventoPagamento,
        on_delete=models.CASCADE,
        verbose_name='Evento de Pagamento',
        related_name='itens'
    )
    folha_pagamento = models.ForeignKey(
        FolhaPagamento,
        on_delete=models.CASCADE,
        verbose_name='Folha de Pagamento',
        related_name='itens',
        help_text='Referência à competência (mantida para compatibilidade)'
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        verbose_name='Funcionário',
        related_name='itens_folha'
    )
    provento_desconto = models.ForeignKey(
        ProventoDesconto,
        on_delete=models.PROTECT,
        verbose_name='Provento/Desconto'
    )
    valor_lancado = models.DecimalField(
        'Valor Lançado',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    base_calculo = models.DecimalField(
        'Base de Cálculo',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Base utilizada para cálculo percentual'
    )
    justificativa = models.TextField('Justificativa', blank=True)
    
    # Rastreabilidade de adiantamentos
    adiantamento_origem = models.ForeignKey(
        Adiantamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Adiantamento Origem',
        related_name='itens_desconto',
        help_text='Referência ao adiantamento original (quando aplicável)'
    )

    class Meta:
        verbose_name = 'Item da Folha'
        verbose_name_plural = 'Itens da Folha'
        ordering = ['evento_pagamento', 'funcionario', 'provento_desconto']

    def __str__(self):
        return f"{self.evento_pagamento.descricao} - {self.funcionario.nome_completo} - {self.provento_desconto.nome}"

    @property
    def tipo_item(self):
        """Retorna o tipo do item (Provento ou Desconto)"""
        return self.provento_desconto.get_tipo_display()


class ResumoFolhaFuncionario(models.Model):
    """
    View materializada para resumo da folha por funcionário
    Otimiza consultas de totalizadores
    """
    folha_pagamento = models.ForeignKey(
        FolhaPagamento,
        on_delete=models.CASCADE,
        related_name='resumos'
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='resumos_folha'
    )
    total_proventos = models.DecimalField(
        'Total de Proventos',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_descontos = models.DecimalField(
        'Total de Descontos',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    valor_liquido = models.DecimalField(
        'Valor Líquido',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        verbose_name = 'Resumo da Folha por Funcionário'
        verbose_name_plural = 'Resumos da Folha por Funcionário'
        unique_together = ['folha_pagamento', 'funcionario']

    def __str__(self):
        return f"{self.folha_pagamento} - {self.funcionario.nome_completo}"

    def calcular_totais(self):
        """Calcula os totais de proventos, descontos e líquido"""
        itens = ItemFolha.objects.filter(
            folha_pagamento=self.folha_pagamento,
            funcionario=self.funcionario
        )
        
        self.total_proventos = itens.filter(
            provento_desconto__tipo='P'
        ).aggregate(total=Sum('valor_lancado'))['total'] or Decimal('0.00')
        
        self.total_descontos = itens.filter(
            provento_desconto__tipo='D'
        ).aggregate(total=Sum('valor_lancado'))['total'] or Decimal('0.00')
        
        self.valor_liquido = self.total_proventos - self.total_descontos
        
        self.save()
