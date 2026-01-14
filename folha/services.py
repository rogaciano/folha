"""
Services - Lógica de negócio para geração e manipulação de folhas de pagamento
"""
from decimal import Decimal
from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import FolhaPagamento, EventoPagamento, ItemFolha, ResumoFolhaFuncionario
from funcionarios.models import Funcionario, Contrato, LancamentoFixo, Adiantamento
from core.models import ProventoDesconto, LancamentoFixoGeral


class FolhaService:
    """Service para gerenciamento de folhas de pagamento"""
    
    @staticmethod
    def gerar_folha(mes: int, ano: int, criar_evento_padrao: bool = True) -> FolhaPagamento:
        """
        Gera uma nova folha de pagamento para o mês/ano especificado
        
        Args:
            mes: Mês da folha (1-12)
            ano: Ano da folha
            
        Returns:
            FolhaPagamento: Instância da folha criada
        """
        with transaction.atomic():
            # Cria a folha
            folha = FolhaPagamento.objects.create(mes=mes, ano=ano)
            
            # Busca todos os contratos ativos no período
            primeiro_dia = date(ano, mes, 1)
            if mes == 12:
                ultimo_dia = date(ano + 1, 1, 1)
            else:
                ultimo_dia = date(ano, mes + 1, 1)
            
            contratos_ativos = Contrato.objects.filter(
                data_inicio__lte=ultimo_dia,
                funcionario__participa_folha=True  # Apenas funcionários que participam da folha
            ).filter(
                models.Q(data_fim__isnull=True) | models.Q(data_fim__gte=primeiro_dia)
            ).select_related('funcionario', 'tipo_contrato')
            
            # Adiciona contratos ativos à folha
            folha.contratos_ativos.set(contratos_ativos)
            
            # Cria evento padrão se solicitado (para compatibilidade)
            if criar_evento_padrao:
                import calendar
                ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
                data_evento = date(ano, mes, ultimo_dia_mes)
                
                evento = EventoPagamento.objects.create(
                    folha_pagamento=folha,
                    tipo_evento='PF',
                    descricao=f'Pagamento Final {mes:02d}/{ano}',
                    data_evento=data_evento,
                    status='R'
                )
                
                # Processa cada funcionário no evento padrão
                for contrato in contratos_ativos:
                    funcionario = contrato.funcionario
                    
                    # 1. Lança o salário base
                    FolhaService._lancar_salario_base(folha, evento, funcionario)
                    
                    # 2. Lança os lançamentos fixos gerais
                    FolhaService._lancar_lancamentos_fixos_gerais(folha, evento, funcionario, primeiro_dia, ultimo_dia)
                    
                    # 3. Lança os lançamentos fixos do funcionário
                    FolhaService._lancar_lancamentos_fixos(folha, evento, funcionario, primeiro_dia, ultimo_dia)
                    
                    # 4. Lança adiantamentos pendentes
                    FolhaService._lancar_adiantamentos(folha, evento, funcionario)
                    
                    # 5. Cria o resumo do funcionário
                    FolhaService._criar_resumo_funcionario(folha, funcionario)
                
                # Recalcula o valor total do evento
                evento.calcular_valor_total()
            
            return folha
    
    @staticmethod
    def criar_evento_pagamento(folha: FolhaPagamento, tipo_evento: str, descricao: str,
                               data_evento: date, processar_funcionarios: bool = True) -> EventoPagamento:
        """
        Cria um novo evento de pagamento dentro de uma competência
        
        Args:
            folha: Folha de pagamento (competência)
            tipo_evento: Tipo do evento (AD, PF, 13, FE, RE, OU)
            descricao: Descrição do evento
            data_evento: Data do evento
            processar_funcionarios: Se True, processa todos os funcionários automaticamente
            
        Returns:
            EventoPagamento: Evento criado
        """
        if folha.status != 'R':
            raise ValidationError('Apenas folhas em rascunho podem ter novos eventos')
        
        with transaction.atomic():
            evento = EventoPagamento.objects.create(
                folha_pagamento=folha,
                tipo_evento=tipo_evento,
                descricao=descricao,
                data_evento=data_evento,
                status='R'
            )
            
            if processar_funcionarios:
                # Processa todos os funcionários da folha
                for contrato in folha.contratos_ativos.all():
                    funcionario = contrato.funcionario
                    
                    # Lança apenas o salário base (outros lançamentos devem ser manuais)
                    FolhaService._lancar_salario_base(folha, evento, funcionario)
                
                evento.calcular_valor_total()
            
            return evento

    @staticmethod
    def criar_evento_adiantamento_massivo(
        folha: FolhaPagamento,
        descricao: str,
        data_evento: date,
        filtros: dict = None,
        valor: Decimal = None,
        percentual: Decimal = None,
    ) -> EventoPagamento:
        """
        Cria um evento de adiantamento (AD) e lança adiantamentos em massa.

        Args:
            folha: Folha de pagamento (competência)
            descricao: Descrição do evento (ex: Adiantamento Quinzenal 15/MM)
            data_evento: Data do adiantamento
            filtros: Filtros para seleção de funcionários (setor_id, funcao_id, status)
            valor: Valor fixo por funcionário (opcional)
            percentual: Percentual do salário base por funcionário (opcional)

        Returns:
            EventoPagamento: Evento criado com valor_total somado dos adiantamentos
        """
        if folha.status != 'R':
            raise ValidationError('Apenas folhas em rascunho podem ter novos eventos')

        if not valor and not percentual:
            raise ValidationError('Informe um valor fixo ou percentual')

        filtros = filtros or {}

        with transaction.atomic():
            evento = EventoPagamento.objects.create(
                folha_pagamento=folha,
                tipo_evento='AD',
                descricao=descricao,
                data_evento=data_evento,
                status='R',
            )

            # Seleciona funcionários da competência
            funcionarios = [c.funcionario for c in folha.contratos_ativos.all()]
            if filtros:
                from funcionarios.models import Funcionario as FuncModel
                qs = FuncModel.objects.filter(pk__in=[f.pk for f in funcionarios])
                qs = qs.filter(**filtros)
                funcionarios = list(qs)

            total_evento = Decimal('0')
            for funcionario in funcionarios:
                if valor:
                    valor_adiantamento = valor
                else:
                    valor_adiantamento = (funcionario.salario_base * percentual) / Decimal('100')
                
                # Arredondar para 2 casas decimais
                valor_adiantamento = valor_adiantamento.quantize(Decimal('0.01'))

                from funcionarios.models import Adiantamento as AdModel
                AdModel.objects.create(
                    funcionario=funcionario,
                    data_adiantamento=data_evento,
                    valor=valor_adiantamento,
                    status='P',
                    observacoes=descricao,
                )
                total_evento += valor_adiantamento

            evento.valor_total = total_evento.quantize(Decimal('0.01'))
            evento.save(update_fields=['valor_total'])

            return evento

    @staticmethod
    def criar_evento_decimo_terceiro(
        folha: FolhaPagamento,
        descricao: str,
        data_evento: date,
        parcela: int = 1,
    ) -> EventoPagamento:
        """
        Cria um evento de 13º salário e lança itens por funcionário.

        Regra simples:
        - 1ª parcela: 50% do salário base como provento.
        - 2ª parcela: 50% restante como provento. Descontos (INSS/IR) podem ser
          adicionados manualmente conforme necessidade.
        """
        if folha.status != 'R':
            raise ValidationError('Apenas folhas em rascunho podem ter novos eventos')

        if parcela not in (1, 2):
            raise ValidationError('Parcela deve ser 1 ou 2')

        with transaction.atomic():
            evento = EventoPagamento.objects.create(
                folha_pagamento=folha,
                tipo_evento='13',
                descricao=descricao,
                data_evento=data_evento,
                status='R',
            )

            # Provento específico para 13º
            try:
                provento_13 = ProventoDesconto.objects.get(
                    codigo_referencia='SALARIO_13',
                    tipo='P',
                )
            except ProventoDesconto.DoesNotExist:
                provento_13 = ProventoDesconto.objects.create(
                    nome='13º Salário',
                    codigo_referencia='SALARIO_13',
                    tipo='P',
                    impacto='F',
                )

            fator = Decimal('0.50') if parcela == 1 else Decimal('0.50')

            total_evento = Decimal('0')
            for contrato in folha.contratos_ativos.all():
                funcionario = contrato.funcionario
                valor = (funcionario.salario_base * fator).quantize(Decimal('0.01'))

                ItemFolha.objects.create(
                    folha_pagamento=folha,
                    evento_pagamento=evento,
                    funcionario=funcionario,
                    provento_desconto=provento_13,
                    valor_lancado=valor,
                    justificativa=f'13º salário - {parcela}ª parcela',
                )
                total_evento += valor

            evento.valor_total = total_evento.quantize(Decimal('0.01'))
            evento.save(update_fields=['valor_total'])

            return evento
    
    @staticmethod
    def _lancar_salario_base(folha: FolhaPagamento, evento: EventoPagamento, funcionario: Funcionario):
        """Lança o salário base do funcionário na folha"""
        try:
            provento_salario = ProventoDesconto.objects.get(
                codigo_referencia='SALARIO',
                tipo='P'
            )
        except ProventoDesconto.DoesNotExist:
            # Cria o provento de salário se não existir
            provento_salario = ProventoDesconto.objects.create(
                nome='Salário Base',
                codigo_referencia='SALARIO',
                tipo='P',
                impacto='F'
            )
        
        ItemFolha.objects.create(
            folha_pagamento=folha,
            evento_pagamento=evento,
            funcionario=funcionario,
            provento_desconto=provento_salario,
            valor_lancado=funcionario.salario_base,
            justificativa='Salário base mensal'
        )
    
    @staticmethod
    def _lancar_lancamentos_fixos_gerais(folha: FolhaPagamento, evento: EventoPagamento,
                                         funcionario: Funcionario, data_inicio: date, data_fim: date):
        """Lança todos os lançamentos fixos gerais ativos para o funcionário"""
        from django.db.models import Q
        
        # Para comparação correta: data_fim é o primeiro dia do mês seguinte,
        # então usamos < ao invés de <= para excluir lançamentos que começam no mês seguinte
        lancamentos_gerais = LancamentoFixoGeral.objects.filter(
            ativo=True,
            data_inicio__lt=data_fim  # Alterado de __lte para __lt
        ).filter(
            Q(data_fim__isnull=True) | Q(data_fim__gte=data_inicio)
        ).select_related('provento_desconto')
        
        for lancamento in lancamentos_gerais:
            # Calcula o valor baseado no tipo de impacto
            if lancamento.provento_desconto.impacto == 'F':
                valor = lancamento.valor or Decimal('0')
                base = None
            else:  # Percentual
                base = funcionario.salario_base
                percentual = lancamento.percentual or Decimal('0')
                valor = (base * percentual) / Decimal('100')
            
            # Ignora lançamentos com valor zero
            if valor <= 0:
                continue
            
            ItemFolha.objects.create(
                folha_pagamento=folha,
                evento_pagamento=evento,
                funcionario=funcionario,
                provento_desconto=lancamento.provento_desconto,
                valor_lancado=valor,
                base_calculo=base,
                justificativa=f'Lançamento fixo geral - {lancamento.observacoes}'
            )
    
    @staticmethod
    def _lancar_lancamentos_fixos(folha: FolhaPagamento, evento: EventoPagamento,
                                   funcionario: Funcionario, data_inicio: date, data_fim: date):
        """Lança todos os lançamentos fixos ativos do funcionário"""
        from django.db.models import Q
        
        # Para comparação correta: data_fim é o primeiro dia do mês seguinte,
        # então usamos < ao invés de <= para excluir lançamentos que começam no mês seguinte
        lancamentos = LancamentoFixo.objects.filter(
            funcionario=funcionario,
            data_inicio__lt=data_fim  # Alterado de __lte para __lt
        ).filter(
            Q(data_fim__isnull=True) | Q(data_fim__gte=data_inicio)
        ).select_related('provento_desconto')
        
        for lancamento in lancamentos:
            # Calcula o valor baseado no tipo de impacto
            if lancamento.provento_desconto.impacto == 'F':
                valor = lancamento.valor or Decimal('0')
                base = None
            else:  # Percentual
                base = funcionario.salario_base
                percentual = lancamento.percentual or Decimal('0')
                valor = (base * percentual) / Decimal('100')
            
            # Ignora lançamentos com valor zero
            if valor <= 0:
                continue
            
            ItemFolha.objects.create(
                folha_pagamento=folha,
                evento_pagamento=evento,
                funcionario=funcionario,
                provento_desconto=lancamento.provento_desconto,
                valor_lancado=valor,
                base_calculo=base,
                justificativa=f'Lançamento fixo - {lancamento.observacoes}'
            )
    
    @staticmethod
    def _lancar_adiantamentos(folha: FolhaPagamento, evento: EventoPagamento, funcionario: Funcionario):
        """Lança adiantamentos pendentes como descontos na folha"""
        adiantamentos_pendentes = Adiantamento.objects.filter(
            funcionario=funcionario,
            status='P'
        )
        
        if not adiantamentos_pendentes.exists():
            return
        
        # Busca ou cria o desconto de adiantamento
        try:
            desconto_adiantamento = ProventoDesconto.objects.get(
                codigo_referencia='ADIANTAMENTO',
                tipo='D'
            )
        except ProventoDesconto.DoesNotExist:
            desconto_adiantamento = ProventoDesconto.objects.create(
                nome='Adiantamento Salarial',
                codigo_referencia='ADIANTAMENTO',
                tipo='D',
                impacto='F'
            )
        
        for adiantamento in adiantamentos_pendentes:
            ItemFolha.objects.create(
                folha_pagamento=folha,
                evento_pagamento=evento,
                funcionario=funcionario,
                provento_desconto=desconto_adiantamento,
                valor_lancado=adiantamento.valor,
                justificativa=f'Adiantamento de {adiantamento.data_adiantamento}',
                adiantamento_origem=adiantamento  # Link direto para rastreabilidade
            )
            
            # Marca o adiantamento como descontado
            adiantamento.status = 'D'
            adiantamento.save()
    
    @staticmethod
    def _criar_resumo_funcionario(folha: FolhaPagamento, funcionario: Funcionario):
        """Cria o resumo da folha para o funcionário"""
        resumo, created = ResumoFolhaFuncionario.objects.get_or_create(
            folha_pagamento=folha,
            funcionario=funcionario
        )
        resumo.calcular_totais()
    
    @staticmethod
    def adicionar_item_manual(evento: EventoPagamento = None, folha: FolhaPagamento = None,
                            funcionario: Funcionario = None, provento_desconto: ProventoDesconto = None,
                            valor: Decimal = None, justificativa: str = '') -> ItemFolha:
        """
        Adiciona um item manual a um evento de pagamento
        
        Args:
            evento: Evento de pagamento (preferencial)
            folha: Folha de pagamento (para compatibilidade - busca/cria evento padrão)
            funcionario: Funcionário
            provento_desconto: Provento ou desconto
            valor: Valor do lançamento
            justificativa: Justificativa do lançamento
            
        Returns:
            ItemFolha: Item criado
            
        Nota:
            Se apenas 'folha' for fornecida, busca ou cria um evento padrão automaticamente.
            Isso mantém compatibilidade com código existente.
        """
        # Compatibilidade: se folha foi passada mas evento não, busca/cria evento padrão
        if folha and not evento:
            # Busca evento padrão existente
            evento = folha.eventos.filter(tipo_evento='PF').first()
            
            # Se não existe, cria um evento padrão
            if not evento:
                import calendar
                ultimo_dia = calendar.monthrange(folha.ano, folha.mes)[1]
                data_evento = date(folha.ano, folha.mes, ultimo_dia)
                
                evento = EventoPagamento.objects.create(
                    folha_pagamento=folha,
                    tipo_evento='PF',
                    descricao=f'Pagamento Final {folha.mes:02d}/{folha.ano}',
                    data_evento=data_evento,
                    status='R'
                )
        
        if not evento:
            raise ValidationError('Evento de pagamento não especificado')
        
        if evento.status != 'R':
            raise ValidationError('Apenas eventos em rascunho podem ser editados')
        
        item = ItemFolha.objects.create(
            folha_pagamento=evento.folha_pagamento,
            evento_pagamento=evento,
            funcionario=funcionario,
            provento_desconto=provento_desconto,
            valor_lancado=valor,
            justificativa=justificativa
        )
        
        # Atualiza o valor total do evento
        evento.calcular_valor_total()
        
        # Atualiza o resumo do funcionário
        FolhaService._criar_resumo_funcionario(evento.folha_pagamento, funcionario)
        
        return item
    
    @staticmethod
    def remover_item(item: ItemFolha):
        """Remove um item de um evento de pagamento"""
        evento = item.evento_pagamento
        folha = item.folha_pagamento
        funcionario = item.funcionario
        
        if evento.status != 'R':
            raise ValidationError('Apenas eventos em rascunho podem ser editados')
        
        item.delete()
        
        # Atualiza o valor total do evento
        evento.calcular_valor_total()
        
        # Atualiza o resumo do funcionário
        FolhaService._criar_resumo_funcionario(folha, funcionario)


