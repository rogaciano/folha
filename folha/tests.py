"""
Testes para o app Folha de Pagamento
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal

from core.models import Setor, Funcao, TipoContrato, ProventoDesconto
from funcionarios.models import Funcionario, Contrato, LancamentoFixo, Adiantamento
from folha.models import FolhaPagamento, ItemFolha, ResumoFolhaFuncionario
from folha.services import FolhaService, AdiantamentoService


class FolhaPagamentoModelTest(TestCase):
    """Testes para o modelo FolhaPagamento"""

    def test_folha_creation(self):
        """Testa criação de folha"""
        folha = FolhaPagamento.objects.create(
            mes=1,
            ano=2024
        )
        self.assertEqual(folha.mes, 1)
        self.assertEqual(folha.ano, 2024)
        self.assertEqual(folha.status, 'R')

    def test_folha_periodo_referencia(self):
        """Testa formatação do período de referência"""
        folha = FolhaPagamento.objects.create(mes=3, ano=2024)
        self.assertEqual(folha.periodo_referencia, '03/2024')

    def test_folha_mes_invalido(self):
        """Testa validação de mês inválido"""
        folha = FolhaPagamento(mes=13, ano=2024)
        with self.assertRaises(ValidationError):
            folha.save()

    def test_folha_duplicada(self):
        """Testa que não pode haver folhas duplicadas para o mesmo período"""
        FolhaPagamento.objects.create(mes=1, ano=2024)
        folha_duplicada = FolhaPagamento(mes=1, ano=2024)
        with self.assertRaises(ValidationError):
            folha_duplicada.save()

    def test_fechar_folha(self):
        """Testa fechamento de folha"""
        folha = FolhaPagamento.objects.create(mes=1, ano=2024)
        folha.fechar_folha()
        self.assertEqual(folha.status, 'F')
        self.assertIsNotNone(folha.data_fechamento)

    def test_reabrir_folha(self):
        """Testa reabertura de folha"""
        folha = FolhaPagamento.objects.create(mes=1, ano=2024)
        folha.fechar_folha()
        folha.reabrir_folha()
        self.assertEqual(folha.status, 'R')
        self.assertIsNone(folha.data_fechamento)


class FolhaServiceTest(TestCase):
    """Testes para o FolhaService"""

    def setUp(self):
        # Cria dados básicos
        self.setor = Setor.objects.create(nome='TI')
        self.funcao = Funcao.objects.create(nome='Desenvolvedor')
        self.tipo_contrato = TipoContrato.objects.create(nome='CLT')
        
        self.funcionario = Funcionario.objects.create(
            nome_completo='João Silva',
            cpf='12345678901',
            data_admissao=date(2023, 1, 1),
            funcao=self.funcao,
            setor=self.setor,
            salario_base=Decimal('5000.00')
        )
        
        self.contrato = Contrato.objects.create(
            funcionario=self.funcionario,
            tipo_contrato=self.tipo_contrato,
            data_inicio=date(2023, 1, 1),
            carga_horaria=40
        )
        
        # Cria provento de salário
        ProventoDesconto.objects.create(
            nome='Salário Base',
            codigo_referencia='SALARIO',
            tipo='P',
            impacto='F'
        )

    def test_gerar_folha(self):
        """Testa geração de folha de pagamento"""
        folha = FolhaService.gerar_folha(mes=1, ano=2024)
        
        self.assertIsNotNone(folha)
        self.assertEqual(folha.mes, 1)
        self.assertEqual(folha.ano, 2024)
        
        # Verifica se o salário foi lançado
        itens = ItemFolha.objects.filter(folha_pagamento=folha)
        self.assertTrue(itens.exists())
        
        # Verifica se o contrato está vinculado
        self.assertIn(self.contrato, folha.contratos_ativos.all())

    def test_gerar_folha_com_lancamento_fixo(self):
        """Testa geração de folha com lançamento fixo"""
        # Cria um provento
        provento = ProventoDesconto.objects.create(
            nome='Vale Transporte',
            codigo_referencia='VT',
            tipo='P',
            impacto='F'
        )
        
        # Cria lançamento fixo
        LancamentoFixo.objects.create(
            funcionario=self.funcionario,
            provento_desconto=provento,
            valor=Decimal('200.00'),
            data_inicio=date(2023, 1, 1)
        )
        
        folha = FolhaService.gerar_folha(mes=1, ano=2024)
        
        # Verifica se o lançamento fixo foi incluído
        itens_vt = ItemFolha.objects.filter(
            folha_pagamento=folha,
            provento_desconto=provento
        )
        self.assertTrue(itens_vt.exists())
        self.assertEqual(itens_vt.first().valor_lancado, Decimal('200.00'))

    def test_gerar_folha_com_adiantamento(self):
        """Testa geração de folha com adiantamento pendente"""
        # Cria adiantamento
        adiantamento = Adiantamento.objects.create(
            funcionario=self.funcionario,
            data_adiantamento=date.today(),
            valor=Decimal('1000.00'),
            status='P'
        )
        
        folha = FolhaService.gerar_folha(mes=1, ano=2024)
        
        # Verifica se o adiantamento foi descontado
        adiantamento.refresh_from_db()
        self.assertEqual(adiantamento.status, 'D')

    def test_adicionar_item_manual(self):
        """Testa adição de item manual à folha"""
        folha = FolhaPagamento.objects.create(mes=1, ano=2024)
        
        provento = ProventoDesconto.objects.create(
            nome='Hora Extra',
            codigo_referencia='HE',
            tipo='P',
            impacto='F'
        )
        
        item = FolhaService.adicionar_item_manual(
            folha=folha,
            funcionario=self.funcionario,
            provento_desconto=provento,
            valor=Decimal('500.00'),
            justificativa='Horas extras do mês'
        )
        
        self.assertIsNotNone(item)
        self.assertEqual(item.valor_lancado, Decimal('500.00'))


class AdiantamentoServiceTest(TestCase):
    """Testes para o AdiantamentoService"""

    def setUp(self):
        setor = Setor.objects.create(nome='TI')
        funcao = Funcao.objects.create(nome='Desenvolvedor')
        
        self.funcionario1 = Funcionario.objects.create(
            nome_completo='João Silva',
            cpf='12345678901',
            data_admissao=date(2023, 1, 1),
            funcao=funcao,
            setor=setor,
            salario_base=Decimal('5000.00')
        )
        
        self.funcionario2 = Funcionario.objects.create(
            nome_completo='Maria Santos',
            cpf='98765432100',
            data_admissao=date(2023, 1, 1),
            funcao=funcao,
            setor=setor,
            salario_base=Decimal('4000.00')
        )

    def test_adiantamento_massivo_valor_fixo(self):
        """Testa lançamento de adiantamento massivo com valor fixo"""
        count = AdiantamentoService.lancar_adiantamento_massivo(
            filtros={'status': 'A'},
            valor=Decimal('1000.00'),
            data_adiantamento=date.today()
        )
        
        self.assertEqual(count, 2)
        
        adiantamentos = Adiantamento.objects.filter(status='P')
        self.assertEqual(adiantamentos.count(), 2)

    def test_adiantamento_massivo_percentual(self):
        """Testa lançamento de adiantamento massivo com percentual"""
        count = AdiantamentoService.lancar_adiantamento_massivo(
            filtros={'status': 'A'},
            percentual=Decimal('20.00'),
            data_adiantamento=date.today()
        )
        
        self.assertEqual(count, 2)
        
        # Verifica valores calculados
        adiantamento1 = Adiantamento.objects.get(funcionario=self.funcionario1)
        self.assertEqual(adiantamento1.valor, Decimal('1000.00'))  # 20% de 5000
        
        adiantamento2 = Adiantamento.objects.get(funcionario=self.funcionario2)
        self.assertEqual(adiantamento2.valor, Decimal('800.00'))  # 20% de 4000
