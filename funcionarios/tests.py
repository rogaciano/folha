"""
Testes para o app Funcionários
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

from core.models import Setor, Funcao, TipoContrato, ProventoDesconto
from funcionarios.models import Funcionario, Contrato, LancamentoFixo, Adiantamento


class FuncionarioModelTest(TestCase):
    """Testes para o modelo Funcionario"""

    def setUp(self):
        self.setor = Setor.objects.create(nome='TI')
        self.funcao = Funcao.objects.create(nome='Desenvolvedor')
        
        self.funcionario = Funcionario.objects.create(
            nome_completo='João Silva',
            cpf='12345678901',
            data_admissao=date(2023, 1, 1),
            funcao=self.funcao,
            setor=self.setor,
            salario_base=5000.00
        )

    def test_funcionario_creation(self):
        """Testa criação de funcionário"""
        self.assertEqual(self.funcionario.nome_completo, 'João Silva')
        self.assertEqual(self.funcionario.status, 'A')

    def test_cpf_invalido(self):
        """Testa validação de CPF inválido"""
        funcionario = Funcionario(
            nome_completo='Maria Santos',
            cpf='00000000000',
            data_admissao=date.today(),
            funcao=self.funcao,
            setor=self.setor,
            salario_base=3000.00
        )
        with self.assertRaises(ValidationError):
            funcionario.save()

    def test_tempo_empresa(self):
        """Testa cálculo de tempo de empresa"""
        tempo = self.funcionario.tempo_empresa
        self.assertIsNotNone(tempo)
        self.assertIn('anos', tempo)


class ContratoModelTest(TestCase):
    """Testes para o modelo Contrato"""

    def setUp(self):
        setor = Setor.objects.create(nome='TI')
        funcao = Funcao.objects.create(nome='Desenvolvedor')
        self.tipo_contrato = TipoContrato.objects.create(nome='CLT')
        
        self.funcionario = Funcionario.objects.create(
            nome_completo='João Silva',
            cpf='12345678901',
            data_admissao=date(2023, 1, 1),
            funcao=funcao,
            setor=setor,
            salario_base=5000.00
        )

    def test_contrato_creation(self):
        """Testa criação de contrato"""
        contrato = Contrato.objects.create(
            funcionario=self.funcionario,
            tipo_contrato=self.tipo_contrato,
            data_inicio=date(2023, 1, 1),
            carga_horaria=40
        )
        self.assertEqual(contrato.funcionario, self.funcionario)
        self.assertTrue(contrato.esta_ativo)

    def test_contrato_data_fim_invalida(self):
        """Testa validação de data fim anterior à data início"""
        contrato = Contrato(
            funcionario=self.funcionario,
            tipo_contrato=self.tipo_contrato,
            data_inicio=date(2023, 1, 1),
            data_fim=date(2022, 12, 31),
            carga_horaria=40
        )
        with self.assertRaises(ValidationError):
            contrato.save()


class LancamentoFixoModelTest(TestCase):
    """Testes para o modelo LancamentoFixo"""

    def setUp(self):
        setor = Setor.objects.create(nome='TI')
        funcao = Funcao.objects.create(nome='Desenvolvedor')
        
        self.funcionario = Funcionario.objects.create(
            nome_completo='João Silva',
            cpf='12345678901',
            data_admissao=date(2023, 1, 1),
            funcao=funcao,
            setor=setor,
            salario_base=5000.00
        )
        
        self.provento = ProventoDesconto.objects.create(
            nome='Vale Transporte',
            codigo_referencia='VT',
            tipo='P',
            impacto='F'
        )

    def test_lancamento_fixo_valor(self):
        """Testa lançamento fixo com valor"""
        lancamento = LancamentoFixo.objects.create(
            funcionario=self.funcionario,
            provento_desconto=self.provento,
            valor=Decimal('200.00'),
            data_inicio=date.today()
        )
        self.assertEqual(lancamento.valor, Decimal('200.00'))
        self.assertTrue(lancamento.esta_ativo)

    def test_lancamento_fixo_percentual(self):
        """Testa lançamento fixo com percentual"""
        provento_percentual = ProventoDesconto.objects.create(
            nome='Bonificação',
            codigo_referencia='BONUS',
            tipo='P',
            impacto='P'
        )
        lancamento = LancamentoFixo.objects.create(
            funcionario=self.funcionario,
            provento_desconto=provento_percentual,
            percentual=Decimal('10.00'),
            data_inicio=date.today()
        )
        self.assertEqual(lancamento.percentual, Decimal('10.00'))


class AdiantamentoModelTest(TestCase):
    """Testes para o modelo Adiantamento"""

    def setUp(self):
        setor = Setor.objects.create(nome='TI')
        funcao = Funcao.objects.create(nome='Desenvolvedor')
        
        self.funcionario = Funcionario.objects.create(
            nome_completo='João Silva',
            cpf='12345678901',
            data_admissao=date(2023, 1, 1),
            funcao=funcao,
            setor=setor,
            salario_base=5000.00
        )

    def test_adiantamento_creation(self):
        """Testa criação de adiantamento"""
        adiantamento = Adiantamento.objects.create(
            funcionario=self.funcionario,
            data_adiantamento=date.today(),
            valor=Decimal('1000.00')
        )
        self.assertEqual(adiantamento.status, 'P')
        self.assertEqual(adiantamento.valor, Decimal('1000.00'))

    def test_adiantamento_str(self):
        """Testa representação string"""
        adiantamento = Adiantamento.objects.create(
            funcionario=self.funcionario,
            data_adiantamento=date.today(),
            valor=Decimal('500.00')
        )
        self.assertIn('João Silva', str(adiantamento))
        self.assertIn('500', str(adiantamento))
