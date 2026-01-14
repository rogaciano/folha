"""
Management command para verificar lançamentos fixos
"""
from django.core.management.base import BaseCommand
from funcionarios.models import Funcionario, LancamentoFixo
from core.models import LancamentoFixoGeral
from folha.models import FolhaPagamento, ItemFolha


class Command(BaseCommand):
    help = 'Verifica lançamentos fixos gerais e por funcionário'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write("DIAGNÓSTICO - LANÇAMENTOS FIXOS")
        self.stdout.write("="*80)

        # 1. Lançamentos Fixos Gerais
        self.stdout.write("\n1. LANÇAMENTOS FIXOS GERAIS")
        self.stdout.write("-"*80)
        lancs_gerais = LancamentoFixoGeral.objects.filter(ativo=True)
        self.stdout.write(f"Total: {lancs_gerais.count()}")
        for lanc in lancs_gerais:
            valor_str = f"R$ {lanc.valor}" if lanc.valor else f"{lanc.percentual}%"
            self.stdout.write(f"  • {lanc.provento_desconto.nome}: {valor_str}")
            self.stdout.write(f"    Período: {lanc.data_inicio} até {lanc.data_fim or 'permanente'}")

        # 2. Lançamentos Fixos por Funcionário
        self.stdout.write("\n2. LANÇAMENTOS FIXOS POR FUNCIONÁRIO")
        self.stdout.write("-"*80)
        funcionarios = Funcionario.objects.all()
        for func in funcionarios:
            lancs = func.lancamentos_fixos.all()
            contratos = func.contratos.count()
            
            self.stdout.write(f"\n{func.nome_completo}")
            self.stdout.write(f"  Contratos: {contratos}")
            self.stdout.write(f"  Lançamentos fixos: {lancs.count()}")
            
            if lancs.exists():
                for lanc in lancs:
                    valor_str = f"R$ {lanc.valor}" if lanc.valor else f"{lanc.percentual}%"
                    data_fim_str = lanc.data_fim.strftime('%d/%m/%Y') if lanc.data_fim else 'permanente'
                    self.stdout.write(f"    - {lanc.provento_desconto.nome}: {valor_str}")
                    self.stdout.write(f"      ({lanc.data_inicio.strftime('%d/%m/%Y')} até {data_fim_str})")

        # 3. Última Folha Gerada
        self.stdout.write("\n3. ÚLTIMA FOLHA DE PAGAMENTO")
        self.stdout.write("-"*80)
        ultima_folha = FolhaPagamento.objects.order_by('-ano', '-mes').first()
        if ultima_folha:
            self.stdout.write(f"Folha: {ultima_folha.periodo_referencia}")
            self.stdout.write(f"Status: {ultima_folha.get_status_display()}")
            
            # Verifica itens da folha
            itens = ItemFolha.objects.filter(folha_pagamento=ultima_folha).select_related(
                'funcionario', 'provento_desconto'
            )
            
            self.stdout.write(f"\nItens na folha: {itens.count()}")
            
            # Agrupa por funcionário
            funcionarios_na_folha = {}
            for item in itens:
                func_nome = item.funcionario.nome_completo
                if func_nome not in funcionarios_na_folha:
                    funcionarios_na_folha[func_nome] = []
                funcionarios_na_folha[func_nome].append(item)
            
            self.stdout.write(f"Funcionários processados: {len(funcionarios_na_folha)}")
            
            for func_nome, itens_func in funcionarios_na_folha.items():
                self.stdout.write(f"\n  {func_nome}:")
                for item in itens_func:
                    self.stdout.write(f"    • {item.provento_desconto.nome}: R$ {item.valor_lancado}")
                    if item.justificativa:
                        self.stdout.write(f"      ({item.justificativa})")
        else:
            self.stdout.write("Nenhuma folha de pagamento cadastrada")

        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("DIAGNÓSTICO COMPLETO"))
        self.stdout.write("="*80 + "\n")
