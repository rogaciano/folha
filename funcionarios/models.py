"""
Modelos relacionados a Funcionários, Contratos, Lançamentos Fixos, Adiantamentos e Férias
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from validate_docbr import CPF
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from core.models import TimeStampedModel, Setor, Funcao, TipoContrato, ProventoDesconto


class Funcionario(TimeStampedModel):
    """Cadastro de funcionários"""
    
    STATUS_CHOICES = [
        ('A', 'Ativo'),
        ('I', 'Inativo'),
        ('F', 'Férias'),
        ('L', 'Licença'),
    ]
    
    nome_completo = models.CharField('Nome Completo', max_length=200)
    cpf = models.CharField('CPF', max_length=14, unique=True)
    foto = models.ImageField('Foto', upload_to='funcionarios/fotos/', blank=True, null=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    email = models.EmailField('E-mail', blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    endereco = models.TextField('Endereço', blank=True)
    chave_pix = models.CharField('Chave PIX', max_length=200, blank=True, help_text='CPF, E-mail, Telefone ou Chave Aleatória')
    
    data_admissao = models.DateField('Data de Admissão')
    funcao = models.ForeignKey(
        Funcao,
        on_delete=models.PROTECT,
        verbose_name='Função',
        related_name='funcionarios'
    )
    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        verbose_name='Setor',
        related_name='funcionarios'
    )
    salario_base = models.DecimalField(
        'Salário Base',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField('Status', max_length=1, choices=STATUS_CHOICES, default='A')
    participa_folha = models.BooleanField(
        'Participa da Folha de Pagamento',
        default=True,
        help_text='Desmarque para funcionários que não devem aparecer na folha (ex: sócios, consultores externos)'
    )
    
    # Hierarquia
    superior = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Superior/Responsável',
        related_name='subordinados',
        help_text='Funcionário responsável direto por este colaborador'
    )
    
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome_completo']

    def __str__(self):
        return f"{self.nome_completo} - {self.cpf}"

    def clean(self):
        """Validação do CPF"""
        cpf_validator = CPF()
        cpf_limpo = ''.join(filter(str.isdigit, self.cpf))
        
        if not cpf_validator.validate(cpf_limpo):
            raise ValidationError({'cpf': 'CPF inválido'})
        
        # Formata o CPF
        self.cpf = cpf_validator.mask(cpf_limpo)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def contrato_ativo(self):
        """Retorna o contrato ativo do funcionário"""
        return self.contratos.filter(
            data_inicio__lte=timezone.now().date(),
            data_fim__isnull=True
        ).first() or self.contratos.filter(
            data_inicio__lte=timezone.now().date(),
            data_fim__gte=timezone.now().date()
        ).first()

    @property
    def tempo_empresa(self):
        """Calcula o tempo de empresa em anos, meses e dias"""
        hoje = date.today()
        delta = relativedelta(hoje, self.data_admissao)
        return f"{delta.years} anos, {delta.months} meses, {delta.days} dias"
    
    def get_subordinados_diretos(self):
        """Retorna os subordinados diretos deste funcionário"""
        return self.subordinados.filter(status='A')
    
    def get_todos_subordinados(self):
        """Retorna todos os subordinados (recursivo) deste funcionário"""
        subordinados = list(self.subordinados.filter(status='A'))
        for subordinado in list(subordinados):
            subordinados.extend(subordinado.get_todos_subordinados())
        return subordinados
    
    def get_hierarquia_superior(self):
        """Retorna a cadeia hierárquica superior (até o topo)"""
        hierarquia = []
        atual = self.superior
        while atual:
            hierarquia.append(atual)
            atual = atual.superior
        return hierarquia
    
    def is_chefe(self):
        """Verifica se o funcionário é chefe de algum setor"""
        return hasattr(self, 'setor_chefiado') and self.setor_chefiado is not None
    
    def get_nivel_hierarquico(self):
        """Retorna o nível hierárquico (0 = topo, sem superior)"""
        nivel = 0
        atual = self.superior
        while atual:
            nivel += 1
            atual = atual.superior
        return nivel


class Contrato(TimeStampedModel):
    """Contratos de trabalho dos funcionários"""
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        verbose_name='Funcionário',
        related_name='contratos'
    )
    tipo_contrato = models.ForeignKey(
        TipoContrato,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Contrato'
    )
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim', null=True, blank=True)
    carga_horaria = models.IntegerField(
        'Carga Horária (horas/semana)',
        validators=[MinValueValidator(1)]
    )
    
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-data_inicio']

    def __str__(self):
        if hasattr(self, 'funcionario') and self.funcionario:
            return f"{self.funcionario.nome_completo} - {self.tipo_contrato.nome}"
        return f"Contrato - {self.tipo_contrato.nome if hasattr(self, 'tipo_contrato') and self.tipo_contrato else 'Novo'}"

    def clean(self):
        """Valida que não existe outro contrato ativo no mesmo período"""
        if self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError('Data de fim não pode ser anterior à data de início')
        
        # Só valida sobreposição se o funcionário já foi atribuído
        if not hasattr(self, 'funcionario') or self.funcionario is None:
            return
        
        # Verifica sobreposição de contratos
        contratos_sobrepostos = Contrato.objects.filter(
            funcionario=self.funcionario
        ).exclude(pk=self.pk)
        
        for contrato in contratos_sobrepostos:
            # Contrato sem data fim (ativo indefinidamente)
            if not contrato.data_fim:
                if not self.data_fim or self.data_fim >= contrato.data_inicio:
                    if self.data_inicio <= contrato.data_inicio or not self.data_fim:
                        raise ValidationError(
                            'Já existe um contrato ativo para este funcionário neste período'
                        )
            # Verifica sobreposição de datas
            elif (self.data_inicio <= contrato.data_fim and 
                  (not self.data_fim or self.data_fim >= contrato.data_inicio)):
                raise ValidationError(
                    'Já existe um contrato ativo para este funcionário neste período'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def esta_ativo(self):
        """Verifica se o contrato está ativo"""
        hoje = date.today()
        if self.data_fim:
            return self.data_inicio <= hoje <= self.data_fim
        return self.data_inicio <= hoje


class LancamentoFixo(TimeStampedModel):
    """Lançamentos fixos recorrentes na folha de pagamento"""
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        verbose_name='Funcionário',
        related_name='lancamentos_fixos'
    )
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

    class Meta:
        verbose_name = 'Lançamento Fixo'
        verbose_name_plural = 'Lançamentos Fixos'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"{self.funcionario.nome_completo} - {self.provento_desconto.nome}"

    def clean(self):
        """Validações do lançamento"""
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
        hoje = date.today()
        if self.data_fim:
            return self.data_inicio <= hoje <= self.data_fim
        return self.data_inicio <= hoje


class Adiantamento(TimeStampedModel):
    """Adiantamentos salariais"""
    
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('D', 'Descontado'),
        ('C', 'Cancelado'),
    ]
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        verbose_name='Funcionário',
        related_name='adiantamentos'
    )
    data_adiantamento = models.DateField('Data do Adiantamento')
    valor = models.DecimalField(
        'Valor',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    status = models.CharField('Status', max_length=1, choices=STATUS_CHOICES, default='P')
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Adiantamento'
        verbose_name_plural = 'Adiantamentos'
        ordering = ['-data_adiantamento']

    def __str__(self):
        return f"{self.funcionario.nome_completo} - R$ {self.valor} em {self.data_adiantamento}"


class Ferias(TimeStampedModel):
    """Controle de férias dos funcionários"""
    
    STATUS_CHOICES = [
        ('PR', 'Programada'),
        ('EG', 'Em Gozo'),
        ('CO', 'Concluída'),
        ('CA', 'Cancelada'),
    ]
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        verbose_name='Funcionário',
        related_name='ferias'
    )
    periodo_aquisitivo_inicio = models.DateField('Início do Período Aquisitivo')
    periodo_aquisitivo_fim = models.DateField('Fim do Período Aquisitivo')
    data_inicio_gozo = models.DateField('Início do Gozo')
    data_fim_gozo = models.DateField('Fim do Gozo')
    dias_corridos = models.IntegerField('Dias Corridos', default=30)
    status = models.CharField('Status', max_length=2, choices=STATUS_CHOICES, default='PR')
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Férias'
        verbose_name_plural = 'Férias'
        ordering = ['-data_inicio_gozo']

    def __str__(self):
        return f"{self.funcionario.nome_completo} - {self.data_inicio_gozo} a {self.data_fim_gozo}"

    def clean(self):
        """Validações"""
        if self.data_inicio_gozo > self.data_fim_gozo:
            raise ValidationError('Data de início não pode ser posterior à data de fim')
        
        if self.periodo_aquisitivo_inicio > self.periodo_aquisitivo_fim:
            raise ValidationError('Período aquisitivo inválido')
        
        # Calcula os dias corridos
        delta = (self.data_fim_gozo - self.data_inicio_gozo).days + 1
        self.dias_corridos = delta

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def calcular_periodo_aquisitivo(cls, data_admissao):
        """Calcula o período aquisitivo baseado na data de admissão"""
        hoje = date.today()
        anos_completos = (hoje - data_admissao).days // 365
        
        inicio = data_admissao + relativedelta(years=anos_completos)
        fim = inicio + relativedelta(years=1) - timedelta(days=1)
        
        return inicio, fim