class AdiantamentoService:
    """Service para gerenciamento de adiantamentos"""
    
    @staticmethod
    def lancar_adiantamento_massivo(filtros: dict, valor: Decimal = None, 
                                    percentual: Decimal = None, 
                                    data_adiantamento: date = None) -> int:
        """
        Lança adiantamentos em massa com base em filtros
        
        Args:
            filtros: Dict com filtros (setor_id, funcao_id, status)
            valor: Valor fixo do adiantamento (se None, usa percentual)
            percentual: Percentual do salário base (se None, usa valor)
            data_adiantamento: Data do adiantamento (default: hoje)
            
        Returns:
            int: Quantidade de adiantamentos criados
        """
        if not valor and not percentual:
            raise ValidationError('Informe um valor fixo ou percentual')
        
        if not data_adiantamento:
            data_adiantamento = date.today()
        
        # Busca funcionários com base nos filtros
        funcionarios = Funcionario.objects.filter(**filtros)
        
        count = 0
        with transaction.atomic():
            for funcionario in funcionarios:
                # Calcula o valor do adiantamento
                if valor:
                    valor_adiantamento = valor
                else:
                    valor_adiantamento = (funcionario.salario_base * percentual) / Decimal('100')
                
                Adiantamento.objects.create(
                    funcionario=funcionario,
                    data_adiantamento=data_adiantamento,
                    valor=valor_adiantamento,
                    status='P',
                    observacoes='Adiantamento lançado em massa'
                )
                count += 1
        
        return count


# Import necessário para Q objects
from django.db import models
