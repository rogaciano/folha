"""
Testes para o app Core
"""
from django.test import TestCase
from core.models import Setor, Funcao, TipoContrato, ProventoDesconto


class SetorModelTest(TestCase):
    """Testes para o modelo Setor"""

    def setUp(self):
        self.setor = Setor.objects.create(
            nome='Tecnologia',
            descricao='Setor de TI'
        )

    def test_setor_creation(self):
        """Testa criação de setor"""
        self.assertEqual(self.setor.nome, 'Tecnologia')
        self.assertTrue(self.setor.ativo)

    def test_setor_str(self):
        """Testa representação string"""
        self.assertEqual(str(self.setor), 'Tecnologia')


class FuncaoModelTest(TestCase):
    """Testes para o modelo Funcao"""

    def setUp(self):
        self.funcao = Funcao.objects.create(
            nome='Desenvolvedor',
            nivel_salarial_referencia=5000.00
        )

    def test_funcao_creation(self):
        """Testa criação de função"""
        self.assertEqual(self.funcao.nome, 'Desenvolvedor')
        self.assertEqual(self.funcao.nivel_salarial_referencia, 5000.00)

    def test_funcao_str(self):
        """Testa representação string"""
        self.assertEqual(str(self.funcao), 'Desenvolvedor')


class ProventoDescontoModelTest(TestCase):
    """Testes para o modelo ProventoDesconto"""

    def setUp(self):
        self.provento = ProventoDesconto.objects.create(
            nome='Salário Base',
            codigo_referencia='SALARIO',
            tipo='P',
            impacto='F'
        )
        self.desconto = ProventoDesconto.objects.create(
            nome='INSS',
            codigo_referencia='INSS',
            tipo='D',
            impacto='P'
        )

    def test_provento_creation(self):
        """Testa criação de provento"""
        self.assertEqual(self.provento.nome, 'Salário Base')
        self.assertEqual(self.provento.tipo, 'P')
        self.assertEqual(self.provento.impacto, 'F')

    def test_desconto_creation(self):
        """Testa criação de desconto"""
        self.assertEqual(self.desconto.nome, 'INSS')
        self.assertEqual(self.desconto.tipo, 'D')
        self.assertEqual(self.desconto.impacto, 'P')

    def test_provento_str(self):
        """Testa representação string"""
        self.assertIn('Provento', str(self.provento))
        self.assertIn('Salário Base', str(self.provento))
